#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

import argparse


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

    headerlength = 16
    outfile = None
    fileindex = 0
    for row in data:
        row = row.replace(' ', '')
        if '|' in row:
            row = row.split('|')[-1]
        if len(row) != 128:
            continue
        header = row[:headerlength]
        payload = row[headerlength:]
        # print("Frame: {} - {}".format(header, payload))
        if header.startswith('01003E01') or (not outfile and header.startswith('01003E05')):
            if outfile:
                outfile.close()
            extension = 'dat'
            if payload.startswith('FFD8'):
                extension = 'jpg'
            outfile = open('{}_{}.{}'.format(args.outfile, fileindex, extension), 'wb')
            print("Writing to: {}".format(outfile.name))
            fileindex += 1
            outfile.write(bytes.fromhex(payload))
        elif header.startswith('01003E05') and outfile:
            outfile.write(bytes.fromhex(payload))
        else:
            if args.verbose:
                print("Skipped frame: {} - {}".format(header, payload))


if __name__ == '__main__':
    main()
