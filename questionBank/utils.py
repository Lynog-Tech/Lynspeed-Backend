from rest_framework import status
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

def format_error_response(status_code, error_code, message, details=None):
    """
    Utility function to format error responses in a standard structure.
    """
    return {
        "status": "error",
        "status_code": status_code,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        }
    }

def validate_subject_selection(subject_names, required_subject="English", required_count=4):
    """
    Validates if the subject selection contains the required subject and the correct number of subjects.
    """
    return required_subject in subject_names and len(subject_names) == required_count

def handle_invalid_selection(selected, required_length=4, compulsory_subject="English"):
    """
    Validates subject selection. Ensures a compulsory subject is included and the required number is selected.
    """
    if compulsory_subject not in selected or len(selected) != required_length:
        logger.warning(f"Invalid subject selection: {compulsory_subject} must be included and {required_length} subjects must be selected.")
        return False
    return True
