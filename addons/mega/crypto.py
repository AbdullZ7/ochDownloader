from Crypto.Cipher import AES

import base64
import json
import struct
import logging


def base64urldecode(data):
    data += '=='[(2 - len(data) * 3) % 4:]
    for search, replace in (('-', '+'), ('_', '/'), (',', '')):
        data = data.replace(search, replace)
    return base64.b64decode(data)


def str_to_a32(b):
    if len(b) % 4:  # Add padding, we need a string with a length multiple of 4
        b += '\0' * (4 - len(b) % 4)
    return struct.unpack('>%dI' % (len(b) / 4), b)


def aes_cbc_decrypt(data, key):
    decryptor = AES.new(key, AES.MODE_CBC, '\0' * 16)
    return decryptor.decrypt(data)


def a32_to_str(a):
    return struct.pack('>%dI' % len(a), *a)


def base64_to_a32(s):
    return str_to_a32(base64urldecode(s))


def dec_attr(attr, key):
    attr = aes_cbc_decrypt(attr, a32_to_str(key))
    attr += "asd"  # put some unwanted chars, just in case there is none
    attr = '"}'.join(attr.split('"}')[:-1])  # remove unwanted chars "{...} asd"
    attr += '"}'
    return json.loads(attr[4:])


def get_chunks(size):
    chunks = {}
    p = pp = 0
    i = 1

    while i <= 8 and p < size - i * 0x20000:
        chunks[p] = i * 0x20000
        pp = p
        p += chunks[p]
        i += 1

    while p < size:
        chunks[p] = 0x100000
        pp = p
        p += chunks[p]

    chunks[pp] = size - pp
    if not chunks[pp]:
        del chunks[pp]

    return chunks


def aes_cbc_encrypt(data, key):
    encryptor = AES.new(key, AES.MODE_CBC, '\0' * 16)
    return encryptor.encrypt(data)


def aes_cbc_encrypt_a32(data, key):
    return str_to_a32(aes_cbc_encrypt(a32_to_str(data), a32_to_str(key)))