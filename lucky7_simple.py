#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

from io import BytesIO
from os import path
from sys import argv


def main():
    if len(argv) != 2:
        print(f'Useage: {path.basename(argv[0])} <infile>\n'
              'Process Lucky-7 images from hex/KISS frames.\n'
              'Output will have the same name as the input, but with ID and .jpg extension\n')
        exit(0)
    if not path.exists(argv[1]):
        print(f'File not found: {argv[1]}')
        exit(1)
    frames = parse_file(argv[1])
    for pid in set(get_packet_ids(frames)):
        print(pid)
        data = parse_frames(pid, frames)
        write_image(f'{path.splitext(argv[1])[0]}_{pid}.jpg', data)


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
        if len(row) >= 70:
            data.append(row)
    return data


def parse_kissfile(infile):
    data = []
    for row in infile.read().split(b'\xC0'):
        if len(row) == 0 or row[0] != 0:
            continue
        data.append(row[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb').hex(bytes_per_sep=2))
    return data


def get_packet_ids(data):
    pids = []
    offset = 49152  # 0xC000
    for row in data:
        oid = int(row[0:2], 16)
        obc = int(row[2:6], 16)
        packets = int(row[10:14], 16)
        if (oid == 128 or oid == 0) and obc >= offset:
            pids.append(packets)
    return pids


def parse_frames(pid, data):
    image = BytesIO()
    offset = 49152  # 0xC000
    for row in data:
        oid = int(row[0:2], 16)
        obc = int(row[2:6], 16)
        # mcu = int(row[6:10], 16)
        packets = int(row[10:14], 16)
        payload = row[14:70]
        # print(f'ID {oid:4}, OBC {obc:5}, MCU {mcu:5}, packets {packets:5}: {row[0:14]} {payload}')
        if (oid == 128 or oid == 0) and obc >= offset and packets == pid:
            image.seek((obc - offset) * 28)
            image.write(bytes.fromhex(payload))
    return image


def write_image(outfile, data):
    print(f'Writing image to: {outfile}')
    with open(outfile, 'wb') as f:
        f.write(data.getbuffer())


if __name__ == '__main__':
    main()
