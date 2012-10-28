import urllib
import logging
logger = logging.getLogger(__name__)
from urlparse import parse_qs

import core.cons as cons
from core.network.connection import URLClose, request


class LinkChecker:
    """"""
    def check(self, link):
        """"""
        video_id = link.split("=")[-1].split("&")[0]

        for el_type in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
            video_info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en'
                              % (video_id, el_type))
            with URLClose(request.get(video_info_url)) as s:
                video_info = parse_qs(s.read())
                if 'token' in video_info:
                    #print video_info
                    #print video_info_url
                    break

        video_title = urllib.unquote_plus(video_info['title'][0])
        video_title = video_title.decode('utf-8')

        return cons.LINK_ALIVE, video_title, 0, None
