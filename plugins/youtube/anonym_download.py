#python libs
import urllib
import logging
logger = logging.getLogger(__name__)
from urlparse import parse_qs
from collections import OrderedDict

#Libs
from core.plugin.base import PluginBase

from addons.video_quality_choice.choice import QualityChoice


class PluginDownload(PluginBase):
    """
    Mostly taken from youtube-dl
    https://github.com/rg3/youtube-dl
    """
    # YouTube quality and codecs id map.
    # source: http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs
    video_extensions = {
        '5': 'flv',
        '6': 'flv',
        '13': '3gp',
        '17': 'mp4',
        '18': 'mp4',
        '22': 'mp4',
        '34': 'flv',
        '35': 'flv',
        '36': 'flv',
        '37': 'mp4',
        '38': 'mp4',
        '43': 'webm',
        '44': 'webm',
        '45': 'webm',
        '82': 'mp4',
        '83': 'mp4',
        '84': 'mp4',
        '85': 'mp4',
        '100': 'webm',
        '101': 'webm',
        '102': 'webm',
        '120': 'flv',
        }

    video_dimensions = [
        ('38', '3072p (.mp4)'),
        ('37', '1080p (.mp4)'),
        ('46', '1080p (.webm)'),
        ('22', '720p (.mp4)'),
        ('45', '720p (.webm)'),
        ('44', '480p (.webm)'),
        ('35', '480p (.flv)'),
        ('18', '360p (.mp4)'),
        ('43', '360p (.webm)'),
        ('34', '360p (.flv)'),
        ('6', '270p (.flv)'),
        ('5', '240p (.flv)'),
        ('17', '144p (.mp4)'),
        ('13', '??? (.3gp)'),

        ('84', '720p (.mp4) - 3D'),
        ('102', '720p (.webm) - 3D'),
        ('85', '520p (.mp4) - 3D'),
        ('82', '360p (.mp4) - 3D'),
        ('100', '360p (.webm) - 3D -'),
        ('101', '360p (.webm) - 3D'),
        ('83', '240p (.mp4) - 3D'),
        ('120', '720p (.flv) - Streaming'),
        ]

    def parse(self):
        video_id = self.link.split("&")[0].split("=")[-1]

        for el_type in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
            video_info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en'
                              % (video_id, el_type))
            video_info_webpage = self.get_page(video_info_url)
            video_info = parse_qs(video_info_webpage)
            if 'token' in video_info:
                #print video_info
                #print video_info_url
                break

        url_data_strs = video_info['url_encoded_fmt_stream_map'][0].split(',')
        url_data = [parse_qs(uds) for uds in url_data_strs]
        url_data = filter(lambda ud: 'itag' in ud and 'url' in ud, url_data)
        url_map = dict((ud['itag'][0], ud['url'][0] + '&signature=' + ud['sig'][0]) for ud in url_data)

        #existing_formats = [x for x in format_list if x in url_map]
        #print existing_formats

        video_title = urllib.unquote_plus(video_info['title'][0])

        if self.video_quality is None:
            choices_list = [quality for id_, quality in self.video_dimensions if id_ in url_map]
            c = QualityChoice(video_title, choices_list, self.wait_func)
            c.run_choice()
            choices_dict = {quality: id_ for id_, quality in self.video_dimensions}
            self.video_quality = choices_dict[c.solution]

        url = url_map[self.video_quality]
        #print url

        source = self.get_page(url, close=False)
        #print source.headers #Content-Type: video/webm

        self.save_as = '.'.join((video_title, self.video_extensions[self.video_quality]))
        self.source = source


if __name__ == "__main__":
    pass

