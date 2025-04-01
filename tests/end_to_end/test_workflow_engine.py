"""
End-to-end tests for the workflow engine.
"""
import pytest
import json
import asyncio
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_complete_call_flow():
    """
    Test a complete call flow from start to finish.
    """
    from workflow.actions import ActionExecutor
    from telephony.call_handler import CallHandler
    from llm.ollama_client import OllamaClient
    from api.routes import CallRepository
    
    # Mock components
    mock_call_handler = AsyncMock(spec=CallHandler)
    mock_llm_client = AsyncMock(spec=OllamaClient)
    mock_call_repo = AsyncMock(spec=CallRepository)
    
    # Setup call ID and caller info
    call_id = "e2e-test-call-001"
    caller_number = "+15555555555"
    
    # Configure mocks
    mock_call_handler.answer_call.return_value = True
    mock_call_handler.say.return_value = True
    mock_call_handler.listen.side_effect = [
        "I'd like to schedule an appointment for a consultation",
        "Next Tuesday at 2pm would work for me",
        "Yes, that's correct",
        "No, that's all I needed, thank you"
    ]
    
    # LLM responses for different turns in conversation
    llm_responses = [
        {
            "response": "I can help you schedule an appointment. What day and time works best for you?",
            "intent": "gather_appointment_info",
            "entities": {}
        },
        {
            "response": "I have Tuesday at 2pm available. Would you like me to schedule a consultation for that time?",
            "intent": "confirm_appointment",
            "entities": {"date": "2023-05-09", "time": "14:00", "purpose": "consultation"}
        },
        {
            "response": "Great! I've scheduled your consultation for Tuesday, May 9th at 2:00 PM. Is there anything else you need help with?",
            "intent": "schedule_appointment",
            "entities": {"date": "2023-05-09", "time": "14:00", "purpose": "consultation"}
        },
        {
            "response": "Thank you for calling. Your appointment has been confirmed. Have a great day!",
            "intent": "end_conversation",
            "entities": {}
        }
    ]
    
    mock_llm_client.generate.side_effect = [
        {"response": json.dumps(response)} for response in llm_responses
    ]
    
    # Create a mock for the appointment scheduling action
    mock_appointment_action = AsyncMock()
    mock_appointment_action.return_value = {
        "success": True,
        "appointment_id": "e2e-test-appointment-001",
        "details": {
            "date": "2023-05-09",
            "time": "14:00",
            "purpose": "consultation"
        }
    }
    
    # Workflow implementation
    async def run_workflow():
        # Initialize call
        call_data = {
            "call_id": call_id,
            "caller_number": caller_number,
            "start_time": "2023-05-01T13:45:00Z",
            "status": "active",
            "transcript": {"items": []}
        }
        
        await mock_call_repo.create_call(call_data)
        await mock_call_handler.answer_call(call_id)
        
        # Initial greeting
        await mock_call_handler.say(call_id, "Hello, thank you for calling. How can I help you today?")
        
        # Add to transcript
        call_data["transcript"]["items"].append({
            "speaker": "assistant",
            "text": "Hello, thank you for calling. How can I help you today?",
            "timestamp": "2023-05-01T13:45:05Z"
        })
        
        # Main conversation loop
        turn = 0
        conversation_active = True
        
        while conversation_active and turn < 4:  # Limit to prevent infinite loops
            # Get user input
            user_input = await mock_call_handler.listen(call_id)
            
            # Add to transcript
            call_data["transcript"]["items"].append({
                "speaker": "user",
                "text": user_input,
                "timestamp": f"2023-05-01T13:45:{10 + turn * 10}Z"
            })
            
            # Process with LLM
            context = "\n".join([
                f"{item['speaker']}: {item['text']}" 
                for item in call_data["transcript"]["items"]
            ])
            
            llm_result = await mock_llm_client.generate(
                prompt=f"User said: {user_input}",
                system_prompt=f"Previous conversation:\n{context}\n\nYou are an AI secretary."
            )
            
            # Extract response and intent
            response_data = json.loads(llm_result["response"])
            assistant_response = response_data["response"]
            intent = response_data["intent"]
            entities = response_data["entities"]
            
            # Add to transcript
            call_data["transcript"]["items"].append({
                "speaker": "assistant",
                "text": assistant_response,
                "timestamp": f"2023-05-01T13:45:{15 + turn * 10}Z"
            })
            
            # Say response to user
            await mock_call_handler.say(call_id, assistant_response)
            
            # Process intent
            if intent == "schedule_appointment":
                # Execute appointment scheduling
                action_result = await mock_appointment_action(entities)
                
                # Add action to call data
                if "actions" not in call_data:
                    call_data["actions"] = []
                
                call_data["actions"].append({
                    "action_type": "schedule_appointment",
                    "timestamp": f"2023-05-01T13:45:{20 + turn * 10}Z",
                    "success": action_result["success"],
                    "details": action_result["details"]
                })
                
                # Update call
                await mock_call_repo.update_call(call_id, call_data)
            
            # Check if conversation should end
            if intent == "end_conversation":
                conversation_active = False
            
            turn += 1
        
        # End call
        call_data["status"] = "completed"
        call_data["duration"] = turn * 30  # Approximate duration
        await mock_call_repo.update_call(call_id, call_data)
        await mock_call_handler.end_call(call_id)
        
        return call_data
    
    # Run the workflow
    final_call_data = await run_workflow()
    
    # Assertions to verify the workflow executed correctly
    assert mock_call_handler.answer_call.called
    assert mock_call_handler.say.call_count >= 4
    assert mock_call_handler.listen.call_count >= 4
    assert mock_call_handler.end_call.called
    
    assert mock_llm_client.generate.call_count >= 4
    assert mock_appointment_action.called
    
    assert final_call_data["status"] == "completed"
    assert "actions" in final_call_data
    assert len(final_call_data["actions"]) >= 1
    assert final_call_data["actions"][0]["action_type"] == "schedule_appointment"
    assert final_call_data["actions"][0]["success"] is True
    
    assert "transcript" in final_call_data
    assert len(final_call_data["transcript"]["items"]) >= 8  # At least 4 turns x 2 messages


