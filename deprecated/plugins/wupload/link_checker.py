import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLOpen, URLClose #leer/abrir urls.

import core.cons as cons


class LinkChecker:
    """
    http://api.wupload.com/
    """
    #sin constructor
    def check(self, link):
        """"""
        name = "Unknown"
        size = 0
        status_msg = None
        link_status = cons.LINK_ERROR
        #for retry_count in range(RETRIES):
        try:
            file_id = link.split("/file/")[1].split("/")[0]
            with URLClose(URLOpen().open("http://api.wupload.com/link?method=getInfo&ids=" + file_id, time_out=10)) as s:
                response = s.read()
                if '"filename"' in response:
                    name = response.split('"filename":"')[-1].split('"')[0]
                    link_status = cons.LINK_ALIVE
                    tmp =response.split('"size":')[-1].split(',')[0]
                    size = int(tmp)
                else:
                    link_status = cons.LINK_DEAD
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            status_msg = "Error: {0}".format(err)
        except Exception as err:
            status_msg = "Error: {0}".format(err)
            logger.exception(err)

        return link_status, name, size, status_msg


if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://www.wupload.com/file/113398493")
