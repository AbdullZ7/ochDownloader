import pickle
import logging
logger = logging.getLogger(__name__)

#Libs
import cons


class SessionParser:
    """"""
    def save(self, download_list):
        """"""
        try:
            with open(cons.SESSION_FILE, "wb", cons.FILE_BUFSIZE) as fh:
                pickle.dump(download_list, fh, pickle.HIGHEST_PROTOCOL)
        except (EnvironmentError, pickle.PicklingError) as err:
            logger.warning("Can't save the session: {0}".format(err))
    
    def load(self):
        """"""
        try:
            with open(cons.SESSION_FILE, "rb", cons.FILE_BUFSIZE) as fh:
                return pickle.load(fh)
        except (EnvironmentError, pickle.UnpicklingError) as err:
            logger.warning(err)
        except EOFError as err:
            logger.warning("End of file error: {0}".format(err))
        return []
