import os
import threading
import logging
logger = logging.getLogger(__name__)

from Crypto.Cipher import AES
from Crypto.Util import Counter

import crypto

FILE_EXT = ".crypted"


class Decrypter(threading.Thread):
    def __init__(self, download_item):
        threading.Thread.__init__(self)

        self.id_item = download_item.id
        self.link = download_item.link
        self.path = download_item.path
        self.name = download_item.name
        self.status = _("Running")

    def run(self):
        try:
            self.decrypt()
        except Exception as err:
            logger.exception(err)
            self.status = "Error: %s" % str(err)
        else:
            self.status = _("Success")

    def get_out_name(self, name):
        if name.endswith(FILE_EXT):
            return name[:-len(FILE_EXT)]
        else:
            return name + ".decrypted"

    def decrypt(self):
        url_parts = self.link.split("!")
        file_id, file_key = url_parts[1], url_parts[2]

        key = crypto.base64_to_a32(file_key)
        k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
        iv = key[4:6] + (0, 0)

        file_path = os.path.join(self.path, self.name)
        size = os.path.getsize(file_path)
        out_name = self.get_out_name(self.name)
        out_file_path = os.path.join(self.path, out_name)

        decryptor = AES.new(crypto.a32_to_str(k), AES.MODE_CTR, counter=Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64))

        with open(file_path, 'rb') as fh_in:
            with open(out_file_path, 'wb') as fh_out:
                for chunk_start, chunk_size in sorted(crypto.get_chunks(size).items()):
                    chunk = fh_in.read(chunk_size)
                    chunk = decryptor.decrypt(chunk)
                    fh_out.write(chunk)

                # mac checking omitted