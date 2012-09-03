import pickle #permite escribir diccionarios, listas, etc en archivos, preservando el tipo.
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import cons


class SessionParser:
    """"""
    def save(self, list_downloads):
        """"""
        try:
            with open(cons.SESSION_FILE, "wb", cons.FILE_BUFSIZE) as fh: #w reemplaza el contenido del archivo.
                pickle.dump(list_downloads, fh, pickle.HIGHEST_PROTOCOL)
        except (EnvironmentError, pickle.PicklingError) as err:
            logger.warning("Can't save the session: {0}".format(err))
    
    def load(self):
        """"""
        result = []
        try:
            with open(cons.SESSION_FILE, "rb", cons.FILE_BUFSIZE) as fh:
                result = pickle.load(fh)
        except (EnvironmentError, pickle.UnpicklingError) as err:
            logger.warning(err)
        except EOFError as err:
            logger.warning("End of file error: {0}".format(err))
        return result
