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
            with URLClose(URLOpen().open(link)) as s:
                for line in s:
                    if '<b title="' in line:
                        name = line.split('<b title="')[-1].split('"')[0]
                        link_status = cons.LINK_ALIVE
                        tmp = s.next().split("<b>")[-1].split("<")[0]
                        size = float(tmp.split("&")[0])
                        unit = tmp[-2:]
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
            status_msg = "Error: {0}".format(err)
        except Exception as err:
            status_msg = "Error: {0}".format(err)
            logger.exception(err)

        return link_status, name, size, status_msg


if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://depositfiles.com/files/am4vowogf/Spartacus.S02E01.720p.HDTV.X264-DIMENSION.mkv")
