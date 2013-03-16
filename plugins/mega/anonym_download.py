import json
import urllib2

from core.plugin.base import PluginBase, BUFF_SZ

from addons.mega import crypto

# http://mega.co.cz/#!file_id!decrypted_key


class PluginDownload(PluginBase):
    def parse(self):
        url_parts = self.link.split("!")
        #if len(url_parts) != 3:
            #raise missing File Key
        file_id, file_key = url_parts[1], url_parts[2]
        key = crypto.base64_to_a32(file_key)
        k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
        #iv = key[4:6] + (0, 0)
        #meta_mac = key[6:8]

        url = 'https://g.api.mega.co.nz/cs?id=1&amp;sid='

        file = self.get_file(url, file_id)
        dl_url = file['g']
        # size = file['s'] # KB
        attributes = crypto.base64urldecode(file['at'])
        attributes = crypto.dec_attr(attributes, k)

        self.save_as = attributes['n']
        self.source = self.get_page(dl_url, close=False)

    def request(self, url, data):
        # json request
        # headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        return urllib2.urlopen(url, data).read(BUFF_SZ)

    def get_file(self, url, file_id):
        response = self.request(url, json.dumps([{'a': 'g', 'g': 1, 'p': file_id}, ]))
        return json.loads(response)[0]


if __name__ == "__main__":
    pass