import logging
import time
import uuid

from fastapi import Request, Response
import structlog

from disguisedcats.settings import settings

logger = structlog.stdlib.get_logger("disguisedcats")


def setup():
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    shared_processors: list[structlog.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.DEBUG:
        log_renderer = structlog.dev.ConsoleRenderer()
    else:
        log_renderer = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL)

    for _log in ["uvicorn", "uvicorn.error"]:
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False


async def middleware(request: Request, next) -> Response:
    structlog.contextvars.clear_contextvars()
    correlation_id = str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    start_time = time.perf_counter_ns()
    try:
        response = await next(request)
    except Exception:
        structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code or 500
        logger.info(
            "Request",
            http={
                "url": str(request.url),
                "status_code": status_code,
                "method": request.method,
                "correlation_id": correlation_id,
                "version": request.scope["http_version"],
            },
            duration=process_time,
        )
    return response
