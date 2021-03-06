import os
import multiprocessing

from Crypto.Cipher import AES
from Crypto.Util import Counter

import crypto


class Decrypter(multiprocessing.Process):
    def __init__(self, download_item, pipe_in):
        multiprocessing.Process.__init__(self)

        self.link = download_item.link
        self.path = download_item.path
        self.name = download_item.name
        self.out_name = download_item.out_name
        self.pipe_in = pipe_in  # (err_flag, msg)

    def run(self):
        try:
            self.decrypt()
        except Exception as err:
            self.pipe_in.send((True, "Error: %s" % str(err)))
        else:
            self.pipe_in.send((False, "Success"))

    def decrypt(self):
        url_parts = self.link.split("!")
        file_id, file_key = url_parts[1], url_parts[2]

        key = crypto.base64_to_a32(file_key)
        k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
        iv = key[4:6] + (0, 0)

        file_path = os.path.join(self.path, self.name)
        size = os.path.getsize(file_path)
        out_file_path = os.path.join(self.path, self.out_name)

        decryptor = AES.new(crypto.a32_to_str(k), AES.MODE_CTR, counter=Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64))

        with open(file_path, 'rb') as fh_in:
            with open(out_file_path, 'wb') as fh_out:
                for chunk_start, chunk_size in sorted(crypto.get_chunks(size).items()):
                    chunk = fh_in.read(chunk_size)
                    chunk = decryptor.decrypt(chunk)
                    fh_out.write(chunk)

                # mac checking omitted