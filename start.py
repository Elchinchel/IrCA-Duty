import logging.config
import logging.handlers
import os
import sys

from duty import config
from duty.app import create_app
from duty.utils.misc import ROOT_DIR


def configure_logging():
    for hdlr in logging.root.handlers:
        # if handler added by duty.utils.gunicorn.Logger
        if getattr(hdlr, '__from_gunicorn_logger__', False):
            logging.root.removeHandler(hdlr)
            break

    if logging.root.handlers:
        return

    cfg = config.load_from_env()
    log_level = cfg.log_level

    log_file = cfg.log_file
    if log_file is None:
        log_dir = ROOT_DIR / 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = log_dir / 'duty.log'

    handlers = []
    if log_file:
        handlers.append(
            logging.handlers.RotatingFileHandler(
                log_file,
                backupCount=1,
                maxBytes=8 * 1024 * 1024,
            )
        )
    if cfg.log_stdout:
        handlers.append(logging.StreamHandler(sys.stdout))

    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)s] (%(name)s) %(message)s',
        '%d.%m.%Y %H:%M:%S'
    )

    logging.root.setLevel(log_level)
    for hdlr in handlers:
        hdlr.setFormatter(formatter)
        logging.root.addHandler(hdlr)


def dev_run():
    import argparse

    parser = argparse.ArgumentParser(
        description='Run app with Flask built-in development server'
    )
    parser.add_argument('--port', default='5000')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    try:
        port = int(args.port)
    except ValueError:
        port = -1

    if not (1 <= port <= 65536):
        raise ValueError('--port should be an integer in range from 1 to 65536')

    create_app().run(host=args.host, port=port, debug=args.debug)


configure_logging()

if __name__ == "__main__":
    dev_run()
