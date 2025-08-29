import logging
from corelog import register, Handlers
import os
import uvicorn
from termos.app import create_app

register(os.environ.get("TERMO_LOG_LEVEL", "INFO"), handler_type=Handlers.RICH)


def start():
    try:
        uvicorn.run(create_app, host="0.0.0.0", port=23727, log_level="info", loop="uvloop", factory=True, access_log=True)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception(e)
