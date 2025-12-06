import json 
import redis 
import threading
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def start_event_listener():
    """
    Redis event listener
    """
    try: 
        redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, 
            db=settings.REDIS_DB, decode_responses=True
        )
        pubsub = redis_client.pubsub()
        pubsub.subscribe("events")

        logger.info("Product service event listener started")

        for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    event_data = json.loads(message["data"])
                    handle_event(event_data)
                except Exception as e:
                    logger.error(f"Error handling event: {e}")

    except Exception as e:
        logger.error(f"Error starting event listener: {e}")


def handle_event(event_data):
    """
    Handle events from Redis
    """
    event_type = event_data.get("type")
    data = event_data.get("data", {})

    if event_type == "order.cancelled":
        """Restore the stock"""
        from .models import Product

        order_items = data.get("items", [])
        for item in order_items:
            try:
                product = Product.objects.get(id=item["product_id"])
                product.release_quantity(item["quantity"])
                logger.info(f"Released {item['quantity']} units of product {product.id}")
            except Product.DoesNotExist:
                logger.error(
                    f"Product {item['product_id']} not found for cancellation event"
                )


if settings.DEBUG:
    thread = threading.Thread(
        target=start_event_listener, daemon=True
    )
    thread.start()