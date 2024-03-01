#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

from io import BytesIO
from os import path
from sys import argv


def main():
    if len(argv) != 2:
        print(f'Usage: {path.basename(argv[0])} <infile>\n'
              'Process a single Stratosat-TK1 image from hex/KISS frames.\n'
              'Output will have the same name as the input, but with .jpg extension\n')
        exit(0)
    if not path.exists(argv[1]):
        print(f'File not found: {argv[1]}')
        exit(1)
    frames = parse_file(argv[1])
    data = parse_frames(frames)
    write_image(path.splitext(argv[1])[0] + '.jpg', data)


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
        if len(row) == 128:
            data.append(row)
    return data


def parse_kissfile(infile):
    data = []
    for row in infile.read().split(b'\xC0'):
        if len(row) == 0 or row[0] != 0:
            continue
        data.append(row[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb').hex(bytes_per_sep=2))
    return data


def parse_frames(data):
    image = BytesIO()
    offset = 0
    for row in data:
        if row[16:22].upper() == 'FFD8FF':
            offset = int((row[14:16] + row[12:14] + row[10:12]), 16)
            if row[6:10].upper() == '2098':  # image is HR
                offset = 0
            break
    for row in data:
        cmd = row[0:4]
        addr = int((row[14:16] + row[12:14] + row[10:12]), 16) - offset
        dlen = (int(row[4:6], 16) + 2) * 2
        payload = row[16:dlen]
        if cmd == '0200' and addr >= 0:
            image.seek(addr)
            image.write(bytes.fromhex(payload))
    return image


def write_image(outfile, data):
    print(f'Writing image to: {outfile}')
    with open(outfile, 'wb') as f:
        f.write(data.getbuffer())


if __name__ == '__main__':
    main()
