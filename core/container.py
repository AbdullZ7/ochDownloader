import hashlib
import struct
import logging
logger = logging.getLogger(__name__)

try:
    from Crypto.Cipher import AES
except ImportError as err:
    logger.warning(err)
    AES = None

from core import cons


class Container:
    """"""
    def __init__(self, fileh):
        """"""
        self.__fileh = fileh #ruta + nombre de archivo
        self.__linklist = []
        self.__contrasenia = "P4$$w0RD"
        
    def get_linklist(self):
        """"""
        return self.__linklist
        
    def extract_links(self):
        """"""
        link_list = self.decodificar().split("http://") #al dividir el primero es un string vacio.
        tmp_list = []
        [tmp_list.append("".join(("http://", link)).strip()) for link in link_list if link]
        self.__linklist = tmp_list[:]
    
    def decodificar_file(self, key, chunksize=24*1024):
        """"""
        if AES is None:
            return ""

        links = ""
        
        try:
            with open(self.__fileh, 'rb', cons.FILE_BUFSIZE) as infile:
                origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
                iv = infile.read(16)
                decryptor = AES.new(key, AES.MODE_CBC, iv)

                while True:
                    chunk = infile.read(chunksize)
                    
                    if not len(chunk):
                        break
                
                    links += decryptor.decrypt(chunk)
        except EnvironmentError as err:
            logger.exception(err)
        
        return links

    def decodificar(self):
        """"""
        key = hashlib.sha256(self.__contrasenia).digest()
        return self.decodificar_file(key)
    
    

if __name__ == "__main__":
    algo = "http://algo11http://algo2http://algo3\n".strip()
    print algo.split("http://")[1:]

    
