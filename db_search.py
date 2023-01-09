#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

import argparse
from datetime import datetime  # , timedelta
from math import ceil

# frame types
D_START = '01003E01'
D_BODY = '01003E05'
D_END = '01002605'
D_ANY = [D_START, D_BODY, D_END]
DATALEN = 56
TF1 = '%Y-%m-%dT%H:%M:%SZ'
TF2 = '%Y-%m-%d %H:%M:%S'


def main():
    parser = argparse.ArgumentParser(description='Search SatNOGS DB export for images')
    parser.add_argument('infile', help="Input file with frames")
    parser.add_argument('-o', '--outfile', default='out', help='Output file')
    gr1 = parser.add_mutually_exclusive_group()
    gr1.add_argument('-s', '--start', action='store_true', help="List START frames, then exit")
    gr1.add_argument('-e', '--end', action='store_true', help="List END frames, then exit")
    parser.add_argument('-m', '--match', default='', help='What to match in END frame')
    parser.add_argument('-d', '--dist', type=int, default=100, help='Search distance in rows to next frame (def: 100)')
    parser.add_argument('-n', '--skip', type=int, default=0, help='Skip this many END frames')
    parser.add_argument('-a', '--all', action='store_true', help='Loop through entire file')
    parser.add_argument('-f', '--offset', type=int, default=32768, help='Offset address in start frame')
#    parser.add_argument('--time_start', type=lambda s: datetime.strptime(s, TF1),
#                        help='Start is greater than or equal to YYYY-mm-ddThh:mm:SSZ')
#    parser.add_argument('--time_end', type=lambda s: datetime.strptime(s, TF1),
#                        help='End is less than or equal to')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help="Increase verbosity")
    args = parser.parse_args()
    if args.match:
        args.outfile += f'_{args.match}'

    data = find_frames(args.infile, args.verbosity, args.offset)

    if args.start or args.end:
        print('# Time             | address   | header         | payload')
        for row in data:
            if (args.start and row['cmd'] == D_START) \
                    or (args.end and row['cmd'] == D_END):
                print(f"{row['ts'].strftime(TF1)} raw addr {row['addr']:#5}: {row['header']} {row['payload']}")
        exit(0)

    print(f"Processing {len(data)} valid frames...")

    if args.all:
        ends = [i for i, row in enumerate(data) if row['cmd'] == D_END and row['addr'] >= 32000]
        for i in ends:
            image = find_image(data, i, args)
            write_hex(f'{args.outfile}_{i}', image)
            write_jpeg(f'{args.outfile}_{i}', image)
    else:
        image = find_image(data, 0, args)
        write_hex(f'{args.outfile}_{args.skip}', image)
        write_jpeg(f'{args.outfile}_{args.skip}', image)


def find_frames(filename, verbosity, offset):
    data = []
    try:
        file = open(filename, 'r')
        filedata = file.read().splitlines()
    except UnicodeDecodeError:
        print("ERROR: binary file ?")
        return None
    for row in filedata:
        if '|' in row:
            d = row.split('|')
            if len(d[1]) == 128 and d[1][:8] in D_ANY:
                data.append({'ts': datetime.strptime(d[0], TF2),
                             'cmd': d[1][:8],
                             'addr': int((d[1][12:14] + d[1][10:12]), 16) - offset,
                             'header': d[1][:16],
                             'payload': d[1][16:]})
            elif verbosity >= 2:
                print("Skipped row with wrong length: {}".format(len(d[1])))
        elif verbosity >= 1:
            print("Row is missing '|', wrong format?")
    return data


def find_image(data, offset, args):
    addr = skipped = 0
    line = offset
    lastfound = -1
    frameestimate = -1
    image = []
    while line < len(data):
        if lastfound < 0 and data[line]['cmd'] == D_END and data[line]['addr'] >= 32000:
            if args.skip > 0:
                args.skip -= 1
                line += 1
                if args.verbosity >= 2:
                    print('Skipping to next END frame')
                continue
            print('End frame found at line: {}, addr: {}'.format(line, data[line]['addr']))
            frameestimate = ceil((data[line]['addr'] + DATALEN) / DATALEN)
            print(f"Estimated amount of frames {frameestimate}")
            image.append(data[line]['header'] + data[line]['payload'] + '\n')
            addr = data[line]['addr'] - DATALEN
            lastfound = line
            line = max(offset, line - args.dist)
        if lastfound >= 0 and abs(data[line]['addr'] - addr) < DATALEN:
            if args.verbosity >= 1:
                print(f"Found addr {addr}, at line {line}")
            image.append(data[line]['header'] + data[line]['payload'] + '\n')
            lastfound = line
            addr = data[line]['addr'] - DATALEN
            line = max(offset, line - args.dist)
        if lastfound >= 0 and line - lastfound > args.dist:
            if args.verbosity >= 1:
                print('Frame addr {} not found, skip to next.'.format(addr))
            skipped += 1
            line = max(offset, lastfound - args.dist)
            addr -= DATALEN
        if addr < 0:
            break
        line += 1
    print(f"Last line used: {lastfound}, frames: {len(image)}, skipped: {skipped}, "
          f"estimated missing: {frameestimate - len(image)}")
    image.reverse()
    return image


def write_hex(filename, image):
    with open('{}.raw'.format(filename), 'w') as f:
        print(f"Writing hex to {f.name}")
        f.writelines(image)


def write_jpeg(filename, image):
    if not image[0][16:20] == 'FFD8':
        return
    with open(f'{filename}.jpg', 'wb') as f:
        print(f"Writing jpeg to {f.name}")
        for d in image:
            f.seek(int((d[12:14] + d[10:12]), 16) % 32768)
            f.write(bytes.fromhex(d[16:]))


if __name__ == '__main__':
    main()
