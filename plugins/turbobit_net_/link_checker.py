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
        api = "http://turbobit.net/linkchecker/csv"
        form = urllib.urlencode({"links_to_check": link, })
        try:
            with URLClose(URLOpen().open(api, form)) as s:
                line = s.read()
                active = int(line.split(", ")[-1].strip())
                if active:
                    link_status = cons.LINK_ALIVE
                    with URLClose(URLOpen().open(link)) as s:
                        for line in s:
                            if 'class="download-file' in line:
                                s.next()
                                line_ = s.next()
                                name = line_.split("'>")[-1].split("<")[0]
                                tmp = line_.split('>')[-1].strip()
                                size = float(tmp.split("(")[-1].split(",")[0])
                                unit = tmp.split(" ")[-1].split(")")[0]
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
    print LinkChecker().check("http://turbobit.net/cx1l0mzyzy5e.html")
