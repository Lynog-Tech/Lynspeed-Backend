import logging
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
from itsdangerous import URLSafeTimedSerializer


logger = logging.getLogger(__name__)



def format_error_response(status_code, error_code, message, details=None):
    return {
        "status": "error",
        "status_code": status_code,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        }
    }

def get_user_by_email(email, CustomUser):
    user = cache.get(f"user_email_{email}")
    if not user:
        user = CustomUser.get_user_by_email(email)
        if user:
            cache.set(f"user_email_{email}", user)
    return user

def send_email(subject, body, to_email):
    try:
        email_message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email]
        )
        email_message.content_subtype = 'html'
        email_message.send()
        logger.info(f"Email sent to: {to_email}")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        raise

def generate_token(data, secret_key, salt):
    s = URLSafeTimedSerializer(secret_key)
    return s.dumps(data, salt=salt)

def verify_token(token, secret_key, salt, max_age=3600):
    s = URLSafeTimedSerializer(secret_key)
    return s.loads(token, salt=salt, max_age=max_age)

def decode_uid(uidb64):
    from django.utils.encoding import force_str
    return force_str(urlsafe_base64_decode(uidb64))
