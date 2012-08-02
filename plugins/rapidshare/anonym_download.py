#python libs
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from core.plugins_core import PluginsCore


class PluginDownload(PluginsCore):
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)

    def parse(self):
        link = self.link
        id_ = self.link.split("/")[-2]
        file_name = self.link.split("/")[-1]
        api_url = "http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=download&fileid=" + id_ + "&filename=" + file_name
        page = self.get_page(api_url)
        m_pattern = 'DL:(?P<subhost>[^,]+),(?P<dlauth>[^,]+),'
        m = self.get_match(m_pattern, page)
        if m is not None:
            self.countdown('DL:[^,]+,[^,]+,(?P<count>[^,]+)', page, 600, 60)
            link = "http://{host}/cgi-bin/rsapi.cgi?sub=download&fileid={id}&filename={filename}&dlauth={auth}".format(host=m.group('subhost'), id=id_, filename=file_name, auth=m.group('dlauth'))
            #resume fix
            self.content_range = None
            self.source = self.get_page(link, close=False)
        else: #link not found
            pass


if __name__ == "__main__":
    import re
    page = 'DL:rs823p10.rapidshare.com,E95A2D53D3A24E52BF5CD3EB3E63033D6EC3637DD63578CED8793CFEFCA074782186FE1E1582E38DB972ED3547FC3C8A00727C572469C984DDA2BEE2079A8B4378DF757633712B4ED6753712B281238597F0143B4B6D50423A888898116A35189878E90CD5A0D5CEAEC7B0D5FFB55241,0,5B79FA9ED187AE4AD8D0F38FB82157E9'
    pattern = 'DL:.*?,.*?,(?P<count>.*)'
    m = re.search(pattern, page, re.S)
    if m is not None:
        print m.groups()
    else:
        print 'not found'
    
