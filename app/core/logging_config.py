import logging
import json
import sys
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="no-request-id")

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "logger": record.name,
        }
        return json.dumps(log_data)

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]