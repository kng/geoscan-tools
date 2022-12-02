#!/usr/bin/env python3
import requests
import os
import argparse
from datetime import datetime, timedelta


def main():
    tf = '%Y-%m-%dT%H:%M:%SZ'
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--norad', default='', help='Satellite norad cat id')
    parser.add_argument('-u', '--uuid', default='', help='Transmitter uuid')
    parser.add_argument('-s', '--start', required=True, type=lambda s: datetime.strptime(s, tf),
                        help='Start is greater than or equal to YYYY-mm-ddThh:mm:SSZ')
    parser.add_argument('-e', '--end', type=lambda s: datetime.strptime(s, tf),
                        help='End is less than or equal to')
    parser.add_argument('-d', '--duration', default='60', type=int, help='End time after start (minutes)')
    parser.add_argument('-w', '--withsignal', help='Only observations vetted with signal')
    parser.add_argument('--dryrun', action='store_true', help='Dry run, get list of files but no download')
    args = parser.parse_args()
    if not len(args.norad) > 0 and not len(args.uuid) > 0:
        print('Select Norad ID or transmitter UUIC')
        parser.print_help()
        exit(1)
    if not args.end:
        args.end = args.start + timedelta(minutes=args.duration)

    payload = []
    page = 1
    while True:
        print(f'Fetching page {page}')
        try:
            r = requests.get('https://network.satnogs.org/api/observations/'
                             f'?page={page}&format=json'
                             f'&transmitter_uuid={args.uuid}&satellite__norad_cat_id={args.norad}'
                             f'&start={args.start.strftime(tf)}&end={args.end.strftime(tf)}').json()
            payload.extend([i['payload'] for i in r if i['payload']])
            if len(r) < 25:
                break
            page += 1
        except Exception as e:
            print(f'Request failed: {e}')
            break

    print(f'Fetching {len(payload)} files...')
    for i in payload:
        print(f'Downloading {i}')
        if not args.dryrun:
            download_file(i)


def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        if os.path.isfile(local_filename) and \
           os.path.getsize(local_filename) == int(r.headers['Content-Length']):
            return local_filename
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=pow(2, 16)):
                f.write(chunk)
    return local_filename


if __name__ == '__main__':
    main()
