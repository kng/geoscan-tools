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


def main():
    tf1 = '%Y-%m-%dT%H:%M:%SZ'
    tf2 = '%Y-%m-%d %H:%M:%S'
    parser = argparse.ArgumentParser(description='Search SatNOGS DB export for images')
    parser.add_argument('infile', help="Input file with frames")
    parser.add_argument('-o', '--outfile', default='out', help='Output file')
    gr1 = parser.add_mutually_exclusive_group()
    gr1.add_argument('-s', '--start', action='store_true', help="List START frames, then exit")
    gr1.add_argument('-e', '--end', action='store_true', help="List END frames, then exit")
    parser.add_argument('-m', '--match', default='', help='What to match in END frame')
    parser.add_argument('-d', '--dist', type=int, default=100, help='Search distance in rows to next frame (def: 100)')
    parser.add_argument('-n', '--skip', type=int, default=0, help='Skip this many END frames')
#    parser.add_argument('--time_start', type=lambda s: datetime.strptime(s, tf1),
#                        help='Start is greater than or equal to YYYY-mm-ddThh:mm:SSZ')
#    parser.add_argument('--time_end', type=lambda s: datetime.strptime(s, tf1),
#                        help='End is less than or equal to')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help="Increase verbosity")
    args = parser.parse_args()
    args.outfile += '_' + str(args.skip)
    if args.match:
        args.outfile += '_' + args.match
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
            if len(d[1]) == 128 and d[1][:8] in D_ANY:
                data.append({'ts': datetime.strptime(d[0], tf2),
                             'cmd': d[1][:8],
                             'addr': int((d[1][12:14] + d[1][10:12]), 16) % 32768,
                             'header': d[1][:16],
                             'payload': d[1][16:]})
            elif args.verbosity >= 2:
                print("Skipped row with wrong length: {}".format(len(d[1])))
        elif args.verbosity >= 1:
            print("Row is missing '|', wrong format?")

    if args.start or args.end:
        print('# Time             | address   | header         | payload')
        for row in data:
            if (args.start and row['cmd'] == D_START and row['addr'] >= 32000) \
                    or (args.end and row['cmd'] == D_END and row['addr'] >= 32000):
                print(f"{row['ts'].strftime(tf1)} addr {row['addr']:#5}: {row['header']} {row['payload']}")
        exit(0)

    print(f"Processing {len(data)} valid frames...")
    addr = skipped = 0
    line = args.skip
    lastfound = -1
    framelen = 56
    frameestimate = -1
    image = []
    while line < len(data):
        if lastfound < 0 and data[line]['cmd'] == D_END and data[line]['addr'] >= 32000 \
                and data[line]['payload'].startswith(args.match):
            #  (args.time_end and args.time_end < data[i]['ts']):
            if args.skip > 0:
                args.skip -= 1
                line += 1
                if args.verbosity >= 2:
                    print('Skipping to next END frame')
                continue
            print('End frame found at line: {}, addr: {}'.format(line, data[line]['addr']))
            frameestimate = ceil((data[line]['addr'] + framelen) / framelen)
            print(f"Estimated amount of frames {frameestimate}")
            image.append(data[line]['header'] + data[line]['payload'] + '\n')
            addr = data[line]['addr'] - framelen
            lastfound = line
            line = max(0, line - args.dist)
        if lastfound >= 0 and abs(data[line]['addr'] - addr) < framelen:
            if args.verbosity >= 1:
                print(f"Found addr {addr}, at line {line}")
            image.append(data[line]['header'] + data[line]['payload'] + '\n')
            lastfound = line
            addr = data[line]['addr'] - framelen
            line = max(0, line - args.dist)
        if lastfound >= 0 and line - lastfound > args.dist:
            if args.verbosity >= 1:
                print('Frame addr {} not found, skip to next.'.format(addr))
            skipped += 1
            line = max(0, lastfound - args.dist)
            addr -= framelen
        if addr < 0:
            break
        line += 1
    print(f"Last line used: {lastfound}")

    image.reverse()
    with open('{}.raw'.format(args.outfile), 'w') as rawfile:
        print(f"Writing {rawfile.name} with {len(image)} frames, {skipped} skipped, "
              f"estimated missing {frameestimate - len(image)}.")
        rawfile.writelines(image)


if __name__ == '__main__':
    main()
