#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

from io import BytesIO
from os import path
from sys import argv


def main():
    if len(argv) != 2:
        print(f'Useage: {path.basename(argv[0])} <infile>\n'
              'Process CAS-5A images from hex/KISS frames.\n'
              'Output will have the same name as the input, but with image timestamp and .jpg extension\n')
        exit(0)
    if not path.exists(argv[1]):
        print(f'File not found: {argv[1]}')
        exit(1)
    frames = parse_file(argv[1])
    for pid in set(get_photo_ids(frames)):
        ts = f'2{int(pid[0:2], 16):03d}-{int(pid[2:4], 16):02d}-{int(pid[4:6], 16):02d}T' \
             f'{int(pid[6:8], 16):02d}-{int(pid[8:10], 16):02d}-{int(pid[10:12], 16):02d}'
        data = parse_frames(pid, frames)
        write_image(f'{path.splitext(argv[1])[0]}_{ts}.jpg', data)


def parse_file(infile):
    try:
        with open(infile, 'r') as f:
            return parse_hexfile(f)
    except UnicodeDecodeError:
        with open(infile, 'rb') as f:
            return parse_kissfile(f)


def parse_hexfile(f):
    data = []
    for row in f:
        row = row.replace(' ', '').strip()
        if '|' in row:
            row = row.split('|')[-1]
        if len(row) >= 64:
            data.append(row)
    return data


def parse_kissfile(infile):
    data = []
    for row in infile.read().split(b'\xC0'):
        if len(row) < 32 or row[0] != 0:
            continue
        data.append(row[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb').hex(bytes_per_sep=2))
    return data


def get_photo_ids(data):
    pids = set()
    for row in data:
        if int(row[32:34], 16) != 3 or int(row[46:48], 16) < 22 or int(row[46:48], 16) > 23 \
                or int(row[48:50], 16) > 12 or int(row[50:52], 16) > 31 or int(row[52:54], 16) > 24 \
                or int(row[54:56], 16) > 60 or int(row[56:58], 16) > 60:  # sanity check
            continue
        pids.add(row[46:64])
    return pids


def parse_frames(pid, data):
    image = BytesIO()
    dlen = 240  # assumed maxed out frames to multiply by sequence number
    hlen = 32   # header length
    for row in data:
        if pid != row[46:64] or int(row[32:34], 16) != 3:
            continue
        ftot = int(row[34:38], 16)
        fseq = int(row[38:42], 16)
        flen = int(row[42:46], 16) * 2 + hlen
        if fseq <= ftot and flen <= len(row):
            image.seek((fseq - 1) * dlen)
            image.write(bytes.fromhex(row[64:flen]))
    return image


def write_image(outfile, data):
    print(f'Writing image to: {outfile}')
    with open(outfile, 'wb') as f:
        f.write(data.getbuffer())


if __name__ == '__main__':
    main()
