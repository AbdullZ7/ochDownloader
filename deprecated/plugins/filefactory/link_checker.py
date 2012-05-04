import urllib2
import urllib
import httplib
import socket
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core.network.connection import URLOpen, URLClose #leer/abrir urls.
from core.misc import html_entities_parser #(html entities and numerics parser)

import core.cons as cons

BASE_URL = "http://www.filefactory.com"


class LinkChecker:
    """"""
    #sin constructor
    def check(self, link):
        """"""
        name = "Unknown"
        size = 0
        status_msg = None
        link_status = cons.LINK_ERROR
        
        try:
            #strip file name
            tmp = link.split("/file/")[1].split("/")[0]
            link = "%s/file/%s" % (BASE_URL, tmp)
            link_quoted = urllib.quote_plus(link)
            with URLClose(URLOpen().open("http://www.filefactory.com/tool/links.php?func=links&links=" + link_quoted, time_out=10)) as s:
                alive = False
                for line in s:
                    if 'Available' in line:
                        alive = True
                    elif alive:
                        if 'class="metadata"' in line:
                            name = line.split('class="metadata">')[-1].split('</div>')[0].split('/')[-1].strip()
                            name = html_entities_parser(name)
                            s.next()
                            size_list = s.next().split("<td>")[-1].split("</td>")[0].split(" ")
                            #size = "".join(size_list)
                            size = int(float(size_list[0]))
                            link_status = cons.LINK_ALIVE
                            break
            if link_status != cons.LINK_ALIVE:
                link_status = cons.LINK_DEAD
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            pass
        except Exception as err:
            status_msg = "Error: {0}".format(err)
            logger.exception(err)
        
        return link_status, name, size, status_msg
        
        
if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://www.filefactory.com/file/cdfca39/n/BackUpm985m_TeBvr_11_AdiT720p.part05.rar")
