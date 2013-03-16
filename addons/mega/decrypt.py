from Crypto.Cipher import AES
from Crypto.Util import Counter

import crypto


def getfile2(download_item):
    url_parts = download_item.link.split("!")
    #if len(url_parts) != 3:
        #raise missing File Key
    file_id, file_key = url_parts[1], url_parts[2]
    key = crypto.base64_to_a32(file_key)
    k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
    iv = key[4:6] + (0, 0)
    meta_mac = key[6:8]

    infile = open('myfile.part', 'rb')
    outfile = open('myfile', 'wb')
    decryptor = AES.new(crypto.a32_to_str(k), AES.MODE_CTR, counter=Counter.new(128, initial_value = ((iv[0] << 32) + iv[1]) << 64))

    size = None # get_file_size

    file_mac = [0, 0, 0, 0]
    for chunk_start, chunk_size in sorted(crypto.get_chunks(size).items()):
        chunk = infile.read(chunk_size)
        chunk = decryptor.decrypt(chunk)
        outfile.write(chunk)

        chunk_mac = [iv[0], iv[1], iv[0], iv[1]]
        for i in xrange(0, len(chunk), 16):
            block = chunk[i:i+16]
            if len(block) % 16:
                block += '\0' * (16 - (len(block) % 16))
            block = crypto.str_to_a32(block)
            chunk_mac = [chunk_mac[0] ^ block[0], chunk_mac[1] ^ block[1], chunk_mac[2] ^ block[2], chunk_mac[3] ^ block[3]]
            chunk_mac = crypto.aes_cbc_encrypt_a32(chunk_mac, k)

        file_mac = [file_mac[0] ^ chunk_mac[0], file_mac[1] ^ chunk_mac[1], file_mac[2] ^ chunk_mac[2], file_mac[3] ^ chunk_mac[3]]
        file_mac = crypto.aes_cbc_encrypt_a32(file_mac, k)

    if (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]) != meta_mac:
        print "MAC mismatch"
    else:
        print "MAC OK"