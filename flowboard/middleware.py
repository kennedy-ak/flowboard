"""
Custom middleware for debugging and logging.
"""
import logging

logger = logging.getLogger(__name__)


class AuthenticationDebugMiddleware:
    """
    Middleware to debug authentication and session issues.
    Enable this temporarily to diagnose login/logout problems.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log authentication status before processing
        if request.path not in ['/static/', '/media/']:  # Skip static files
            logger.debug(f"[AUTH DEBUG] Path: {request.path}")
            logger.debug(f"[AUTH DEBUG] User: {request.user}")
            logger.debug(f"[AUTH DEBUG] Is Authenticated: {request.user.is_authenticated}")
            logger.debug(f"[AUTH DEBUG] Session Key: {request.session.session_key}")
            logger.debug(f"[AUTH DEBUG] Session Data: {dict(request.session)}")

            # Print to console for immediate debugging
            print(f"\n=== AUTH DEBUG ===")
            print(f"Path: {request.path}")
            print(f"Method: {request.method}")
            print(f"User: {request.user}")
            print(f"Authenticated: {request.user.is_authenticated}")
            print(f"Session Key: {request.session.session_key}")
            print(f"Cookies: {request.COOKIES.keys()}")
            print(f"==================\n")

        response = self.get_response(request)
        return response
