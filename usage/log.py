import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

logger = logging.getLogger('usage')
logger.setLevel(logging.DEBUG)
