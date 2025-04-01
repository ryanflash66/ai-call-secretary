"""
Prompt templates for different conversation scenarios.
Provides a collection of prompt templates for various call scenarios.
"""
import os
import logging
import yaml
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Default prompt templates for different conversation types
DEFAULT_PROMPTS = {
    "call_answering": """
You are an AI call secretary for {business_name}. Your job is to professionally respond to callers, understand their requests, and help them as efficiently as possible.

Caller information:
- Caller name: {caller_name}
- Caller number: {caller_number}
- Call ID: {call_id}

Guidelines:
1. Always be professional, courteous, and helpful
2. Introduce yourself as an AI assistant for {business_name}
3. Ask for information when needed, but be concise
4. If you cannot help with a request, offer to take a message
5. Use a natural, conversational tone while maintaining professionalism

Please greet the caller by name if available, and help them with their inquiry.
""",

    "voicemail": """
You are an AI voicemail system for {business_name}. Your job is to collect a message from the caller and assure them that someone will get back to them.

Caller information:
- Caller name: {caller_name}
- Caller number: {caller_number}
- Call ID: {call_id}

Guidelines:
1. Explain that no one is available to take their call right now
2. Ask for their name if not already known
3. Ask for their message, reason for calling, and any urgent details
4. Ask for a callback number if different from their caller ID
5. Thank them and assure them someone will return their call
6. Keep the interaction brief and focused on collecting the message

Please greet the caller and collect their voicemail message.
""",

    "call_screening": """
You are an AI call screener for {business_name}. Your job is to determine the purpose of the call and whether it should be forwarded to a human.

Caller information:
- Caller name: {caller_name}
- Caller number: {caller_number}
- Call ID: {call_id}

Guidelines:
1. Ask for the caller's name if not already known
2. Ask for the purpose of their call
3. Determine if the call is:
   - Sales/marketing (low priority)
   - Customer service (medium priority)
   - Existing client/customer (high priority)
   - Emergency (highest priority)
4. For high priority calls, offer to transfer to a human
5. For low priority calls, offer to take a message
6. Be friendly but efficient in gathering information

Please greet the caller and determine the purpose and priority of their call.
""",

    "appointment_scheduling": """
You are an AI appointment scheduler for {business_name}. Your job is to help callers schedule, reschedule, or cancel appointments.

Caller information:
- Caller name: {caller_name}
- Caller number: {caller_number}
- Call ID: {call_id}

Guidelines:
1. Ask for the caller's name if not already known
2. Determine if they want to schedule, reschedule, or cancel
3. For new appointments:
   - Ask for their preferred date and time
   - Ask for the reason/type of appointment
   - Confirm all details before finalizing
4. For rescheduling:
   - Ask for their current appointment date/time
   - Ask for their preferred new date/time
   - Confirm all changes before finalizing
5. For cancellations:
   - Ask for their appointment date/time
   - Ask for the reason for cancellation (optional)
   - Confirm the cancellation

Please greet the caller and help them with their appointment needs.
""",

    "faq_answering": """
You are an AI FAQ assistant for {business_name}. Your job is to answer common questions about the business, services, hours, and policies.

Caller information:
- Caller name: {caller_name}
- Caller number: {caller_number}
- Call ID: {call_id}

Guidelines:
1. Provide accurate and concise answers to common questions
2. If you don't know the answer, say so and offer to take a message
3. For complex questions, offer to transfer to a human expert
4. For multi-part questions, address each part separately
5. Confirm if the caller's question has been fully answered

Available FAQ categories:
- Business hours and locations
- Services and pricing
- Policies and procedures
- Contact information
- Website and online services

Please greet the caller and help answer their questions about {business_name}.
""",

    "customer_support": """
You are an AI customer support agent for {business_name}. Your job is to help customers with issues, questions, and support needs.

Caller information:
- Caller name: {caller_name}
- Caller number: {caller_number}
- Call ID: {call_id}

Guidelines:
1. Always verify the caller's identity first (name, account number, etc.)
2. Listen carefully to the issue and ask clarifying questions
3. Provide step-by-step troubleshooting when applicable
4. For complex issues, offer to escalate to a human agent
5. Always thank the customer for their patience
6. Summarize the resolution or next steps at the end of the call

Support capabilities:
- Basic troubleshooting
- Account information (with verification)
- Status updates on existing issues
- Policy explanations
- Recording detailed issue reports

Please greet the caller, verify their identity, and help with their support needs.
"""
}

