#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

import io
import os
import sys


def main():
    if len(sys.argv) != 2:
        print(f'Useage: {os.path.basename(sys.argv[0])} <infile>\n'
              'Process a single Geoscan-Edelveis image from hex frames.\n'
              'Output will have the same name as the input, but with .jpg extension\n')
        sys.exit(0)
    frames = parse_file(sys.argv[1])
    data = parse_frames(frames)
    write_image(os.path.splitext(sys.argv[1])[0] + '.jpg', data)


def parse_file(infile):
    data = []
    with open(infile, 'r') as f:
        for row in f:
            row = row.replace(' ', '').strip()
            if '|' in row:
                row = row.split('|')[-1]
            if len(row) == 128:
                data.append(row)
    return data


def parse_frames(data):
    image = io.BytesIO()
    for row in data:
        cmd = row[0:4]
        addr = int((row[12:14] + row[10:12]), 16) % 32768
        dlen = (int(row[4:6], 16) + 2) * 2
        payload = row[16:dlen]
        if cmd == '0100':
            image.seek(addr)
            image.write(bytes.fromhex(payload))
    return image


def write_image(outfile, data):
    with open(outfile, 'wb') as f:
        f.write(data.getbuffer())


if __name__ == '__main__':
    main()
