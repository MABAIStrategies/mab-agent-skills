"""
MAB AI Strategies - Shared Logging Module
Structured logging with PII redaction and Cloud Logging integration
"""

import os
import re
import json
import logging
import traceback
from typing import Any, Dict
from datetime import datetime
from functools import wraps

# Google Cloud Logging
try:
    from google.cloud import logging as cloud_logging
    CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    CLOUD_LOGGING_AVAILABLE = False

# Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENABLE_STRUCTURED_LOGGING = os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true"
ENABLE_CLOUD_LOGGING = os.getenv("ENABLE_CLOUD_LOGGING", "false").lower() == "true"
ENABLE_PII_REDACTION = os.getenv("ENABLE_PII_REDACTION", "true").lower() == "true"

# PII Patterns
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
}


class PIIRedactor:
    """Redact PII from log messages"""
    
    @staticmethod
    def redact(text: str) -> str:
        """
        Redact PII from text
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text
        """
        if not ENABLE_PII_REDACTION:
            return text
        
        redacted = text
        
        for pii_type, pattern in PII_PATTERNS.items():
            redacted = re.sub(
                pattern,
                f"[REDACTED_{pii_type.upper()}]",
                redacted
            )
        
        return redacted


class StructuredLogger:
    """Structured logging with Cloud Logging support"""
    
    def __init__(self, name: str, skill_name: str = None):
        self.name = name
        self.skill_name = skill_name or os.getenv("SKILL_NAME", "unknown")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Setup Cloud Logging if enabled
        if ENABLE_CLOUD_LOGGING and CLOUD_LOGGING_AVAILABLE:
            try:
                client = cloud_logging.Client()
                handler = client.get_default_handler()
                self.logger.addHandler(handler)
            except Exception as e:
                print(f"Failed to setup Cloud Logging: {e}")
        else:
            # Local console logging
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _format_message(
        self,
        message: str,
        extra: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Format log message as structured data"""
        
        # Redact PII
        message = PIIRedactor.redact(message)
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "skill": self.skill_name,
            "message": message,
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        if user_id:
            log_data["user_id"] = user_id
        
        if extra:
            # Redact PII from extra fields
            for key, value in extra.items():
                if isinstance(value, str):
                    extra[key] = PIIRedactor.redact(value)
            
            log_data["extra"] = extra
        
        return log_data
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        if ENABLE_STRUCTURED_LOGGING:
            log_data = self._format_message(message, kwargs.get('extra'), kwargs.get('user_id'))
            self.logger.debug(json.dumps(log_data))
        else:
            self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        if ENABLE_STRUCTURED_LOGGING:
            log_data = self._format_message(message, kwargs.get('extra'), kwargs.get('user_id'))
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        if ENABLE_STRUCTURED_LOGGING:
            log_data = self._format_message(message, kwargs.get('extra'), kwargs.get('user_id'))
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.warning(message)
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message with optional exception"""
        extra = kwargs.get('extra', {})
        
        if error:
            extra['error_type'] = type(error).__name__
            extra['error_message'] = str(error)
            extra['traceback'] = traceback.format_exc()
        
        if ENABLE_STRUCTURED_LOGGING:
            log_data = self._format_message(message, extra, kwargs.get('user_id'))
            self.logger.error(json.dumps(log_data))
        else:
            self.logger.error(f"{message}: {error}" if error else message)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        if ENABLE_STRUCTURED_LOGGING:
            log_data = self._format_message(message, kwargs.get('extra'), kwargs.get('user_id'))
            self.logger.critical(json.dumps(log_data))
        else:
            self.logger.critical(message)


class AuditLogger:
    """Audit logging for compliance"""
    
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.logger = StructuredLogger(f"{skill_name}.audit", skill_name)
    
    def log_action(
        self,
        action: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any] = None,
        success: bool = True
    ):
        """
        Log an auditable action
        
        Args:
            action: Action performed (CREATE, UPDATE, DELETE, READ)
            user_id: User who performed action
            resource_type: Type of resource affected
            resource_id: ID of resource
            details: Additional details
            success: Whether action succeeded
        """
        audit_entry = {
            "action": action,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            audit_entry["details"] = details
        
        self.logger.info(
            f"AUDIT: {action} on {resource_type}:{resource_id}",
            extra=audit_entry,
            user_id=user_id
        )
        
        # Also store in Firestore for compliance
        if os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true":
            from shared.database import get_firestore_client
            
            db = get_firestore_client()
            db.collection("audit_logs").add(audit_entry)


def log_function_call(logger: StructuredLogger = None):
    """
    Decorator to log function calls
    
    Args:
        logger: Logger instance (creates default if None)
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = StructuredLogger(__name__)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(
                f"Calling {func_name}",
                extra={
                    "function": func_name,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }
            )
            
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}", error=e)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(
                f"Calling {func_name}",
                extra={
                    "function": func_name,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }
            )
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}", error=e)
                raise
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global logger factory
def get_logger(name: str, skill_name: str = None) -> StructuredLogger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        skill_name: Skill name for context
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, skill_name)
