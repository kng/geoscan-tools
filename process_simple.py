#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

from io import BytesIO
from os import path
from sys import argv


def main():
    if len(argv) != 2:
        print(f'Useage: {path.basename(argv[0])} <infile>\n'
              'Process a single Geoscan-Edelveis image from hex frames.\n'
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
    offset = 16384  # old 32768
    for row in data:
        if row[0:4] == '0100' and row[6:8] == '01':
            offset = int((row[12:14] + row[10:12]), 16)
            break
    for row in data:
        cmd = row[0:4]
        addr = int((row[12:14] + row[10:12]), 16) - offset
        dlen = (int(row[4:6], 16) + 2) * 2
        payload = row[16:dlen]
        if cmd == '0100' and addr >= 0:
            image.seek(addr)
            image.write(bytes.fromhex(payload))
    return image


def write_image(outfile, data):
    print(f'Writing image to: {outfile}')
    with open(outfile, 'wb') as f:
        f.write(data.getbuffer())


if __name__ == '__main__':
    main()
