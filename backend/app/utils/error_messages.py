"""Error message utilities for user-friendly error handling"""

from typing import Optional
from enum import Enum


class ErrorCategory(Enum):
    """Error categories for better user guidance"""
    NETWORK = "network"
    API = "api"
    USER = "user"
    SERVER = "server"
    FILE = "file"


class ErrorMessage:
    """Structured error message with actionable guidance"""
    
    def __init__(
        self,
        title: str,
        message: str,
        category: ErrorCategory,
        actionable_steps: list[str],
        support_contact: Optional[str] = None,
    ):
        self.title = title
        self.message = message
        self.category = category
        self.actionable_steps = actionable_steps
        self.support_contact = support_contact or "support@transkeep.com"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "title": self.title,
            "message": self.message,
            "category": self.category.value,
            "actionable_steps": self.actionable_steps,
            "support_contact": self.support_contact,
        }


# Predefined error messages
ERROR_MESSAGES = {
    # Network errors
    "network_timeout": ErrorMessage(
        title="Connection Timeout",
        message="The request took too long to complete. This might be due to a slow internet connection or server issues.",
        category=ErrorCategory.NETWORK,
        actionable_steps=[
            "Check your internet connection",
            "Try again in a few moments",
            "If the problem persists, contact support",
        ],
    ),
    "network_error": ErrorMessage(
        title="Network Error",
        message="Unable to connect to the server. Please check your internet connection.",
        category=ErrorCategory.NETWORK,
        actionable_steps=[
            "Verify your internet connection is working",
            "Try refreshing the page",
            "Check if other websites are accessible",
        ],
    ),
    
    # API errors
    "deepl_unavailable": ErrorMessage(
        title="Translation Service Unavailable",
        message="The primary translation service is temporarily unavailable. We're using a backup service with slightly lower quality.",
        category=ErrorCategory.API,
        actionable_steps=[
            "Your translation will continue with backup service",
            "Quality may be slightly lower than usual",
            "No action needed - we'll notify you when complete",
        ],
    ),
    "claude_unavailable": ErrorMessage(
        title="Tone Customization Unavailable",
        message="Tone customization is temporarily unavailable. Your translation will complete without tone adjustments.",
        category=ErrorCategory.API,
        actionable_steps=[
            "Your translation will complete normally",
            "Tone customization will be skipped",
            "You can retry tone customization later if needed",
        ],
    ),
    
    # File errors
    "file_too_large": ErrorMessage(
        title="File Too Large",
        message="Your file exceeds the 100MB size limit.",
        category=ErrorCategory.FILE,
        actionable_steps=[
            "Try splitting the PDF into smaller files",
            "Compress the PDF if possible",
            "Contact support for assistance with large files",
        ],
    ),
    "invalid_file_type": ErrorMessage(
        title="Invalid File Type",
        message="Only PDF files are supported.",
        category=ErrorCategory.FILE,
        actionable_steps=[
            "Ensure your file is a PDF (.pdf extension)",
            "Convert other file types to PDF first",
            "Check that the file is not corrupted",
        ],
    ),
    "scanned_pdf": ErrorMessage(
        title="Scanned PDF Detected",
        message="This PDF appears to be scanned (image-based). Limited text was extracted.",
        category=ErrorCategory.FILE,
        actionable_steps=[
            "For best results, use a PDF with selectable text",
            "OCR support is planned for Phase 2",
            "You can still proceed, but translation quality may be limited",
        ],
    ),
    
    # Server errors
    "server_error": ErrorMessage(
        title="Server Error",
        message="An unexpected error occurred on our servers. We're working to fix it.",
        category=ErrorCategory.SERVER,
        actionable_steps=[
            "Try again in a few minutes",
            "If the problem persists, contact support",
            "Your file has been saved and will be processed when service is restored",
        ],
    ),
    
    # User errors
    "unauthorized": ErrorMessage(
        title="Authentication Required",
        message="Please sign in to continue.",
        category=ErrorCategory.USER,
        actionable_steps=[
            "Sign in with your account",
            "If you don't have an account, create one",
            "Check that your session hasn't expired",
        ],
    ),
    "quota_exceeded": ErrorMessage(
        title="Translation Quota Exceeded",
        message="You've reached your monthly translation limit.",
        category=ErrorCategory.USER,
        actionable_steps=[
            "Upgrade to a higher tier for more translations",
            "Wait until next month for quota reset",
            "Contact support for assistance",
        ],
    ),
}


def get_error_message(error_key: str) -> ErrorMessage:
    """
    Get a user-friendly error message by key.
    
    Args:
        error_key: Error message key
        
    Returns:
        ErrorMessage object or default error message
    """
    return ERROR_MESSAGES.get(error_key, ErrorMessage(
        title="An Error Occurred",
        message="Something went wrong. Please try again.",
        category=ErrorCategory.SERVER,
        actionable_steps=[
            "Try again",
            "If the problem persists, contact support",
        ],
    ))


def categorize_error(error: Exception) -> ErrorCategory:
    """
    Categorize an error based on its type.
    
    Args:
        error: Exception object
        
    Returns:
        ErrorCategory
    """
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    if "network" in error_str or "connection" in error_str or "timeout" in error_str:
        return ErrorCategory.NETWORK
    elif "api" in error_str or "quota" in error_str or "rate limit" in error_str:
        return ErrorCategory.API
    elif "file" in error_str or "pdf" in error_str or "size" in error_str:
        return ErrorCategory.FILE
    elif "auth" in error_str or "unauthorized" in error_str or "permission" in error_str:
        return ErrorCategory.USER
    else:
        return ErrorCategory.SERVER
