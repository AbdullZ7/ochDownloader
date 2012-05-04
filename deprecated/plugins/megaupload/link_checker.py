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
            id = link.split("d=")[-1].strip()
            if "&" in id:
                id = id.split("&")[0]
            #TODO: enviar cookie.
            with URLClose(URLOpen().open("http://www.megaupload.com/mgr_linkcheck.php", form=urllib.urlencode({"id0": id}))) as s: #urllib.urlencode = diccionario para hacer POST. http://www.megaupload.com/mgr_linkcheck.php&id0=id
                tmp = s.read().split("&") #returns a list.
                if len(tmp) > 4:
                    name = "&".join(tmp[5:]).split("n=")[1]
                    size = int(tmp[3].split("s=")[1])
                    link_status = cons.LINK_ALIVE
                elif tmp[2] == 'id0=3': #id0=1 dead, id0=3 unavailable, id0=0 alive
                    #name = "Unknown"
                    #size = None
                    link_status = cons.LINK_UNAVAILABLE
                    status_msg = "Temporarily Unavailable. You can add the file anyway (it will be downloaded later)" #not used, yet.
                else:
                    link_status = cons.LINK_DEAD
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            status_msg = "Error: {0}".format(err)
            pass
            #if isinstance(err.reason, socket.timeout):
                #break
        except Exception, err:
            logger.exception(err)
        return link_status, name, size, status_msg



if __name__ == "__main__":
    #test
    #name, size = LinkChecker().check("http://www.megaupload.com/?d=XVIJ051I") #dead
    print LinkChecker().check("http://www.megaupload.com/?d=C4FQ04TZ")
