import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLClose, request

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
            with URLClose(request.get(link)) as s:
                for line in s:
                    if 'id="filename"' in line:
                        name = line.split('id="filename">')[-1].split("<")[0]
                        name = name.replace("&hellip;", "...")
                        link_status = cons.LINK_ALIVE
                        tmp = s.next().split('">')[-1].split("<")[0]
                        size = float(tmp.split(" ")[0].split(",")[0])
                        unit = tmp.split(" ")[-1]
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
    print LinkChecker().check("http://uploaded.to/file/fdn987ab/Mrs.Browns.Boys.S02E06.HDTV.XviD-TLA.avi")



