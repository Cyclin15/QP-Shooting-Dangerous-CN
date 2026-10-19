# -*- coding: utf-8 -*-
"""DX Archive v4 (DxLib) unpack/repack tools - reverse engineered.
Format:
  Whole file XOR-encrypted with 12-byte key derived from keystring (MakeKey12).
  Header 28 bytes: 'DX'(2) ver(2)=4 tableSize(4) dataStart(4)=0x1c
                   tableOffset(4) namesAreaSize(4) recordsEnd(4) fmt(4)=0x3a4
  Data area [dataStart, tableOffset): per-file blocks, 4-byte aligned:
      block = {origSize:4, storedSize:4, escape:1, stream}
      storedSize counts the whole block incl. 9-byte header.
  Table (tableSize bytes at tableOffset):
      [0,4) zero; [4,namesAreaSize) name entries
        {WORD nDwords, WORD x, UPPERNAME, lowername} (each name nDwords*4 padded)
      [namesAreaSize, recordsEnd) 44-byte records:
        {nameOff, attrs, FILETIME*3, dataOff, origSize, storedSize}
      [recordsEnd, tableSize) 32-byte root node (byte-preserved on repack)
  Decompression: escape-byte RLE-LZ (see decompress()).
"""
import struct

def rol(b, n): return ((b << n) | (b >> (8 - n))) & 0xff

def make_key(s):
    B = (s * 12)[:12].encode('cp932')
    return bytes([~B[0] & 0xff, rol(B[1], 4), B[2] ^ 0x8a, ~rol(B[3], 4) & 0xff,
                  ~B[4] & 0xff, B[5] ^ 0xac, ~B[6] & 0xff,
                  ~((B[7] >> 3) | (B[7] << 5)) & 0xff, rol(B[8], 3), B[9] ^ 0x7f,
                  rol(B[10], 4) ^ 0xd6, B[11] ^ 0xcc])

def xor(data, key):
    return bytes(b ^ key[i % 12] for i, b in enumerate(data))

def decompress(block):
    """block = full storedSize bytes (9-byte header + stream)."""
    origSize, storedSize = struct.unpack('<II', block[:8])
    escape = block[8]
    src = block[9:]
    out = bytearray()
    i = 0
    dist = 0
    n = len(src)
    while i < n:
        b = src[i]
        if b != escape:
            out.append(b); i += 1; continue
        if i + 1 < n and src[i + 1] == escape:
            out.append(escape); i += 2; continue
        if i + 1 >= n: break
        cnt = src[i + 1]
        c = cnt - 1 if cnt > escape else cnt
        i += 2
        length = c >> 3
        if c & 4:
            if i >= n: break
            length |= src[i] << 5
            i += 1
        length += 4
        dsz = c & 3
        if dsz == 0:
            if i >= n: break
            dist = src[i]; i += 1
        elif dsz == 1:
            if i + 1 >= n: break
            dist = src[i] | (src[i + 1] << 8); i += 2
        elif dsz == 2:
            if i + 2 >= n: break
            dist = src[i] | (src[i + 1] << 8) | (src[i + 2] << 16); i += 3
        d = dist + 1
        if length > d:
            base = len(out) - d
            for k in range(length):
                out.append(out[base + (k % d)])
        else:
            base = len(out) - d
            out.extend(out[base:base + length])
    return bytes(out)

def compress(data, escape=0xfa):
    """Compressor for the escape-RLE-LZ scheme. Greedy longest-match."""
    n = len(data)
    out = bytearray()
    lit = bytearray()

    def flush():
        out.extend(lit)
        del lit[:]

    # hash chains on 4-byte prefix
    from collections import defaultdict
    chains = defaultdict(list)
    i = 0
    prev_dist = None
    while i < n:
        best_len = 0; best_dist = 0
        if i + 4 <= n:
            key = data[i:i + 4]
            for j in reversed(chains[key]):
                d = i - j
                if d <= 0 or d >= (1 << 24): break
                # length = (c>>3 <= 31) + (hi <= 255)<<5 + 4  =>  max 8195
                maxlen = min(n - i, 8195)
                l = 0
                while l < maxlen and data[j + l] == data[i + l]:
                    l += 1
                if l > best_len:
                    best_len = l; best_dist = d
                    if l >= maxlen: break
            chains[key].append(i)
            if len(chains[key]) > 64:
                del chains[key][:-64]
        if best_len >= 6:
            # emit pending literals
            flush()
            length = best_len
            dist = best_dist - 1  # stored dist = d-1
            if dist < 0x100: dsz = 0
            elif dist < 0x10000: dsz = 1
            else: dsz = 2
            # c must be <= 0xf9 (or 0xfa, encodable as cnt 0xfb); shrink if not
            while True:
                L = length - 4
                hi_needed = L > 0x1f
                c = ((L & 0x1f) << 3) | dsz | (4 if hi_needed else 0)
                if c <= 0xf9 or c == 0xfa:
                    break
                length -= 1
                if length < 6:
                    length = 0
                    break
            if length < 6:
                lit.append(data[i]); i += 1; continue
            cnt = 0xfb if c == 0xfa else c
            out.append(escape)
            out.append(cnt)
            if hi_needed:
                out.append(L >> 5)
            if dsz == 0:
                out.append(dist)
            elif dsz == 1:
                out += struct.pack('<H', dist)
            else:
                out += struct.pack('<I', dist)[:3]
            i += length
        else:
            b = data[i]
            if b == escape:
                flush()
                out.append(escape); out.append(escape)
            else:
                lit.append(b)
            i += 1
    flush()
    return struct.pack('<IIB', n, len(out) + 9, escape) + bytes(out)

