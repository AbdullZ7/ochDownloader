import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLClose, request

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
            with URLClose(request.get(link)) as s:
                alive = False
                for line in s:
                    if '<title>' in line:
                        tmp = line.split("-")
                        if len(tmp) > 2:
                            tmp_name = link.split("/files/")[-1].split("/")
                            if len(tmp_name) == 2:
                                name = tmp_name[-1].rstrip(".html") #complete name
                            else:
                                name = tmp[0].strip().split(" ")[-1] #shorted name, ie: filenam...part1.rar
                            link_status = cons.LINK_ALIVE
                            alive = True
                        else:
                            link_status = cons.LINK_DEAD
                    elif alive and "<h1>" in line and name in line:
                        tmp = line.split("-")[-1].strip()
                        unit = tmp.split(" ")[-1] #
                        size = float(tmp.split(" ")[0])
                        #convert size to bytes.
                        if "kb" in unit.lower():
                            size = size * 1024
                        elif "mb" in unit.lower():
                            size = size * 1024 * 1024
                        elif "gb" in unit.lower():
                            size = size * 1024 * 1024 * 1024
                        break
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            status_msg = "Error: {0}".format(err)
        except Exception as err:
            status_msg = "Error: {0}".format(err)
            logger.exception(err)

        return link_status, name, size, status_msg


if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://bitshare.com/files/mklpswlg/Alcatraz.S01E04.720p.HDTV.X264-DIMENSION.mkv.html")
