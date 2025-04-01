"""
Integration tests for the API layer.
"""
import pytest
import json
from fastapi import status


@pytest.mark.asyncio
async def test_get_system_status(api_client, auth_headers):
    """Test getting the system status."""
    response = await api_client.get("/status", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "components" in data
    assert "uptime" in data
    
    # Check required components
    components = data["components"]
    assert "api" in components
    assert "telephony" in components
    assert "llm" in components
    assert "voice" in components


@pytest.mark.asyncio
async def test_call_lifecycle(api_client, auth_headers, test_call_data):
    """Test the entire call lifecycle."""
    # Create a call
    response = await api_client.post(
        "/calls",
        headers=auth_headers,
        json=test_call_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    call_id = response.json().get("call_id")
    assert call_id == test_call_data["call_id"]
    
    # Get the call
    response = await api_client.get(
        f"/calls/{call_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    call_data = response.json()
    assert call_data["call_id"] == call_id
    assert call_data["caller_name"] == test_call_data["caller_name"]
    
    # Update the call
    updated_data = {"status": "transferred", "notes": "Updated notes"}
    response = await api_client.put(
        f"/calls/{call_id}",
        headers=auth_headers,
        json=updated_data
    )
    assert response.status_code == status.HTTP_200_OK
    
    call_data = response.json()
    assert call_data["status"] == "transferred"
    assert call_data["notes"] == "Updated notes"
    
    # Delete the call
    response = await api_client.delete(
        f"/calls/{call_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deletion
    response = await api_client.get(
        f"/calls/{call_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_message_handling(api_client, auth_headers, test_message_data):
    """Test message creation and retrieval."""
    # Create a message
    response = await api_client.post(
        "/messages",
        headers=auth_headers,
        json=test_message_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    message_id = response.json().get("message_id")
    assert message_id == test_message_data["message_id"]
    
    # Get message
    response = await api_client.get(
        f"/messages/{message_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    message_data = response.json()
    assert message_data["message_id"] == message_id
    assert message_data["subject"] == test_message_data["subject"]
    
    # Get all messages
    response = await api_client.get(
        "/messages",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "messages" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # Test filtering
    response = await api_client.get(
        "/messages?urgency=normal",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    for message in data["messages"]:
        assert message["urgency"] == "normal"


@pytest.mark.asyncio
async def test_appointment_management(api_client, auth_headers, test_appointment_data):
    """Test appointment creation and management."""
    # Create an appointment
    response = await api_client.post(
        "/appointments",
        headers=auth_headers,
        json=test_appointment_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    appointment_id = response.json().get("appointment_id")
    assert appointment_id == test_appointment_data["appointment_id"]
    
    # Get appointment
    response = await api_client.get(
        f"/appointments/{appointment_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    appointment_data = response.json()
    assert appointment_data["appointment_id"] == appointment_id
    assert appointment_data["title"] == test_appointment_data["title"]
    
    # Update appointment
    updated_data = {"status": "completed", "notes": "Appointment completed"}
    response = await api_client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json=updated_data
    )
    assert response.status_code == status.HTTP_200_OK
    
    appointment_data = response.json()
    assert appointment_data["status"] == "completed"
    assert appointment_data["notes"] == "Appointment completed"
    
    # Get appointments by date
    response = await api_client.get(
        f"/appointments?date={test_appointment_data['date']}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "appointments" in data
    assert len(data["appointments"]) >= 1


@pytest.mark.asyncio
async def test_action_execution(api_client, auth_headers):
    """Test action execution."""
    # Execute a schedule appointment action
    action_data = {
        "action_type": "schedule_appointment",
        "params": {
            "date": "2023-02-01",
            "time": "10:00",
            "duration": 60,
            "contact": "Test Contact",
            "purpose": "Follow-up"
        }
    }
    
    response = await api_client.post(
        "/actions",
        headers=auth_headers,
        json=action_data
    )
    assert response.status_code == status.HTTP_200_OK
    
    result = response.json()
    assert "success" in result
    assert result["success"] is True
    assert "action_id" in result
    
    # Execute a send message action
    action_data = {
        "action_type": "send_message",
        "params": {
            "recipient": "test@example.com",
            "subject": "Test Message",
            "content": "This is a test message.",
            "urgency": "high"
        }
    }
    
    response = await api_client.post(
        "/actions",
        headers=auth_headers,
        json=action_data
    )
    assert response.status_code == status.HTTP_200_OK
    
    result = response.json()
    assert "success" in result
    assert "message_id" in result