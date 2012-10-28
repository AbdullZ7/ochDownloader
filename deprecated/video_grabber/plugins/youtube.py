import os, urllib2, httplib, socket, urllib
from urlparse import parse_qs

from base_plugin import BasePlugin


class Grab(BasePlugin):
    """
    Mostly taken from youtube-dl
    https://github.com/rg3/youtube-dl
    """
    video_extensions = {
        '13': '3gp',
        '17': 'mp4',
        '18': 'mp4',
        '22': 'mp4',
        '37': 'mp4',
        '38': 'video',
        '43': 'webm',
        '44': 'webm',
        '45': 'webm',
        '46': 'webm',
    }

    video_dimensions = {
        '5': '400x240',
        '6': '???',
        '13': '???',
        '17': '176x144',
        '18': '640x360',
        '22': '1280x720',
        '34': '640x360',
        '35': '854x480',
        '37': '1920x1080',
        '38': '4096x3072',
        '43': '640x360',
        '44': '854x480',
        '45': '1280x720',
        '46': '1920x1080',
    }

    def __init__(self, *args, **kwargs):
        BasePlugin.__init__(self, *args, **kwargs)

    def parse(self, link):
        video_id = link.split("=")[-1].split("&")[0]

        for el_type in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
            video_info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en'
                              % (video_id, el_type))
            request = urllib2.Request(video_info_url)
            video_info_webpage = urllib2.urlopen(request).read()
            video_info = parse_qs(video_info_webpage)
            if 'token' in video_info:
                #print video_info
                #print video_info_url
                break

        format_list = ['38', '37', '46', '22', '45', '35', '44', '34', '18', '43', '6', '5', '17', '13']

        url_data_strs = video_info['url_encoded_fmt_stream_map'][0].split(',')
        url_data = [parse_qs(uds) for uds in url_data_strs]
        url_data = filter(lambda ud: 'itag' in ud and 'url' in ud, url_data)
        url_map = dict((ud['itag'][0], ud['url'][0] + '&signature=' + ud['sig'][0]) for ud in url_data)

        existing_formats = [x for x in format_list if x in url_map]
        #print existing_formats
        url = url_map[existing_formats[1]]
        #print url

        #self.source = urllib2.urlopen(url)
        #print source.headers #Content-Type: video/webm

        video_title = urllib.unquote_plus(video_info['title'][0])
        video_title = video_title.decode('utf-8')

        self.video_list.append((video_title, url))

        #print video_title