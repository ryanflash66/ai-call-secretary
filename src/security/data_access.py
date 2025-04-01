"""
Secure data access layer for AI Call Secretary.
Provides controlled access to sensitive data with encryption and access logging.
"""
import os
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Set, Callable
from datetime import datetime

from src.security_config import security_config
from src.security.encryption import encryption_service
from src.security.audit_log import audit_log, AuditLogEvent, AuditLogLevel

# Initialize logging
logger = logging.getLogger(__name__)

class DataAccessControl:
    """
    Access control for secure data access.
    Implements role-based access control with data masking and encryption.
    """
    
    def __init__(self):
        """Initialize the data access control system."""
        # Role-permission mappings
        self.role_permissions = {
            "admin": {
                "users": {"read", "write", "delete"},
                "calls": {"read", "write", "delete"},
                "messages": {"read", "write", "delete"},
                "appointments": {"read", "write", "delete"},
                "system_settings": {"read", "write"},
                "audit_logs": {"read"},
            },
            "manager": {
                "users": {"read"},
                "calls": {"read", "write"},
                "messages": {"read", "write"},
                "appointments": {"read", "write"},
                "system_settings": {"read"},
                "audit_logs": {"read"},
            },
            "operator": {
                "calls": {"read", "write"},
                "messages": {"read", "write"},
                "appointments": {"read", "write"},
            },
            "viewer": {
                "calls": {"read"},
                "messages": {"read"},
                "appointments": {"read"},
            },
        }
        
        # Field sensitivity levels
        self.field_sensitivity = {
            "users": {
                "username": "public",
                "email": "protected",
                "password": "restricted",
                "phone": "protected",
                "address": "restricted",
            },
            "calls": {
                "call_id": "public",
                "caller_number": "protected",
                "caller_name": "protected",
                "start_time": "public",
                "end_time": "public",
                "duration": "public",
                "status": "public",
                "transcript": "protected",
                "credit_card_info": "restricted",
                "ssn": "restricted",
            },
            "messages": {
                "message_id": "public",
                "caller_name": "protected",
                "caller_number": "protected",
                "message": "protected",
                "timestamp": "public",
                "status": "public",
            },
            "appointments": {
                "appointment_id": "public",
                "date": "public",
                "time": "public",
                "duration": "public",
                "name": "protected",
                "phone": "protected",
                "email": "protected",
                "purpose": "protected",
                "notes": "protected",
            },
        }
        
        # Thread-local storage for current user context
        self.user_context = threading.local()
        
        logger.info("Data Access Control initialized")
    
    def set_current_user(self, user_id: str, role: str) -> None:
        """
        Set the current user context.
        
        Args:
            user_id: User ID
            role: User role
        """
        self.user_context.user_id = user_id
        self.user_context.role = role
    
    def clear_current_user(self) -> None:
        """Clear the current user context."""
        if hasattr(self.user_context, "user_id"):
            delattr(self.user_context, "user_id")
        if hasattr(self.user_context, "role"):
            delattr(self.user_context, "role")
    
    def get_current_user(self) -> tuple:
        """
        Get the current user context.
        
        Returns:
            Tuple of (user_id, role)
        """
        user_id = getattr(self.user_context, "user_id", None)
        role = getattr(self.user_context, "role", None)
        return user_id, role
    
    def has_permission(self, resource_type: str, permission: str) -> bool:
        """
        Check if current user has permission for a resource type.
        
        Args:
            resource_type: Type of resource
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        _, role = self.get_current_user()
        if not role:
            return False
        
        # Admins have all permissions
        if role == "admin":
            return True
        
        # Check role permissions
        role_perms = self.role_permissions.get(role, {})
        resource_perms = role_perms.get(resource_type, set())
        
        return permission in resource_perms
    
    def filter_fields(self, resource_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter and mask fields based on user's role and field sensitivity.
        
        Args:
            resource_type: Type of resource
            data: Data to filter
            
        Returns:
            Filtered data
        """
        _, role = self.get_current_user()
        if not role:
            # Return minimal public data if no user context
            return self._filter_by_sensitivity(resource_type, data, {"public"})
        
        # Admins see everything
        if role == "admin":
            return data
        
        # Determine visible sensitivity levels based on role
        visible_levels = {"public"}
        if role in ["admin", "manager", "operator"]:
            visible_levels.add("protected")
        if role in ["admin"]:
            visible_levels.add("restricted")
        
        # Filter data
        return self._filter_by_sensitivity(resource_type, data, visible_levels)
    
    def _filter_by_sensitivity(
        self, resource_type: str, data: Dict[str, Any], visible_levels: Set[str]
    ) -> Dict[str, Any]:
        """
        Filter data by field sensitivity levels.
        
        Args:
            resource_type: Type of resource
            data: Data to filter
            visible_levels: Set of visible sensitivity levels
            
        Returns:
            Filtered data
        """
        # Get field sensitivity map for resource type
        sensitivity_map = self.field_sensitivity.get(resource_type, {})
        
        # Create filtered result
        result = {}
        for field, value in data.items():
            field_sensitivity = sensitivity_map.get(field, "protected")
            
            if field_sensitivity in visible_levels:
                # Field is visible to user
                result[field] = value
            elif field_sensitivity == "protected" and "public" in visible_levels:
                # Mask protected fields
                result[field] = self._mask_field(field, value)
            # Restricted fields are omitted entirely
        
        return result
    
    def _mask_field(self, field: str, value: Any) -> Any:
        """
        Mask a field value.
        
        Args:
            field: Field name
            value: Field value
            
        Returns:
            Masked value
        """
        if value is None:
            return None
        
        if field in ["email"]:
            # Mask email (show first 2 chars and domain)
            if "@" in value:
                username, domain = value.split("@", 1)
                return f"{username[:2]}{'*' * (len(username) - 2)}@{domain}"
            return "****"
        
        if field in ["caller_number", "phone"]:
            # Mask phone number (show last 4 digits)
            if isinstance(value, str) and len(value) >= 4:
                return f"{'*' * (len(value) - 4)}{value[-4:]}"
            return "****"
        
        if field in ["caller_name", "name"]:
            # Mask name (show first letter)
            if isinstance(value, str) and len(value) > 0:
                return f"{value[0]}{'*' * (len(value) - 1)}"
            return "****"
        
        if field in ["message"]:
            # Return placeholder for message
            return "[Message content hidden]"
        
        # Default masking
        if isinstance(value, str):
            if len(value) <= 4:
                return "****"
            return f"{value[:1]}{'*' * (len(value) - 2)}{value[-1:]}"
        
        return "****"


