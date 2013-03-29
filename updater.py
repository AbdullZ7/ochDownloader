import os
import sys
import logging

APP_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "")
LOG_NAME = "updater_error.log"
LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
LOG_FILE = os.path.join(APP_PATH, LOG_NAME)


class Updater:
    # Work in progress...
    def __init__(self):
        self.setup_logger()
        self.logger = logging.getLogger(self.__class__.__name__)

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG,
                            format="%(levelname)-7s %(name)s: %(message)s")
        fh = logging.FileHandler(LOG_FILE, mode="wb")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger("").addHandler(fh)

    def uncompress(self):
        # uncompress the new zipped app version in to a temp folder
        pass

    def move_files(self):
        # move the new files, overwriting the old ones
        pass

    def clean_up(self):
        # remove .pyc files, zipped app, and temp folder
        pass


if __name__ == "__main__":
    updater = Updater()
    try:
        updater.uncompress()
        updater.move_files()
        updater.clean_up()
    except Exception as err:
        updater.logger(err)
        sys.exit(str(err))
    else:
        sys.exit(0)