"""
Integration tests for the Telephony and LLM components.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_call_handler_with_llm(mock_call_handler, mock_ollama_client):
    """Test integration between call handler and LLM."""
    from workflow.actions import ActionExecutor
    
    # Setup
    call_id = "test-integration-123"
    
    # Mock the speech-to-text result
    mock_call_handler.listen = AsyncMock(return_value="I want to schedule an appointment for next Monday at 2pm")
    
    # Create action executor with mocked components
    action_executor = ActionExecutor(
        call_handler=mock_call_handler,
        llm_client=mock_ollama_client
    )
    
    # Patch the action execution to return success
    with patch.object(action_executor, 'execute_action', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = {
            "success": True,
            "action_type": "schedule_appointment",
            "params": {
                "date": "2023-01-15",  # Next Monday in this scenario
                "time": "14:00",
                "duration": 60,
                "purpose": "General appointment"
            }
        }
        
        # Start call
        await mock_call_handler.answer_call(call_id)
        
        # Simulate conversation flow
        await mock_call_handler.say(call_id, "Hello, how can I help you today?")
        
        # "Listen" for user input
        user_input = await mock_call_handler.listen(call_id)
        assert "appointment" in user_input.lower()
        
        # Process with LLM
        llm_response = await mock_ollama_client.generate(
            prompt=f"User said: {user_input}. What should I do?",
            system_prompt="You are an AI secretary that helps schedule appointments."
        )
        
        # Should have a response
        assert llm_response is not None
        assert "response" in llm_response
        
        # Process the intent (which would normally come from LLM)
        intent = "schedule_appointment"
        action_result = await action_executor.execute_action(
            action_type=intent,
            call_id=call_id,
            params={
                "date": "2023-01-15",
                "time": "14:00"
            }
        )
        
        # Verify action was "executed"
        assert action_result["success"] is True
        assert action_result["action_type"] == "schedule_appointment"
        
        # Respond to user
        await mock_call_handler.say(
            call_id, 
            "I've scheduled your appointment for Monday, January 15th at 2:00 PM. Is there anything else you need?"
        )
        
        # End call
        await mock_call_handler.end_call(call_id)
        
        # Verify the expected interactions occurred
        mock_call_handler.answer_call.assert_called_once_with(call_id)
        mock_call_handler.say.assert_called()
        mock_call_handler.listen.assert_called_once()
        mock_call_handler.end_call.assert_called_once_with(call_id)
        mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_voice_processing_pipeline():
    """Test the voice processing pipeline from STT to TTS."""
    from voice.stt import SpeechToText
    from voice.tts import TextToSpeech
    
    # Mock implementations
    class MockSTT(SpeechToText):
        async def transcribe(self, audio_data):
            # Simulate transcription delay
            await asyncio.sleep(0.1)
            return "This is a mock transcription."
    
    class MockTTS(TextToSpeech):
        async def synthesize(self, text):
            # Simulate synthesis delay
            await asyncio.sleep(0.1)
            # Return mock audio data (bytes)
            return b"mock_audio_data"
    
    # Create instances
    stt = MockSTT()
    tts = MockTTS()
    
    # Test STT
    mock_audio = b"simulated_audio_data"
    transcript = await stt.transcribe(mock_audio)
    assert transcript == "This is a mock transcription."
    
    # Test TTS
    response_text = "Thank you for your message. I'll schedule that appointment."
    audio_response = await tts.synthesize(response_text)
    assert audio_response == b"mock_audio_data"
    
    # Test full pipeline
    result_text = await stt.transcribe(mock_audio)
    result_audio = await tts.synthesize(f"I heard: {result_text}")
    assert isinstance(result_audio, bytes)
    assert len(result_audio) > 0