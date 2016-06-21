import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

logger = logging.getLogger('usage')
logger.setLevel(logging.INFO)
