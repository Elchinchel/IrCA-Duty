import logging
import sys

from gunicorn import glogging


class Logger(glogging.Logger):
    def setup(self, cfg):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s.%(msecs)03d [%(levelname)s] (%(name)s) %(message)s',
                '%d.%m.%Y %H:%M:%S'
            )
        )
        handler.__from_gunicorn_logger__ = True  # pyright: ignore

        # this will be overriden in start:configure_logging (if it gonna be execute ofc)
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(handler)

        self.error_log.propagate = True
        self.error_log.setLevel(logging.INFO)
