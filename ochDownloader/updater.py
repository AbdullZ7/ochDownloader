import os
import sys
import logging

logger = logging.getLogger(__name__)

APP_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "")
LOG_NAME = "updater_error.log"
LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
LOG_FILE = os.path.join(APP_PATH, LOG_NAME)


def setup_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)-7s %(name)s: %(message)s")
    fh = logging.FileHandler(LOG_FILE, mode="wb")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger().addHandler(fh)


def check_active_app():
    # checks if the app is still running by using sockets
    pass


def uncompress():
    # uncompress the new zipped app version into a temp folder
    pass


def move_files():
    # move the new files, overwriting the old ones
    pass


def clean_up():
    # remove .pyc files, zipped app, and temp folder
    pass


if __name__ == "__main__":
    setup_logger()
    uncompress()
    clean_up()
    move_files()
    sys.exit()