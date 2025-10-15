import logging, sys

def setup_logger():
    log = logging.getLogger("prodify")
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s"
    ))
    log.handlers = [handler]
    return log

logger = setup_logger()
