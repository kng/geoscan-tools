#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

import argparse
import io
import os
import struct
from binascii import hexlify
from datetime import datetime, timedelta


def main():
    parser = argparse.ArgumentParser(
        prog='process_frames <infile>',
        description='Process images from geoscan frames',
        epilog='')
    parser.add_argument('infile', help="Input file with frames (default in hex)")
    parser.add_argument('-o', '--outfile', help="Output file prefix")
    parser.add_argument('-k', '--kiss', action='store_true', help="Input file format: KISS")
    parser.add_argument('-r', '--raw', action='store_true', help="Store raw frames")
    parser.add_argument('-s', '--single', action='store_true', help="Write to single file, accumulating data")
    parser.add_argument('--half', action='store_true', help="Switch to 16k blocks, 32k default for jpeg")
    # parser.add_argument('-p', '--pad', help="Byte to pad missing data")
    # parser.add_argument('-a', '--align', help="Align missing data with jpeg blocks")
    parser.add_argument('-v', '--verbosity', action='count', default=0, help="Increase verbosity")
    args = parser.parse_args()
    if not args.outfile:
        args.outfile = os.path.splitext(args.infile)[0]

    data = []
    if args.kiss:
        frame_tuples = []
        try:
            file = open(args.infile, 'rb')
            frame_tuples = list(read_kiss_frames(file))
        except AssertionError:
            print('ERROR: KISS file inconsistent')
            exit(1)
        for (timestamp, frame) in frame_tuples:
            if len(frame) == 64:
                data.append(hexlify(frame).decode('ascii').upper())
            elif args.verbosity >= 2:
                print("Skipped frame with length: {}".format(len(frame)))

    else:
        filedata = []
        try:
            file = open(args.infile, 'r')
            filedata = file.read().splitlines()
        except UnicodeDecodeError:
            print("ERROR: binary file ? try with --kiss")
            exit(1)
        for row in filedata:
            row = row.replace(' ', '')
            if '|' in row:
                row = row.split('|')[-1]
            if len(row) == 128:
                data.append(row)
            elif args.verbosity >= 2:
                print("Skipped row with length: {}".format(len(row)))

    dataframes = ['01003E01', '01003E05', '01002605']
    headerlength = 16
    outfile = rawfile = io.BufferedWriter
    fileindex = 0
    chunks = 1
    for row in data:
        header = row[:headerlength]
        cmd = row[:headerlength//2]
        addr = int((row[12:14] + row[10:12]), 16) % 32768
        payload = row[headerlength:]
        if args.verbosity >= 3:
            print("Frame: {} - {}".format(header, payload))
        if cmd in dataframes:
            if not outfile.closed and cmd == dataframes[0] and not args.single:
                outfile.close()
            if outfile.closed:
                extension = 'dat'
                if payload.startswith('FFD8'):
                    extension = 'jpg'
                if args.single:
                    outfile = open('{}.jpg'.format(args.outfile), 'wb')
                else:
                    outfile = open('{}_{}.{}'.format(args.outfile, fileindex, extension), 'wb')
                print("Writing to: {}".format(outfile.name))
                if args.raw:
                    rawfile = open('{}_{}.raw'.format(args.outfile, fileindex), 'w')
                    print("Raw file to: {}".format(rawfile.name))
                fileindex += 1
            pos = addr - outfile.tell()
            if pos != 0 and args.verbosity >= 1:
                print("Skipped {} bytes at pos {}. ".format(pos, addr - pos))
                # if args.pad:
                #     outfile.write(args.pad * pos)
                # pos //= 2
                # outfile.write(b'\xFF\xFF' * pos)
            outfile.seek(addr)
            outfile.write(bytes.fromhex(payload))
            if not rawfile.closed:
                rawfile.write(row + '\n')
            chunks += 1
            # stopping at 32736 or 16352 if not in single mode
            if not args.single and ((cmd == dataframes[2] and addr >= 16352 and args.half) or
               (cmd == dataframes[2] and addr >= 32736 and not args.half)):
                outfile.close()
                if not rawfile.closed:
                    rawfile.close()
                if args.verbosity >= 1:
                    print("{} bytes written.".format(chunks * 56))
                chunks = 1
        else:
            if args.verbosity >= 2:
                print("Skipped frame: {} - {}".format(header, payload))
    if not outfile.closed:
        outfile.close()
    if not rawfile.closed:
        rawfile.close()


# kiss functions:
# Copyright 2020 Fabian Schmidt <kerel+satnogs at mailbox.org>
# Extended by SA2KNG <knegge at gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

# Define KISS Special Codes
# http://www.ax25.net/kiss.aspx
FEND = b'\xc0'
FESC = b'\xdb'
TFEND = b'\xdc'
TFESC = b'\xdd'


def kiss_unescape(escaped_frame):
    return escaped_frame.replace(
        FESC + TFEND,
        FEND
    ).replace(
        FESC + TFESC,
        FESC
    )


def read_kiss_frames(kf):
    parts = kf.read().split(FEND)

    # Check that content starts with FEND byte (First Frame start)
    assert (parts[0] == b'')

    # Check that content is composed of (empty, timestamp, empty, frame_content)-frame tuples
    parts_len = len(parts)
    assert ((parts_len - 1) % 4 == 0)

    frames_len = (parts_len - 1) // 4

    for i in range(0, frames_len):
        timestamp_raw = parts[i * 4 + 1]
        escaped_frame = parts[i * 4 + 3]

        # Make sure this is a KISS control frame (type = b'\x09')
        assert (timestamp_raw[0] == 9)
        # Make sure this is a data frame (type = b'\x00')
        assert (escaped_frame[0] == 0)

        timestamp_int, = struct.unpack('>Q', kiss_unescape(timestamp_raw[1:]))
        epoch = datetime(1970, 1, 1)
        timestamp_e = epoch + timedelta(seconds=timestamp_int // 1000)

        yield timestamp_e, kiss_unescape(escaped_frame[1:])


if __name__ == '__main__':
    main()