class Dxa:
    def __init__(self, raw, keystring):
        self.key = make_key(keystring)
        dec = xor(raw, self.key)
        self.dec = dec
        assert dec[:2] == b'DX', 'bad magic'
        self.version = struct.unpack('<H', dec[2:4])[0]
        (self.tableSize, self.dataStart, self.tableOff,
         self.namesSize, self.recordsEnd, self.fmt) = struct.unpack('<6I', dec[4:28])
        self.tbl = bytearray(dec[self.tableOff:self.tableOff + self.tableSize])
        self.names = {}      # nameOff -> (upper, lower, x, n)
        self.order = []      # nameOffs in table order
        off = 4
        while off < self.namesSize:
            nd, x = struct.unpack('<HH', self.tbl[off:off + 4])
            if nd == 0: break
            u = bytes(self.tbl[off + 4:off + 4 + nd * 4]).split(b'\0')[0]
            l = bytes(self.tbl[off + 4 + nd * 4:off + 4 + nd * 8]).split(b'\0')[0]
            self.names[off] = [u, l, x, nd]
            self.order.append(off)
            off += 4 + nd * 8
        self.namesEnd = off
        self.recs = []
        nrec = (self.recordsEnd - self.namesSize) // 44
        for k in range(nrec):
            o = self.namesSize + k * 44
            nameOff, attrs = struct.unpack('<II', self.tbl[o:o + 8])
            fts = bytes(self.tbl[o + 8:o + 32])
            A, B, C = struct.unpack('<III', self.tbl[o + 32:o + 44])
            self.recs.append([nameOff, attrs, fts, A, B, C])
        self.rootNode = bytes(self.tbl[self.recordsEnd:])

    def files(self):
        """yield (name_lower, decompressed_bytes, record_index)"""
        for k, r in enumerate(self.recs):
            if r[1] & 0x10:  # directory
                continue
            nm = self.names.get(r[0])
            if nm is None: continue
            name = nm[1].decode('cp932', 'replace')
            if r[5] == 0xffffffff:  # stored raw (uncompressed)
                data = self.dec[self.dataStart + r[3]:self.dataStart + r[3] + r[4]]
                assert len(data) == r[4], 'raw size mismatch %s' % name
            else:
                block = self.dec[self.dataStart + r[3]:self.dataStart + r[3] + r[5]]
                data = decompress(block)
                assert len(data) == r[4], 'size mismatch %s: %d != %d' % (name, len(data), r[4])
            yield name, data, k

    def repack(self, name_to_data, out_path):
        """name_to_data: dict lowername -> new bytes (missing = unchanged)."""
        # 1. lay out data blocks in record order
        blocks = []
        pos = 0
        for r in self.recs:
            if r[1] & 0x10: continue
            nm = self.names.get(r[0])
            if nm is None: continue
            name = nm[1].decode('cp932', 'replace')
            if name in name_to_data:
                new = name_to_data[name]
                if r[5] == 0xffffffff:
                    blk = new                       # keep raw storage
                else:
                    blk = compress(new)
            else:
                if r[5] == 0xffffffff:
                    blk = self.dec[self.dataStart + r[3]:self.dataStart + r[3] + r[4]]
                else:
                    blk = self.dec[self.dataStart + r[3]:self.dataStart + r[3] + r[5]]
            r[3] = pos                      # dataOff
            r[4] = len(blk) if r[5] == 0xffffffff else struct.unpack('<I', blk[:4])[0]
            if name in name_to_data and r[5] == 0xffffffff:
                r[4] = len(blk)
            if r[5] != 0xffffffff:
                r[5] = len(blk)              # storedSize
            blocks.append(blk)
            pos += len(blk)
            pos = (pos + 3) & ~3            # 4-byte align
        dataArea = bytearray()
        for blk in blocks:
            dataArea += blk
            dataArea += b'\0' * ((-len(blk)) % 4 if False else (4 - len(blk) % 4) % 4)
        # 2. rebuild table
        tbl = bytearray(self.tbl)
        for k, r in enumerate(self.recs):
            o = self.namesSize + k * 44
            struct.pack_into('<II', tbl, o, r[0], r[1])
            tbl[o + 8:o + 32] = r[2]
            struct.pack_into('<III', tbl, o + 32, r[3], r[4], r[5])
        # 3. header
        tableOff = self.dataStart + len(dataArea)
        hdr = struct.pack('<2H6I', 0x5844, self.version, len(tbl), self.dataStart,
                          tableOff, self.namesSize, self.recordsEnd, self.fmt)
        raw = hdr + bytes(dataArea) + bytes(tbl)
        with open(out_path, 'wb') as f:
            f.write(xor(raw, self.key))
        return tableOff
