import requests
import logging
from django.conf import settings
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class ProductService:
    """Service for interacting with the product API."""

    @staticmethod
    def get_product(product_id: str) -> Optional[Dict[str, Any]]:
        """Obtain product details from the API."""

        try:
            response = requests.get(
                f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/",
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return None
        
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error fetching product {product_id}: {e}"
            )
            return None
        

@staticmethod
def check_availability(product_id: str, quantity: int) -> bool:
    """Check product availability."""
    try:
        response = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/check-availability/",
            params={"quantity": quantity},
            timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("available", False)
        return False
    
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error checking availability for product {product_id}: {e}"
        )
        return False
    

class UserService:
    """Service for interacting with the user API."""

    @staticmethod
    def get_user_details(token: str) -> Optional[Dict[str, Any]]:
        """Obtaining user details from the API by token."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/users/profile/",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user details: {e}")
            return None