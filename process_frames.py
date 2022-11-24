#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

import argparse
import io


def main():
    parser = argparse.ArgumentParser(
        prog='sa2kng_process <infile>',
        description='Process images from geoscan frames',
        epilog='')
    parser.add_argument('infile', help="Input file, hex dump of frames")
    parser.add_argument('-o', '--outfile', help="Output file prefix", default="out")
    # parser.add_argument('-r', '--raw', action='store_true', help="Store raw output")
    # parser.add_argument('-k', '--kiss', action='store_true', help="Input file format: KISS")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    args = parser.parse_args()

    file = open(args.infile, 'r')
    data = file.read().splitlines()

    dataframes = ['01003E01', '01003E05', '01002605']
    headerlength = 16
    outfile = io.BufferedWriter
    fileindex = 0
    for row in data:
        row = row.replace(' ', '')
        if '|' in row:
            row = row.split('|')[-1]
        if len(row) != 128:
            continue
        header = row[:headerlength]
        cmd = row[:headerlength//2]
        addr = int((row[12:14] + row[10:12]), 16) % 32768
        payload = row[headerlength:]
        # print("Frame: {} - {}".format(header, payload))
        if cmd in dataframes:
            if outfile.closed:
                extension = 'dat'
                if payload.startswith('FFD8'):
                    extension = 'jpg'
                outfile = open('{}_{}.{}'.format(args.outfile, fileindex, extension), 'wb')
                print("Writing to: {}".format(outfile.name))
                fileindex += 1
            outfile.seek(addr)
            outfile.write(bytes.fromhex(payload))
            if cmd == dataframes[2]:
                outfile.close()
        else:
            if args.verbose:
                print("Skipped frame: {} - {}".format(header, payload))


if __name__ == '__main__':
    main()
