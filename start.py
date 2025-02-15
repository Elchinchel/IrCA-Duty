import logging.config
import logging.handlers
import os

from duty import config, create_app
from duty.utils.misc import ROOT_DIR


def configure_logging():
    is_dev_env = (os.getenv('FLASK_ENV') == 'development')
    log_level = config.load_from_env().log_level

    log_dir = ROOT_DIR / 'logs'
    os.makedirs(log_dir, exist_ok=True)

    handlers: list = [
        logging.handlers.RotatingFileHandler(
            log_dir / 'duty.log',
            backupCount=1,
            maxBytes=8 * 1024 * 1024,
        )
    ]
    if is_dev_env:
        handlers.append(logging.StreamHandler())

    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
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
