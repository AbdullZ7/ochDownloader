import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLClose, request
from core.utils import html_entities_parser #(html entities and numerics parser)

import core.cons as cons


class LinkChecker:
    """"""
    #sin constructor
    def check(self, link):
        """
        Rapidshare api: http://images.rapidshare.com/apidoc.txt
        
        Status integer, which can have the following numeric values:
            0=File not found
            1=File OK
            3=Server down
            4=File marked as illegal
            5=Direct download
        """
        name = "Unknown"
        size = 0
        status_msg = None
        link_status = cons.LINK_ERROR
        
        FILE_ID, FILE_NAME, SIZE, SERVER_ID, STATUS, SHORT_HOST, MD5 = range(7)
        
        try:
            id = link.split("/")[-2]
            file_name = link.split("/")[-1]
            #http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=subroutine&files=value1&filenames=value2
            with URLClose(request.post("http://api.rapidshare.com/cgi-bin/rsapi.cgi", data={"sub": "checkfiles", "files": id, "filenames": file_name}, timeout=10)) as s:
                tmp = s.read().split(",")
                #print tmp
                name = tmp[FILE_NAME]
                size = int(tmp[SIZE])
                if int(tmp[STATUS]) in (1, 5): #alive or direct download
                    link_status = cons.LINK_ALIVE
                elif int(tmp[STATUS]) == 3: #server down
                    link_status = cons.LINK_UNAVAILABLE
                else:
                    link_status = cons.LINK_DEAD
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            status_msg = "Error: {0}".format(err)
        except Exception as err:
            status_msg = "Error: {0}".format(err)
            logger.exception(err)
        return link_status, name, size, status_msg


if __name__ == "__main__":
    pass
    
