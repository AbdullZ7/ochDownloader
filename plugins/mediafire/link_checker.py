import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLOpen, URLClose #leer/abrir urls.
#from core.misc import html_entities_parser #(html entities and numerics parser)

import core.cons as cons


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
            with URLClose(URLOpen().open(link)) as s:
                found = False
                for line in s:
                    if 'download_file_title">' in line:
                        found = True
                        link_status = cons.LINK_ALIVE
                        name = line.split('download_file_title">')[-1].split('<')[0].strip()
                        tmp = line.split('class="download_link')[1].split('<span>(')[-1].split(')')[0].strip()
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
                if not found:
                    link_status = cons.LINK_DEAD
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            status_msg = "Error: {0}".format(err)
        except Exception, err:
            logger.exception(err)
        return link_status, name, size, status_msg
