"""
Call handling logic for incoming calls.
This module processes calls and integrates with STT, LLM, and TTS components.
"""
import time
import logging
import asyncio
import json
import os
from typing import Dict, List, Optional, Any

from src.voice.stt import SpeechToText
from src.voice.tts import TextToSpeech
from src.llm.context import ConversationContext
from src.llm.ollama_client import OllamaClient
from src.workflow.actions import ActionHandler

logger = logging.getLogger(__name__)

class CallHandler:
    """
    Handles incoming calls, manages the conversation, and orchestrates
    the various components (STT, LLM, TTS).
    """
    
    def __init__(self, call_metadata: Dict[str, Any]):
        """
        Initialize the call handler with call metadata.
        
        Args:
            call_metadata: Dictionary containing call information like caller ID, timestamp, etc.
        """
        self.call_metadata = call_metadata
        self.call_id = call_metadata.get('call_id', 'unknown')
        self.caller_number = call_metadata.get('caller_number', 'unknown')
        self.caller_name = call_metadata.get('caller_name', 'Unknown')
        
        # Initialize components
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.llm = OllamaClient()
        self.context = ConversationContext()
        self.action_handler = ActionHandler()
        
        # Call state
        self.conversation_history = []
        self.call_duration = 0
        self.start_time = time.time()
        
        logger.info(f"Call handler initialized for call {self.call_id} from {self.caller_name} <{self.caller_number}>")
    
    def process_call(self, session) -> None:
        """
        Main method to process a call from start to finish.
        
        Args:
            session: The telephony session object
        """
        try:
            # Initialize the conversation context
            self.context.init_conversation(
                caller_name=self.caller_name,
                caller_number=self.caller_number,
                call_id=self.call_id
            )
            
            # Play welcome greeting
            initial_greeting = "Hello, this is your AI assistant. How can I help you today?"
            self._play_response(session, initial_greeting)
            
            # Main conversation loop
            continue_call = True
            while continue_call:
                # Listen for user input
                user_audio = self._capture_audio(session)
                if not user_audio:
                    continue
                
                # Convert speech to text
                user_text = self.stt.transcribe(user_audio)
                if not user_text or user_text.strip() == "":
                    self._play_response(session, "I didn't catch that. Could you please repeat?")
                    continue
                
                logger.info(f"User said: {user_text}")
                self.conversation_history.append({"role": "user", "content": user_text})
                
                # Check for call-ending phrases
                if self._should_end_call(user_text):
                    self._play_response(session, "Thank you for calling. Goodbye!")
                    continue_call = False
                    break
                
                # Process with LLM
                self.context.add_user_message(user_text)
                llm_response = self.llm.generate_response(self.context.get_context())
                
                if not llm_response:
                    self._play_response(session, "I apologize, but I'm having trouble processing your request.")
                    continue
                
                logger.info(f"AI response: {llm_response}")
                self.conversation_history.append({"role": "assistant", "content": llm_response})
                self.context.add_assistant_message(llm_response)
                
                # Check for actions to perform
                actions = self.action_handler.extract_actions(llm_response)
                for action in actions:
                    action_result = self.action_handler.execute_action(action)
                    if action_result:
                        self.context.add_action_result(action, action_result)
                
                # Speak the response
                self._play_response(session, llm_response)
            
        except Exception as e:
            logger.error(f"Error processing call: {str(e)}", exc_info=True)
            self._play_response(session, "I apologize, but there was an error processing your call. Please try again later.")
        finally:
            # Call cleanup
            self.call_duration = time.time() - self.start_time
            self._save_call_record()
            logger.info(f"Call {self.call_id} completed. Duration: {self.call_duration:.2f} seconds")
    
    def _capture_audio(self, session, max_duration: int = 10) -> Optional[bytes]:
        """
        Captures audio from the call session.
        
        Args:
            session: The telephony session object
            max_duration: Maximum recording duration in seconds
            
        Returns:
            Audio data as bytes or None if capture failed
        """
        # Implementation depends on the specific telephony system
        # For FreeSWITCH, we would use record or audio_fork
        try:
            # For now, we'll simulate audio capture
            # In production, this would interact with the session object
            logger.debug(f"Capturing audio for up to {max_duration} seconds")
            
            # This is a placeholder - actual implementation would use FreeSWITCH APIs
            # Example: session.execute("record", f"/tmp/{self.call_id}.wav {max_duration}")
            
            # Simulating recording delay
            time.sleep(2)  # Pretend user spoke for 2 seconds
            
            # In a real implementation, we would return the captured audio bytes
            return b"SIMULATED_AUDIO_DATA"
        except Exception as e:
            logger.error(f"Error capturing audio: {str(e)}", exc_info=True)
            return None
    
    def _play_response(self, session, text: str) -> None:
        """
        Converts text to speech and plays it to the caller.
        
        Args:
            session: The telephony session object
            text: The text to speak
        """
        try:
            # Convert text to speech
            audio_data = self.tts.synthesize(text)
            
            # In a real implementation, we would play this audio through the session
            # Example: session.execute("playback", f"/tmp/{self.call_id}_response.wav")
            
            # This is a placeholder - actual implementation would use FreeSWITCH APIs
            logger.info(f"Playing response: {text}")
            
            # Simulate playback delay based on text length
            play_time = len(text.split()) * 0.3  # Rough estimate: 0.3 seconds per word
            time.sleep(min(play_time, 10))  # Cap at 10 seconds for simulation
            
        except Exception as e:
            logger.error(f"Error playing response: {str(e)}", exc_info=True)
    
    def _should_end_call(self, text: str) -> bool:
        """
        Determines if the call should be ended based on the user's input.
        
        Args:
            text: The user's transcribed speech
            
        Returns:
            True if the call should end, False otherwise
        """
        end_phrases = [
            "goodbye", "bye", "hang up", "end call", "thank you goodbye",
            "that's all", "that is all", "disconnect", "end the call"
        ]
        
        return any(phrase in text.lower() for phrase in end_phrases)
    
    def _save_call_record(self) -> None:
        """
        Saves the call record to storage for later reference.
        """
        call_record = {
            "call_id": self.call_id,
            "caller_number": self.caller_number,
            "caller_name": self.caller_name,
            "start_time": self.start_time,
            "duration": self.call_duration,
            "conversation": self.conversation_history
        }
        
        # In a production system, this would save to a database
        # For now, we'll log it and save to a JSON file in a data directory
        log_dir = os.path.join(os.path.dirname(__file__), "../../data/call_logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"{self.call_id}.json")
        try:
            with open(log_file, 'w') as f:
                json.dump(call_record, f, indent=2)
            logger.info(f"Call record saved to {log_file}")
        except Exception as e:
            logger.error(f"Error saving call record: {str(e)}", exc_info=True)