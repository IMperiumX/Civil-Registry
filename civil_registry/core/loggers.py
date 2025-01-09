import logging
from typing import Any

from django.utils.timezone import now
from structlog import get_logger

throwaways = set()


class HumanRenderer:
    def __call__(self, logger, name, event_dict):
        level = event_dict.pop("level")
        real_level = (
            level.upper() if isinstance(level, str) else logging.getLevelName(level)
        )
        base = "{} [{}] {}: {}".format(
            now().strftime("%H:%M:%S"),
            real_level,
            event_dict.pop("name", "root"),
            event_dict.pop("event", ""),
        )
        join = " ".join(k + "=" + repr(v) for k, v in event_dict.items())
        return "{}{}".format(base, (" (%s)" % join if join else ""))


class StructLogHandler(logging.StreamHandler):
    def get_log_kwargs(self, record: logging.LogRecord) -> dict[str, Any]:
        kwargs = {
            k: v
            for k, v in vars(record).items()
            if k not in throwaways and v is not None
        }
        kwargs.update({"level": record.levelno, "event": record.msg})

        if record.args:
            # record.args inside of LogRecord.__init__ gets unrolled
            # if it's the shape `({},)`, a single item dictionary.
            # so we need to check for this, and re-wrap it because
            # down the line of structlog, it's expected to be this
            # original shape.
            if isinstance(record.args, (tuple, list)):
                kwargs["positional_args"] = record.args
            else:
                kwargs["positional_args"] = (record.args,)

        return kwargs

    def emit(
        self, record: logging.LogRecord, logger: logging.Logger | None = None
    ) -> None:
        # If anyone wants to use the 'extra' kwarg to provide context within
        # structlog, we have to strip all of the default attributes from
        # a record because the RootLogger will take the 'extra' dictionary
        # and just turn them into attributes.
        try:
            if logger is None:
                logger = get_logger()
            logger.log(**self.get_log_kwargs(record=record))
        except Exception:
            if logging.raiseExceptions:
                raise


def configure_structlog() -> None:
    """
    Make structlog comply with all of our options.
    """
    import logging.config

    import structlog
    from django.conf import settings

    kwargs = {
        "wrapper_class": structlog.stdlib.BoundLogger,
        "cache_logger_on_first_use": True,
        "processors": [
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.format_exc_info,
        ],
    }

    kwargs["processors"].extend(
        [structlog.processors.ExceptionPrettyPrinter(), HumanRenderer()]
    )

    structlog.configure(**kwargs)

    lvl = settings.LOG_LEVEL

    if lvl and lvl not in logging._nameToLevel:
        raise AttributeError("%s is not a valid logging level." % lvl)

    settings.LOGGING["root"].update({"level": lvl or settings.LOGGING["default_level"]})

    if lvl:
        for logger in settings.LOGGING["overridable"]:
            try:
                settings.LOGGING["loggers"][logger].update({"level": lvl})
            except KeyError:
                raise KeyError("%s is not a defined logger." % logger)

    logging.config.dictConfig(settings.LOGGING)
