import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLClose, request
#from core.misc import html_entities_parser #(html entities and numerics parser)

import core.cons as cons
import core.misc as misc


class LinkChecker:
    """"""
    #sin constructor
    def check(self, link):
        """"""
        name = cons.UNKNOWN
        size = 0
        status_msg = None
        link_status = cons.LINK_ERROR
        #for retry_count in range(RETRIES):
        try:
            with URLClose(request.get(link)) as s:
                for line in s:
                    if 'name="description"' in line:
                        name = line.split('content="')[-1].split(" | Free file hosting")[0]
                        name = misc.html_entities_parser(name)
                    elif "File Size:</b>" in line:
                        tmp = line.split("</b>")[-1].split("</div>")[0].strip()
                        unit = tmp[-2:]
                        size = float(tmp[:-2])
                        #convert size to bytes.
                        if unit == "KB":
                            size = size * 1024
                        elif unit == "MB":
                            size = size * 1024 * 1024
                        elif unit == "GB":
                            size = size * 1024 * 1024 * 1024
                        break
            if size:
                link_status = cons.LINK_ALIVE
            else:
                link_status, name, size = cons.LINK_DEAD, cons.UNKNOWN, 0
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            status_msg = "Error: {0}".format(err)
        except Exception as err:
            name, size = cons.UNKNOWN, 0
            logger.exception(err)
        
        return link_status, name, size, status_msg



if __name__ == "__main__":
    pass