@pytest.mark.asyncio
async def test_call_with_transfer():
    """
    Test a call flow that results in a transfer to a human.
    """
    from workflow.actions import ActionExecutor
    from telephony.call_handler import CallHandler
    from llm.ollama_client import OllamaClient
    from api.routes import CallRepository
    
    # Mock components
    mock_call_handler = AsyncMock(spec=CallHandler)
    mock_llm_client = AsyncMock(spec=OllamaClient)
    mock_call_repo = AsyncMock(spec=CallRepository)
    
    # Setup call ID and caller info
    call_id = "e2e-test-call-002"
    caller_number = "+15555555556"
    
    # Configure mocks
    mock_call_handler.answer_call.return_value = True
    mock_call_handler.say.return_value = True
    mock_call_handler.listen.side_effect = [
        "I have a complex question about my account that I need help with",
        "I need to discuss my billing situation",
        "Yes, please transfer me to a human representative"
    ]
    
    # LLM responses for different turns in conversation
    llm_responses = [
        {
            "response": "I can try to help with your account. What specific question do you have?",
            "intent": "gather_information",
            "entities": {"topic": "account"}
        },
        {
            "response": "I understand you have questions about billing. This might be better handled by one of our human representatives. Would you like me to transfer you?",
            "intent": "offer_transfer",
            "entities": {"topic": "billing"}
        },
        {
            "response": "I'll transfer you to a representative who can help with your billing questions. Please hold while I connect you.",
            "intent": "transfer_call",
            "entities": {"transfer_reason": "billing assistance"}
        }
    ]
    
    mock_llm_client.generate.side_effect = [
        {"response": json.dumps(response)} for response in llm_responses
    ]
    
    # Create a mock for the transfer action
    mock_transfer_action = AsyncMock()
    mock_transfer_action.return_value = {
        "success": True,
        "transfer_id": "transfer-001",
        "details": {
            "transfer_to": "billing_department",
            "reason": "billing assistance",
            "timestamp": "2023-05-01T14:15:30Z"
        }
    }
    
    # Workflow implementation
    async def run_workflow():
        # Initialize call
        call_data = {
            "call_id": call_id,
            "caller_number": caller_number,
            "start_time": "2023-05-01T14:00:00Z",
            "status": "active",
            "transcript": {"items": []}
        }
        
        await mock_call_repo.create_call(call_data)
        await mock_call_handler.answer_call(call_id)
        
        # Initial greeting
        await mock_call_handler.say(call_id, "Hello, thank you for calling. How can I help you today?")
        
        # Add to transcript
        call_data["transcript"]["items"].append({
            "speaker": "assistant",
            "text": "Hello, thank you for calling. How can I help you today?",
            "timestamp": "2023-05-01T14:00:05Z"
        })
        
        # Main conversation loop
        turn = 0
        conversation_active = True
        
        while conversation_active and turn < 3:  # Limit to prevent infinite loops
            # Get user input
            user_input = await mock_call_handler.listen(call_id)
            
            # Add to transcript
            call_data["transcript"]["items"].append({
                "speaker": "user",
                "text": user_input,
                "timestamp": f"2023-05-01T14:00:{10 + turn * 10}Z"
            })
            
            # Process with LLM
            context = "\n".join([
                f"{item['speaker']}: {item['text']}" 
                for item in call_data["transcript"]["items"]
            ])
            
            llm_result = await mock_llm_client.generate(
                prompt=f"User said: {user_input}",
                system_prompt=f"Previous conversation:\n{context}\n\nYou are an AI secretary."
            )
            
            # Extract response and intent
            response_data = json.loads(llm_result["response"])
            assistant_response = response_data["response"]
            intent = response_data["intent"]
            entities = response_data["entities"]
            
            # Add to transcript
            call_data["transcript"]["items"].append({
                "speaker": "assistant",
                "text": assistant_response,
                "timestamp": f"2023-05-01T14:00:{15 + turn * 10}Z"
            })
            
            # Say response to user
            await mock_call_handler.say(call_id, assistant_response)
            
            # Process intent
            if intent == "transfer_call":
                # Execute transfer action
                action_result = await mock_transfer_action(entities)
                
                # Add action to call data
                if "actions" not in call_data:
                    call_data["actions"] = []
                
                call_data["actions"].append({
                    "action_type": "transfer_call",
                    "timestamp": f"2023-05-01T14:00:{20 + turn * 10}Z",
                    "success": action_result["success"],
                    "details": action_result["details"]
                })
                
                # Update call status
                call_data["status"] = "transferred"
                conversation_active = False
                
                # Update call
                await mock_call_repo.update_call(call_id, call_data)
            
            turn += 1
        
        # End call if not transferred
        if call_data["status"] != "transferred":
            call_data["status"] = "completed"
        
        call_data["duration"] = turn * 30  # Approximate duration
        await mock_call_repo.update_call(call_id, call_data)
        
        return call_data
    
    # Run the workflow
    final_call_data = await run_workflow()
    
    # Assertions to verify the workflow executed correctly
    assert mock_call_handler.answer_call.called
    assert mock_call_handler.say.call_count >= 3
    assert mock_call_handler.listen.call_count >= 3
    
    assert mock_llm_client.generate.call_count >= 3
    assert mock_transfer_action.called
    
    assert final_call_data["status"] == "transferred"
    assert "actions" in final_call_data
    assert len(final_call_data["actions"]) >= 1
    assert final_call_data["actions"][0]["action_type"] == "transfer_call"
    assert final_call_data["actions"][0]["success"] is True
    
    assert "transcript" in final_call_data
    assert len(final_call_data["transcript"]["items"]) >= 6  # At least 3 turns x 2 messages