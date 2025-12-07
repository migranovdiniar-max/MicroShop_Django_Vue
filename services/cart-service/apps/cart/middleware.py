import jwt
from django.conf import settings
from django.http import JsonResponse
from .services import UserService
import logging

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    """JWT Authentication Middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """"Skip health check and admin routes"""
        if request.path in ["/health", "/admin/"] or \
        request.path.startswith("/admin/"):
            return self.get_response(request)
        
        """Skip OPTIONS requests"""
        if request.method == "OPTIONS":
            return self.get_response(request)
        
        """Retrieve and verify JWT token"""
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            logger.info(
                f"Found auth token in request to {request.path}"
            )

            """Get the user via user service"""
            user_data = UserService.get_user_from_token(token)
            if user_data:
                request.user_id = user_data["id"]
                request.user_email = user_data["email"]
                logger.info(
                    f"Authenticated user {request.user_email} " \
                    f"with ID {user_data['id']} " \
                    f"for request to {request.path}"
                )

                response = self.get_response(request)
                return response
            
            else:
                logger.warning(
                    f"Failed to authenticate user for request to {request.path}"
                )
                return JsonResponse(
                    {
                        "error": "Invalid toke",
                        "message": "The provided authentication token is invalid"
                    }, status=401
                )
        else:
            logger.warning(
                f"No auth token found in request to {request.path}"
            )
            return JsonResponse(
                {
                    "error": "Authentication required",
                    "message": "No authentication token provided"
                }, status=401
            )
        
        response = self.get_response(request)
        return response