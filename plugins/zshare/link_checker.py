import urllib2
import urllib
import httplib
import socket
import logging
#logger = logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLOpen, URLClose #leer/abrir urls.
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
            if "/video/" in link:
                link = link.replace("/video/", "/download/")
            elif "/audio/" in link:
                link = link.replace("/audio/", "/download/")
            elif "/image/" in link:
                link = link.replace("/image/", "/download/")
            with URLClose(URLOpen().open(link)) as s:
                for line in s:
                    if 'File Name:' in line:
                        name = s.next().split("</font>")[0].split('>')[-1].strip()
                        name = misc.html_entities_parser(name)
                    elif 'File Size:' in line:
                        tmp = line.split("</font>")[0].split('>')[-1].strip()
                        unit = tmp[-2:].strip()
                        size = float(tmp[:-2])
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
        except Exception as err:
            name, size = cons.UNKNOWN, 0
            logger.exception(err)

        return link_status, name, size, status_msg


if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://www.zshare.net/download/676959526535015c")