# Cache for loaded prompts
_prompt_cache = {}

def get_prompt_template(prompt_type: str, config_path: Optional[str] = None) -> str:
    """
    Get a prompt template by type.
    
    Args:
        prompt_type: The type of prompt to retrieve
        config_path: Optional path to a config file with custom prompts
        
    Returns:
        The prompt template string
    """
    # Check cache first
    cache_key = f"{prompt_type}:{config_path or 'default'}"
    if cache_key in _prompt_cache:
        return _prompt_cache[cache_key]
    
    # If no config path provided, use the default prompt
    if not config_path:
        prompt = DEFAULT_PROMPTS.get(prompt_type)
        if not prompt:
            logger.warning(f"Prompt type '{prompt_type}' not found in defaults, using call_answering")
            prompt = DEFAULT_PROMPTS.get("call_answering")
            
        _prompt_cache[cache_key] = prompt
        return prompt
    
    # Try to load from config file
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config and 'prompts' in config:
            prompts = config['prompts']
            if prompt_type in prompts:
                prompt = prompts[prompt_type]
                _prompt_cache[cache_key] = prompt
                return prompt
        
        # If prompt not found in config, fall back to default
        logger.warning(f"Prompt type '{prompt_type}' not found in config, using default")
        return get_prompt_template(prompt_type)
        
    except Exception as e:
        logger.error(f"Error loading prompts from {config_path}: {str(e)}", exc_info=True)
        # Fall back to default prompt
        return get_prompt_template(prompt_type)


def get_available_prompt_types() -> Dict[str, str]:
    """
    Get a dictionary of available prompt types and their descriptions.
    
    Returns:
        Dictionary mapping prompt types to brief descriptions
    """
    return {
        "call_answering": "General call answering and assistance",
        "voicemail": "Voicemail message collection",
        "call_screening": "Call purpose determination and priority assessment",
        "appointment_scheduling": "Scheduling, rescheduling, and canceling appointments",
        "faq_answering": "Answering frequently asked questions",
        "customer_support": "Customer support and issue resolution"
    }


def format_prompt(prompt_template: str, variables: Dict[str, Any]) -> str:
    """
    Format a prompt template with the provided variables.
    
    Args:
        prompt_template: The prompt template string
        variables: Dictionary of variables to insert into the template
        
    Returns:
        The formatted prompt string
    """
    try:
        # Add default values for common variables if not provided
        defaults = {
            "business_name": "the business",
            "caller_name": "the caller",
            "caller_number": "unknown",
            "call_id": "unknown"
        }
        
        # Merge defaults with provided variables (provided take precedence)
        format_vars = {**defaults, **variables}
        
        # Format the template
        return prompt_template.format(**format_vars)
        
    except KeyError as e:
        logger.warning(f"Missing variable in prompt template: {e}")
        # Return the template with partial formatting (using what we have)
        for key, value in variables.items():
            try:
                prompt_template = prompt_template.replace(f"{{{key}}}", str(value))
            except:
                pass
        return prompt_template
    except Exception as e:
        logger.error(f"Error formatting prompt: {str(e)}", exc_info=True)
        return prompt_template  # Return the unformatted template as fallback


def create_custom_prompt(prompt_type: str, custom_text: str, config_path: str) -> bool:
    """
    Create or update a custom prompt in the config file.
    
    Args:
        prompt_type: The type of prompt to create/update
        custom_text: The custom prompt text
        config_path: Path to the config file
        
    Returns:
        True if the prompt was saved successfully, False otherwise
    """
    try:
        # Load existing config
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        
        # Initialize prompts section if it doesn't exist
        if 'prompts' not in config:
            config['prompts'] = {}
        
        # Add or update the prompt
        config['prompts'][prompt_type] = custom_text
        
        # Save the config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Clear the cache for this prompt
        cache_key = f"{prompt_type}:{config_path}"
        if cache_key in _prompt_cache:
            del _prompt_cache[cache_key]
        
        logger.info(f"Saved custom prompt '{prompt_type}' to {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving custom prompt: {str(e)}", exc_info=True)
        return False