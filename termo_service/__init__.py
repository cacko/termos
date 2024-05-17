from corelog import register, Handlers
import os

register(os.environ.get("TERMO_LOG_LEVEL", "INFO"), handler_type=Handlers.RICH)