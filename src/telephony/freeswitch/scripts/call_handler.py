"""
FreeSWITCH script to handle incoming calls and bridge to AI secretary.
This script is executed by FreeSWITCH when a call matches the dialplan.
"""
import sys
import os
import time
import json

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

import freeswitch
from src.telephony.call_handler import CallHandler

def handler(session, args):
    """
    Main handler function called by FreeSWITCH.
    
    Args:
        session: The FreeSWITCH session object
        args: Arguments passed from the dialplan
    """
    freeswitch.consoleLog("info", f"AI Call Secretary handling call: {session.getVariable('caller_id_number')}\n")
    
    # Initialize the call handler
    call_id = session.getVariable('uuid')
    caller_number = session.getVariable('caller_id_number')
    caller_name = session.getVariable('caller_id_name') or 'Unknown'
    
    # Create metadata for the call
    call_metadata = {
        'call_id': call_id,
        'caller_number': caller_number,
        'caller_name': caller_name,
        'timestamp': time.time(),
        'direction': 'inbound'
    }
    
    try:
        # Play greeting
        session.answer()
        session.execute("sleep", "500")
        session.execute("playback", "ivr/ivr-hello.wav")
        
        # Start audio stream to our STT system
        session.execute("audio_fork", "start api:127.0.0.1:8021 fork_uuid")
        
        # Create the call handler instance
        handler = CallHandler(call_metadata)
        
        # Process the call
        handler.process_call(session)
        
    except Exception as e:
        freeswitch.consoleLog("err", f"Error in call handler: {str(e)}\n")
        # Play error message
        session.execute("playback", "ivr/ivr-call_cannot_be_completed_as_dialed.wav")
    finally:
        # Cleanup
        session.execute("audio_fork", "stop")
        freeswitch.consoleLog("info", f"Call completed: {call_id}\n")

# This is the entry point that FreeSWITCH calls
def python_handler(session, args):
    handler(session, args)