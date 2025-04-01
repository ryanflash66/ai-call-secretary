#!/usr/bin/env python3
"""
Script to create an admin user for the AI Call Secretary system.
"""
import os
import sys
import argparse
import logging
import secrets
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Import security components
    from src.security.encryption import encryption_service
    from src.security.data_access import data_store, access_control
    from src.security.utils import security_utils
    from src.api.security_schemas import UserRole, UserStatus
except ImportError:
    print("Error: Could not import required modules.")
    print("Make sure you're running this script from the project root.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_admin_user(
    username: str,
    password: str,
    email: str,
    full_name: Optional[str] = None,
    force: bool = False
) -> bool:
    """
    Create a new admin user.
    
    Args:
        username: Username for the new admin
        password: Password for the new admin
        email: Email address for the new admin
        full_name: Full name for the new admin (optional)
        force: Force creation even if validation fails
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set admin context for data store access
        access_control.set_current_user(
            user_id="system",
            role=UserRole.ADMIN
        )
        
        # Check if user already exists
        users = data_store.load_data("users")
        if username in users:
            logger.error(f"User {username} already exists")
            return False
        
        # Validate email
        if not security_utils.validate_email(email) and not force:
            logger.error(f"Invalid email: {email}")
            return False
        
        # Validate password strength
        valid, reason = security_utils.validate_password_strength(password)
        if not valid and not force:
            logger.error(f"Password too weak: {reason}")
            return False
        
        # Hash password
        hashed_password, salt = encryption_service.hash_password(password)
        
        # Create user
        user_data = {
            "username": username,
            "hashed_password": hashed_password.hex(),
            "password_salt": salt.hex(),
            "email": email,
            "full_name": full_name,
            "role": UserRole.ADMIN,
            "status": UserStatus.ACTIVE,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "mfa_enabled": False,
            "failed_login_attempts": 0,
            "locked_until": None,
        }
        
        # Save user
        if username not in users:
            users[username] = user_data
            data_store.save_data("users", users)
            logger.info(f"Admin user {username} created successfully")
            return True
        else:
            logger.error(f"User {username} already exists")
            return False
            
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}", exc_info=True)
        return False
    finally:
        # Clear admin context
        access_control.clear_current_user()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create admin user for AI Call Secretary")
    
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Username for the admin user"
    )
    
    parser.add_argument(
        "--password",
        type=str,
        help="Password for the admin user (if not provided, will be generated)"
    )
    
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Email address for the admin user"
    )
    
    parser.add_argument(
        "--full-name",
        type=str,
        help="Full name for the admin user"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force creation even if validation fails"
    )
    
    args = parser.parse_args()
    
    # Generate password if not provided
    password = args.password
    if not password:
        password = security_utils.generate_password()
        logger.info(f"Generated password: {password}")
    
    # Create admin user
    success = create_admin_user(
        username=args.username,
        password=password,
        email=args.email,
        full_name=args.full_name,
        force=args.force
    )
    
    if success:
        print(f"Admin user '{args.username}' created successfully")
        if not args.password:
            print(f"Generated password: {password}")
            print("Please save this password as it won't be shown again")
    else:
        print("Failed to create admin user")
        sys.exit(1)


if __name__ == "__main__":
    main()