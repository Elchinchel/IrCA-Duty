import os
import logging
from logging.config import dictConfig

from duty import create_app
from duty.utils import ROOT_DIR


def configure_logging():
    is_dev_env = (os.getenv('FLASK_ENV') == 'development')
    log_level = logging.DEBUG if is_dev_env else logging.INFO

    handlers = {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ROOT_DIR / 'duty.log',
            'backupCount': 1,
            'maxBytes': 8 * 1024 * 1024,
            'level': log_level,
        }
    }
    if is_dev_env:
        handlers['console'] = {
            'class': 'logging.handlers.StreamHandler',
            'level': log_level
        }

    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s : %(message)s'
            }
        },
        'handlers': handlers,
        'root': {
            'level': log_level,
            'handlers': list(handlers.keys())
        }
    })


def dev_run():
    import argparse

    parser = argparse.ArgumentParser(
        description='Run service with Flask built-in development server'
    )
    parser.add_argument('--port', default='5000')
    parser.add_argument('--host', default='localhost')
    args = parser.parse_args()

    try:
        port = int(args.port)
    except ValueError:
        port = -1

    if not (1 <= port <= 65536):
        raise ValueError('--port should be an integer in range from 1 to 65536')

    create_app().run(host=args.host, port=port)


# configure_logging()

if __name__ == "__main__":
    dev_run()
