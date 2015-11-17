#!/usr/bin/python

import sys
import os
import struct
import optparse

from Crypto.Cipher import AES


class CorruptFile(Exception):
    pass


class LCG(object):

    def __init__(self, seed):
        self._seed = (seed & 0xFFFFFFFF << 32) | (seed - 1 & 0xFFFFFFFF)

    def rand(self):
        a = 6364136223846793005
        c = 1
        m = 2 ** 64
        self._seed = (a * self._seed + c) % m
        return self._seed >> 0x21

    def randstring(self, n):
        c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-#'?!"
        return ''.join([c[self.rand() % len(c)] for _ in range(n)])

    def randbin(self, n):
        return ''.join([chr(self.rand() & 0xff) for _ in range(n)])


def get_key_iv(lcg, count=0):
    for i in range(count * 32):
        lcg.rand()
    key = lcg.randstring(16)
    iv = lcg.randbin(16)
    return key, iv


def parse_header(filepath):
    header_size = 0
    try:
        with open(filepath, 'rb') as f:
            old_mode = struct.unpack('<I', f.read(4))[0]
            key_sz = struct.unpack('<I', f.read(4))[0]
            key = f.read(key_sz)
            iv_file = f.read(16)
            if not key or not iv_file:
                raise CorruptFile()
            header_size = f.tell()
    except struct.error:
        raise CorruptFile()

    return iv_file, header_size


def find_seed(filepath):
    file_idx_start = 0
    ts = int(os.path.getmtime(filepath))

    try:
        iv_file, _ = parse_header(filepath)
    except CorruptFile:
        print '[!] File is probably truncated'
        return None

    for i in range(-60, 3600):
        lcg = LCG(ts - i)
        for file_idx in range(file_idx_start, file_idx_start + 10000):
            key, iv = get_key_iv(lcg)
            if iv[:15] == iv_file[:15]:
                return ts - i

    return None


def decrypt_file(d, path):
    iv_file, header_size = parse_header(path)

    with open(path, 'rb') as f:
        f.seek(header_size)
        content = f.read()

    last_block_size = ord(iv_file[15]) & 0x0F
    if last_block_size == 0:
        last_block_size = 16
    orig_size = len(content) - 16 + last_block_size
    if iv_file[:15] not in d:
        return False

    cipher = AES.new(d[iv_file[:15]], AES.MODE_CBC, iv_file)
    decrypted_content = cipher.decrypt(content)[:orig_size]

    decrypted_path = path[:-len('.encrypted')]
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_content)

    return True


def decrypt_files(seed, file_list, error_file_list):
    recovered = 0
    bad_seed = 0
    corrupt = 0
    lcg = LCG(seed)

    with open(file_list, 'r') as f:
        count = 0
        for _ in f:
            count += 1

    if os.path.exists(error_file_list):
        os.unlink(error_file_list)

    d = dict()
    for i in range(count * 5):
        k, iv = get_key_iv(lcg)
        d[iv[:15]] = k

    with open(file_list, 'r') as f:
        for line in f:
            _, filepath = line.strip().split(' ', 1)
            try:
                if decrypt_file(d, filepath):
                    print '[OK]', filepath
                    recovered += 1
                else:
                    print '[FAILED]', filepath
                    bad_seed += 1
                    with open(error_file_list, 'a') as e:
                        e.write(line)
            except CorruptFile:
                print '[CORRUPT]', filepath
                corrupt += 1

    print '[*] recovered %d files' % recovered
    print '[*] failed to recover (probably bad seed) %d files' % bad_seed
    print '[*] %d corrupted (probably truncated) files' % corrupt


def main(filename=None, seed=None, filelist=None, errorfilelist=None):
    if filename and (seed or filelist or errorfilelist):
        print '[!] Choose a filename or choose a seed and filelist'
        return -1

    if filename:
        seed = find_seed(filename)
        if seed:
            print '[*] Seed: %d' % seed
        else:
            print '[!] Seed not found! Timestamps corrupt?'
    elif seed and filelist and errorfilelist:
        decrypt_files(seed, filelist, errorfilelist)
    else:
        print('[!] The seed, filelist, and errorfilelist are all required')

    return 0


if __name__ == '__main__':
    parser = optparse.OptionParser()

    find_group = optparse.OptionGroup(parser, 'Find seed',
                                      'Tries to get the seed used to generate the encryption key and IV.')
    find_group.add_option('-f', '--filename', dest='filename', help='first encrypted file')
    parser.add_option_group(find_group)

    decrypt_group = optparse.OptionGroup(parser, 'Decrypt',
                                         'Decrypts files given an initial seed and a list of files.')
    decrypt_group.add_option('-s', '--seed', dest='seed', help='Seed value', type='int')
    decrypt_group.add_option('-l', '--filelist', dest='filelist',
                             help='File containing a list of timestamps and file paths')
    decrypt_group.add_option('-e', '--errorfilelist', dest='errorfilelist',
                             help='File containing timestamps and file paths for files which were not decrypted')

    parser.add_option_group(decrypt_group)
    options, _ = parser.parse_args(sys.argv)

    sys.exit(main(**vars(options)))
