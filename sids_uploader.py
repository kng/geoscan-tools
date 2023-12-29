#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

from datetime import datetime, timedelta
from os import path
from requests import post
from struct import unpack
from sys import argv

SERVER = 'https://db.satnogs.org/api/telemetry/'  # Production database
# SERVER = 'https://db-dev.satnogs.org/api/telemetry/'  # Dev database
MYCALL = ''
QTH_LAT = '0.0N'  # WGS84
QTH_LON = '0.0E'


def main():
    if len(argv) != 3:
        print(f'Usage: {path.basename(argv[0])} <NORAD> <infile>\n'
              'Upload stored frames to SatNOGS DB via SiDS.')
        exit(1)
    if not argv[1].isnumeric() or not 0 <= int(argv[1]) <= 99999:
        print('Invalid NORAD ID')
        exit(1)
    if not path.exists(argv[2]):
        print(f'File not found: {argv[2]}')
        exit(1)
    if len(MYCALL) == 0:
        print('No call sign set, please edit!')
        exit(1)

    frames = parse_file(argv[2])
    print(f'Found {len(frames)} frames.')
    upload_frames(int(argv[1]), frames)


def upload_frames(norad, frames):
    print('Uploading: ', end='')
    for row in frames:
        try:
            payload = {'noradID': norad, 'source': MYCALL, 'locator': 'longLat', 'latitude': QTH_LAT,
                       'longitude': QTH_LON, 'version': '1.8.1', 'timestamp': row[0], 'frame': row[1]}
            r = post(SERVER, data=payload)
            r.raise_for_status()
            print('.', end='')
        except Exception as e:
            print(f'Request for timestamp {row[0]} failed: {e}')
            break
    print(' Done.')


def parse_file(infile):
    try:
        with open(infile, 'rt') as f:
            return parse_hexfile(f)
    except UnicodeDecodeError:
        with open(infile, 'rb') as f:
            return parse_kissfile(f)


def parse_hexfile(infile):
    data = []
    for row in infile:
        row = row.replace(' ', '').strip()
        if '|' in row:
            row = row.split('|')
        else:
            print('ERROR: File does not contain timestamps')
            return []
        if len(row) >= 10000:  # add nothing
            data.append([row[0], row[-1]])
    print('WARNING: HEX reader not implemented properly')
    return data


def parse_kissfile(infile):
    data = []
    ts = datetime(1970, 1, 1)  # MUST be overwritten by timestamps in file
    for row in infile.read().split(b'\xC0'):
        if len(row) == 9 and row[0] == 9:  # timestamp frame
            ts = datetime(1970, 1, 1) + timedelta(seconds=unpack('>Q', row[1:])[0] / 1000)
        if len(row) > 0 and row[0] == 0:  # data frame
            data.append([ts.isoformat(timespec='milliseconds') + 'Z',
                         row[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb').
                        hex(bytes_per_sep=2).upper()])
    return data


if __name__ == '__main__':
    main()
