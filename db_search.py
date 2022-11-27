#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

import argparse
import io
import os
import struct
from binascii import hexlify
from datetime import datetime, timedelta


# frame types
D_START = '01003E01'
D_BODY = '01003E05'
D_END = '01002605'
D_ANY = [D_START, D_BODY, D_END]


def main():
    parser = argparse.ArgumentParser(
        prog='sb_search <infile>',
        description='Search SatNOGS DB export for frames',
        epilog='')
    parser.add_argument('infile', help="Input file with frames")
    parser.add_argument('-o', '--outfile', help='Output file')
    gr1 = parser.add_mutually_exclusive_group()
    gr1.add_argument('-s', '--start', action='store_true', help="Search start frames")
    gr1.add_argument('-e', '--end', action='store_true', help="Search end frames")
    parser.add_argument('-m', '--match', default='', help='What to match in end frame')
    parser.add_argument('-d', '--dist', type=int, default=100, help='Search distance to next frame')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help="Increase verbosity")
    args = parser.parse_args()
    if not args.outfile:
        args.outfile = "out"

    filedata = []
    data = []
    try:
        file = open(args.infile, 'r')
        filedata = file.read().splitlines()
    except UnicodeDecodeError:
        print("ERROR: binary file ?")
        exit(1)

    for row in filedata:
        if '|' in row:
            d = row.split('|')
            if len(d[1]) == 128:
                data.append({'ts': datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S'),
                             'cmd': d[1][:8],
                             'addr': int((d[1][12:14] + d[1][10:12]), 16) % 32768,
                             'header': d[1][:16],
                             'payload': d[1][16:]})
            elif args.verbosity >= 2:
                print("Skipped row with data length: {}".format(len(d[1])))

    if args.start or args.end:
        for row in data:
            if args.start and row['cmd'] == D_START:
                print(row)
            if args.end and row['cmd'] == D_END:
                print(row)
        exit(0)

    i = addr = pos = skipped = 0
    framelen = 56
    image = []
    while i < len(data):  # ends: A69493DB 52B94F41 600A010A
        if pos == 0 and data[i]['cmd'] == D_END and data[i]['payload'].startswith(args.match):
            print('End frame found at line: {}, block: {}'.format(i, data[i]['addr'] // framelen))
            pos = i + 1
            addr = data[i]['addr'] - framelen
            image.append(data[i]['header'] + data[i]['payload'] + '\n')
        elif pos > 0 and data[i]['addr'] == addr:
            if args.verbosity >= 1:
                print('Found block {}, at {} lines away'.format(addr // framelen, i - pos))
            pos = i + 1
            image.append(data[i]['header'] + data[i]['payload'] + '\n')
            if addr == 0:
                print('Start frame found at line: {}'.format(i))
                break
            addr -= framelen
        if pos > 0 and i - pos > args.dist:
            if args.verbosity >= 1:
                print('Block {} not found, skip to next next.'.format(addr // framelen))
            skipped += 1
            i = pos
            addr -= framelen
        if addr < 0:
            print('Block < 0, exit')
            break
        i += 1
    rawfile = open('{}_{}.raw'.format(args.outfile, args.match), 'w')
    print("Writing {} with {} blocks, skipped {} not found.".format(rawfile.name, len(image), skipped))
    image.reverse()
    rawfile.writelines(image)
    rawfile.close()


if __name__ == '__main__':
    main()
