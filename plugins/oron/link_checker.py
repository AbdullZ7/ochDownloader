import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLClose, request

import core.cons as cons
import core.misc as misc


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
            with URLClose(request.get(link, time_out=10)) as s:
                for line in s:
                    if 'class="f_arial f_14px"' in line:
                        name = line.split('"f_arial f_14px">')[-1].split('<')[0].strip()
                        name = misc.html_entities_parser(name)
                        tmp = s.next().split(":")[-1].split("<")[0].strip()
                        unit = tmp.split(" ")[-1].strip()
                        size = float(tmp.split(" ")[0].strip())
                        #convert size to bytes.
                        if unit.lower() == "kb":
                            size = size * 1024
                        elif unit.lower() == "mb":
                            size = size * 1024 * 1024
                        elif unit.lower() == "gb":
                            size = size * 1024 * 1024 * 1024
                        break
            if size:
                link_status = cons.LINK_ALIVE
            else:
                link_status, name, size = cons.LINK_DEAD, cons.UNKNOWN, 0
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            status_msg = "Error: {0}".format(err)
        except Exception, err:
            status_msg = "Error: {0}".format(err)
            name, size = cons.UNKNOWN, 0
            logger.exception(err)

        return link_status, name, size, status_msg


if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://www.megaupload.com/?d=C4FQ04TZ")