class SecureDataStore:
    """
    Secure data storage with encryption and access control.
    """
    
    def __init__(self, access_control: DataAccessControl, data_dir: Optional[str] = None):
        """
        Initialize the secure data store.
        
        Args:
            access_control: Data access control instance
            data_dir: Directory to store data files. If None, will use 'data/'
        """
        self.access_control = access_control
        self.data_dir = data_dir or "data"
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Cache for data objects
        self.cache = {}
        
        # Cache initialization lock
        self.cache_locks = {}
        
        logger.info(f"Secure Data Store initialized with path: {self.data_dir}")
    
    def get_data_file_path(self, resource_type: str) -> str:
        """
        Get path to data file for a resource type.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            Path to data file
        """
        return os.path.join(self.data_dir, f"{resource_type}.json")
    
    def load_data(self, resource_type: str) -> Dict[str, Any]:
        """
        Load data from file for a resource type.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            Data dictionary
        """
        # Check cache first
        if resource_type in self.cache:
            return self.cache[resource_type]
        
        # Create lock for this resource type if it doesn't exist
        if resource_type not in self.cache_locks:
            self.cache_locks[resource_type] = threading.Lock()
        
        # Acquire lock to prevent concurrent initialization
        with self.cache_locks[resource_type]:
            # Check cache again after acquiring lock
            if resource_type in self.cache:
                return self.cache[resource_type]
            
            # Load from file
            file_path = self.get_data_file_path(resource_type)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        encrypted_data = json.load(f)
                    
                    # Decrypt data
                    data = encryption_service.decrypt_dict(encrypted_data)
                    
                    # Update cache
                    self.cache[resource_type] = data
                    
                    return data
                except Exception as e:
                    logger.error(
                        f"Error loading data for {resource_type}: {str(e)}",
                        exc_info=True
                    )
            
            # Return empty dict if file doesn't exist or error occurred
            self.cache[resource_type] = {}
            return {}
    
    def save_data(self, resource_type: str, data: Dict[str, Any]) -> bool:
        """
        Save data to file for a resource type.
        
        Args:
            resource_type: Type of resource
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create lock for this resource type if it doesn't exist
            if resource_type not in self.cache_locks:
                self.cache_locks[resource_type] = threading.Lock()
            
            # Acquire lock to prevent concurrent writes
            with self.cache_locks[resource_type]:
                # Encrypt data
                encrypted_data = encryption_service.encrypt_dict(data)
                
                # Save to file
                file_path = self.get_data_file_path(resource_type)
                with open(file_path, "w") as f:
                    json.dump(encrypted_data, f, indent=2)
                
                # Update cache
                self.cache[resource_type] = data
                
                return True
        except Exception as e:
            logger.error(
                f"Error saving data for {resource_type}: {str(e)}",
                exc_info=True
            )
            return False
    
    def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a resource by ID.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            
        Returns:
            Resource data or None if not found or no permission
        """
        # Check if user has read permission
        if not self.access_control.has_permission(resource_type, "read"):
            logger.warning(
                f"Access denied: reading {resource_type} (user: {self.access_control.get_current_user()[0]})"
            )
            
            # Log to audit log
            user_id, _ = self.access_control.get_current_user()
            audit_log.log_event(
                event_type=AuditLogEvent.ACCESS_DENIED,
                level=AuditLogLevel.WARNING,
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=resource_id,
                message=f"Access denied: reading {resource_type} {resource_id}"
            )
            
            return None
        
        # Load data
        data = self.load_data(resource_type)
        
        # Check if resource exists
        if resource_id not in data:
            return None
        
        # Get resource
        resource = data[resource_id]
        
        # Filter fields based on user's role
        filtered_resource = self.access_control.filter_fields(resource_type, resource)
        
        # Log access to audit log
        user_id, _ = self.access_control.get_current_user()
        audit_log.log_event(
            event_type=AuditLogEvent.DATA_ACCESS,
            level=AuditLogLevel.INFO,
            user=user_id or "anonymous",
            resource_type=resource_type,
            resource_id=resource_id,
            message=f"Access: reading {resource_type} {resource_id}"
        )
        
        return filtered_resource
    
    def list_resources(
        self, resource_type: str, filter_func: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        List resources of a type.
        
        Args:
            resource_type: Type of resource
            filter_func: Optional function to filter resources
            
        Returns:
            List of filtered resources
        """
        # Check if user has read permission
        if not self.access_control.has_permission(resource_type, "read"):
            logger.warning(
                f"Access denied: listing {resource_type} (user: {self.access_control.get_current_user()[0]})"
            )
            
            # Log to audit log
            user_id, _ = self.access_control.get_current_user()
            audit_log.log_event(
                event_type=AuditLogEvent.ACCESS_DENIED,
                level=AuditLogLevel.WARNING,
                user=user_id or "anonymous",
                resource_type=resource_type,
                message=f"Access denied: listing {resource_type}"
            )
            
            return []
        
        # Load data
        data = self.load_data(resource_type)
        
        # Filter resources
        resources = []
        for resource_id, resource in data.items():
            # Apply custom filter if provided
            if filter_func and not filter_func(resource):
                continue
            
            # Filter fields based on user's role
            filtered_resource = self.access_control.filter_fields(resource_type, resource)
            resources.append(filtered_resource)
        
        # Log access to audit log
        user_id, _ = self.access_control.get_current_user()
        audit_log.log_event(
            event_type=AuditLogEvent.DATA_ACCESS,
            level=AuditLogLevel.INFO,
            user=user_id or "anonymous",
            resource_type=resource_type,
            message=f"Access: listing {resource_type} (count: {len(resources)})"
        )
        
        return resources
    
    def create_resource(self, resource_type: str, resource_id: str, resource: Dict[str, Any]) -> bool:
        """
        Create a new resource.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            resource: Resource data
            
        Returns:
            True if successful, False otherwise
        """
        # Check if user has write permission
        if not self.access_control.has_permission(resource_type, "write"):
            logger.warning(
                f"Access denied: creating {resource_type} (user: {self.access_control.get_current_user()[0]})"
            )
            
            # Log to audit log
            user_id, _ = self.access_control.get_current_user()
            audit_log.log_event(
                event_type=AuditLogEvent.ACCESS_DENIED,
                level=AuditLogLevel.WARNING,
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=resource_id,
                message=f"Access denied: creating {resource_type} {resource_id}"
            )
            
            return False
        
        # Load data
        data = self.load_data(resource_type)
        
        # Check if resource already exists
        if resource_id in data:
            logger.warning(f"Resource already exists: {resource_type} {resource_id}")
            return False
        
        # Add metadata
        user_id, _ = self.access_control.get_current_user()
        resource["created_by"] = user_id
        resource["created_at"] = datetime.utcnow().isoformat()
        resource["updated_by"] = user_id
        resource["updated_at"] = datetime.utcnow().isoformat()
        
        # Add resource
        data[resource_id] = resource
        
        # Save data
        success = self.save_data(resource_type, data)
        
        if success:
            # Log to audit log
            audit_log.log_event(
                event_type=AuditLogEvent.DATA_MODIFICATION,
                level=AuditLogLevel.INFO,
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=resource_id,
                message=f"Created: {resource_type} {resource_id}"
            )
        
        return success
    
    def update_resource(
        self, resource_type: str, resource_id: str, updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing resource.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        # Check if user has write permission
        if not self.access_control.has_permission(resource_type, "write"):
            logger.warning(
                f"Access denied: updating {resource_type} (user: {self.access_control.get_current_user()[0]})"
            )
            
            # Log to audit log
            user_id, _ = self.access_control.get_current_user()
            audit_log.log_event(
                event_type=AuditLogEvent.ACCESS_DENIED,
                level=AuditLogLevel.WARNING,
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=resource_id,
                message=f"Access denied: updating {resource_type} {resource_id}"
            )
            
            return False
        
        # Load data
        data = self.load_data(resource_type)
        
        # Check if resource exists
        if resource_id not in data:
            logger.warning(f"Resource not found: {resource_type} {resource_id}")
            return False
        
        # Get existing resource
        resource = data[resource_id]
        
        # Update metadata
        user_id, _ = self.access_control.get_current_user()
        updates["updated_by"] = user_id
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        # Apply updates
        resource.update(updates)
        
        # Save data
        success = self.save_data(resource_type, data)
        
        if success:
            # Log to audit log
            audit_log.log_event(
                event_type=AuditLogEvent.DATA_MODIFICATION,
                level=AuditLogLevel.INFO,
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=resource_id,
                message=f"Updated: {resource_type} {resource_id}"
            )
        
        return success
    
    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a resource.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            
        Returns:
            True if successful, False otherwise
        """
        # Check if user has delete permission
        if not self.access_control.has_permission(resource_type, "delete"):
            logger.warning(
                f"Access denied: deleting {resource_type} (user: {self.access_control.get_current_user()[0]})"
            )
            
            # Log to audit log
            user_id, _ = self.access_control.get_current_user()
            audit_log.log_event(
                event_type=AuditLogEvent.ACCESS_DENIED,
                level=AuditLogLevel.WARNING,
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=resource_id,
                message=f"Access denied: deleting {resource_type} {resource_id}"
            )
            
            return False
        
        # Load data
        data = self.load_data(resource_type)
        
        # Check if resource exists
        if resource_id not in data:
            logger.warning(f"Resource not found: {resource_type} {resource_id}")
            return False
        
        # Delete resource
        del data[resource_id]
        
        # Save data
        success = self.save_data(resource_type, data)
        
        if success:
            # Log to audit log
            user_id, _ = self.access_control.get_current_user()
            audit_log.log_event(
                event_type=AuditLogEvent.DATA_DELETION,
                level=AuditLogLevel.INFO,
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=resource_id,
                message=f"Deleted: {resource_type} {resource_id}"
            )
        
        return success
    
    def search_resources(
        self, resource_type: str, query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Search for resources matching a query.
        
        Args:
            resource_type: Type of resource
            query: Search query (field-value pairs)
            
        Returns:
            List of matching resources
        """
        # Define filter function
        def filter_func(resource):
            for field, value in query.items():
                # Skip metadata fields
                if field in ["created_by", "created_at", "updated_by", "updated_at"]:
                    continue
                
                # Check if resource has the field
                if field not in resource:
                    return False
                
                # Handle different value types
                if isinstance(value, str) and isinstance(resource[field], str):
                    # Case-insensitive string match
                    if value.lower() not in resource[field].lower():
                        return False
                elif resource[field] != value:
                    # Exact match for non-string types
                    return False
            
            return True
        
        # Use list_resources with filter
        return self.list_resources(resource_type, filter_func)


# Create global instances
access_control = DataAccessControl()
data_store = SecureDataStore(access_control)