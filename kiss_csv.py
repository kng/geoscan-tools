#!/usr/bin/env python3
# Made by SA2KNG <knegge at gmail.com>

from binascii import hexlify
from datetime import datetime, timedelta
from os import path
from struct import unpack
from sys import argv, exit


def main():
    if len(argv) != 2:
        print(f'Useage: {path.basename(argv[0])} <kissfile>\n'
              'Process a KISS file to CSV with HEX frames.\n'
              'Output will have the same name as the input, but with .csv extension\n')
        exit(2)

    try:
        with open(argv[1], 'rb') as kf:
            frame_tuples = list(read_kiss_frames(kf))
    except AssertionError as e:
        print('ERROR: KISS file inconsistent: {}'.format(e))
        exit(1)

    with open(path.splitext(argv[1])[0] + '.csv', 'w') as outfile:
        for (timestamp, frame) in frame_tuples:
            if len(frame) == 0:
                continue
            outfile.write('{} | len: {} | {}\n'.format(timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                                       len(frame), hexlify(frame).decode('ascii').upper()))


# KISS functions:
# Copyright 2020 Fabian Schmidt <kerel+satnogs at mailbox.org>
# SPDX-License-Identifier: GPL-3.0-or-later
# Modified by SA2KNG <knegge at gmail.com>

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
    assert (parts[0] == b''), 'does not begin with frame start'

    # Check that content is composed of (empty, timestamp, empty, frame_content)-frame tuples
    parts_len = len(parts)
    assert ((parts_len - 1) % 2 == 0), 'does not contain even number of frame tuples'

    frames_len = (parts_len - 1) // 2

    timestamp_raw = None
    for i in range(0, frames_len):
        if parts[i * 2 + 1][0] == 9:
            timestamp_raw = parts[i * 2 + 1]
            continue
        escaped_frame = parts[i * 2 + 1]

        # Make sure this is a time frame (type = b'\x09')
        assert (timestamp_raw[0] == 9), 'timestamp is not type 9'
        # Make sure this is a data frame (type = b'\x00')
        assert (escaped_frame[0] == 0), 'data is not type 0'

        timestamp_int, = unpack('>Q', kiss_unescape(timestamp_raw[1:]))
        epoch = datetime(1970, 1, 1)
        timestamp_e = epoch + timedelta(seconds=timestamp_int // 1000)

        yield timestamp_e, kiss_unescape(escaped_frame[1:])


if __name__ == '__main__':
    main()
