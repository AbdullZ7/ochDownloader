import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLOpen, URLClose #leer/abrir urls.

import core.cons as cons


class LinkChecker:
    """"""
    #sin constructor
    def check(self, link):
        """"""
        name = "Unknown"
        size = 0
        status_msg = None
        link_status = cons.LINK_ERROR
        #for retry_count in range(RETRIES):
        try:
            with URLClose(URLOpen().open(link, time_out=10)) as s:
                for line in s:
                    if '"panel file_download"' in line:
                        s.next()
                        name = s.next().split(">")[1].split("<")[0]
                        link_status = cons.LINK_ALIVE
                        s.next()
                        s.next()
                        tmp = s.next().split("<strong>")[1].split("<")[0]
                        unit = tmp[-2:] #
                        size = float(tmp[:-2])
                        #convert size to bytes.
                        if unit.lower() == "kb":
                            size = size * 1024
                        elif unit.lower() == "mb":
                            size = size * 1024 * 1024
                        elif unit.lower() == "gb":
                            size = size * 1024 * 1024 * 1024
                        break
                if link_status != cons.LINK_ALIVE:
                    link_status = cons.LINK_DEAD
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            pass
        except Exception, err:
            status_msg = "Error: {0}".format(err)
            logger.exception(err)

        return link_status, name, size, status_msg


if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://www.megaupload.com/?d=C4FQ04TZ")
