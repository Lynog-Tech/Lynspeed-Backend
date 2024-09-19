import logging
from rest_framework.test import APITestCase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseTestCase(APITestCase):
    """Base test case class to include common methods and logging."""

    def log_request_response(self, method, url, data=None, response=None):
        logger.info(f"Request method: {method}")
        logger.info(f"Request URL: {url}")
        if data:
            logger.info(f"Request body: {data}")
        if response:
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.data}")

    def assert_passed(self, test_name):
        logger.info(f"{test_name} PASSED \n ")

    def assert_failed(self, test_name, error):
        logger.error(f"{test_name} FAILED: {error} \n ")
        raise error
