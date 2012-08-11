# -*- encoding: utf-8 -*-
# binux<17175297.hk@gmail.com>

import os
import struct
import hashlib

def parse_fid(fid):
    cid, size, gcid = struct.unpack("<20sq20s", fid.decode("base64"))
    return cid.encode("hex").upper(), size, gcid.encode("hex").upper()

def gen_fid(cid, size, gcid):
    return struct.pack("<20sq20s", cid.decode("hex"), size, gcid.decode("hex")).encode("base64").replace("\n", "")

def gcid_hash_file(path):
    h = hashlib.sha1()
    size = os.path.getsize(path)
    psize = 0x40000
    while size / psize > 0x200:
        psize = psize << 1
    with open(path, 'rb') as stream:
        data = stream.read(psize)
        while data:
            h.update(hashlib.sha1(data).digest())
            data = stream.read(psize)
    return h.hexdigest().upper()

def cid_hash_file(path):
    h = hashlib.sha1()
    size = os.path.getsize(path)
    with open(path, 'rb') as stream:
        if size < 0xF000:
            h.update(stream.read())
        else:
            h.update(stream.read(0x5000))
            stream.seek(size/3)
            h.update(stream.read(0x5000))
            stream.seek(size-0x5000)
            h.update(stream.read(0x5000))
    return h.hexdigest().upper()

thunder_filename_mask = "6131E45F00000000".decode("hex")
def thunder_filename_encode(filename, encoding="gbk"):
    if isinstance(filename, unicode):
        filename = filename.encode(encoding)
    result = ["01", ]
    for i, word in enumerate(filename):
        mask = thunder_filename_mask[i%len(thunder_filename_mask)]
        result.append("%02X" % (ord(word)^ord(mask)))
    while len(result) % 8 != 1:
        mask = thunder_filename_mask[len(result)%len(thunder_filename_mask)-1]
        result.append("%02X" % ord(mask))
    return "".join(result)

def thunder_filename_decode(code, encoding="gbk"):
    assert code.startswith("01")
    result = []
    for i, word in enumerate(code[2:].decode("hex")):
        mask = thunder_filename_mask[i%len(thunder_filename_mask)]
        result.append(chr(ord(word)^ord(mask)))
    result = "".join(result).rstrip("\0")
    return result.decode(encoding)

def encode_thunder(url):
    return "thunder://"+("AA"+url+"ZZ").encode("base64").replace("\n", "")

def decode_thunder(url):
    assert url.lower().startswith("thunder://"), "should startswith 'thunder://'"
    url = url[10:].decode("base64")
    assert url.startswith("AA") and url.endswith("ZZ"), "unknow format"
    return url[2:-2]

def encode_flashget(url):
    return "Flashget://"+("[FLASHGET]"+url+"[FLASHGET]").encode("base64").replace("\n", "")

def decode_flashget(url):
    assert url.lower().startswith("flashget://"), "should startswith 'Flashget://'"
    url = url[11:].decode("base64")
    assert url.startswith("[FLASHGET]") and url.endswith("[FLASHGET]"), "unknow format"
    return url[10:-10]

def encode_qqdl(url):
    return "qqdl://"+url.encode("base64").replace("\n", "")

def decode_qqdl(url):
    assert url.lower().startswith("qqdl://"), "should startswith 'qqdl://'"
    return url[7:].decode("base64")

def url_unmask(url):
    url_lower = url.lower()
    try:
        if url_lower.startswith("thunder://"):
            return decode_thunder(url)
        elif url_lower.startswith("flashget://"):
            return decode_flashget(url)
        elif url_lower.startswith("qqdl://"):
            return decode_qqdl(url)
        else:
            return url
    except:
        return url
