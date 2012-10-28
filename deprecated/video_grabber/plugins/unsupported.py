import urllib
import re

from base_plugin import BasePlugin
from core.network.connection import request


class Grab(BasePlugin):
    """
    Mostly taken from youtube-dl
    https://github.com/rg3/youtube-dl
    """
    def __init__(self, *args, **kwargs):
        BasePlugin.__init__(self, *args, **kwargs)

    def parse(self, link):
        #TODO: use findall.
        source = request.get(link).read(1024 * 1024)

        #Start with something easy: JW Player in SWFObject
        mobj = re.search(r'flashvars: [\'"](?:.*&)?file=(http[^\'"&]*)', source)
        if mobj is None:
            #Broaden the search a little bit
            mobj = re.search(r'[^A-Za-z0-9]?(?:file|source)=(http[^\'"&]*)', source)
        if mobj is None:
            mobj = re.search(r'(?:file|source)[\s]+src=["|\'](http[^\'"&]*)', source)
        if mobj is None:
            #nothing found
            return

        # It's possible that one of the regexes
        # matched, but returned an empty group:
        if mobj.group(1) is None:
            #nothing found
            return

        video_url = urllib.unquote(mobj.group(1))
        self.video_list.append((None, video_url))
