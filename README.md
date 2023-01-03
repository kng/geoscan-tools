# geoscan-tools
Process frames from satellite Geoscan-Edelveis

## Description
The satellite can send frames that are part of bigger files. This program makes an attempt at solving this.

## Installation
Clone this repo with `git clone https://github.com/kng/geoscan-tools.git` <br>
Either copy the scripts you want to use to a directory in PATH, or set path to the directory where the scripts are.<br>
An easy route is to use the Makefile, just type `make install` and it will put it in `~/.local/bin/` by default.<br>
To change the installation path, use PREFIX, and sudo if permissions is required: 
`sudo make PREFIX=/usr/local/bin install`

Please read the [GUIDE](GUIDE.md) for detailed examples on how to use the scripts.

## Useage: process_simple
The `process_simple.py` is very straightforward, it takes a single argument which is the input file.
The output is named the same as input but with `.jpg` as extension.
It reqires frames from a single image, but doesn't care if there's duplicates or the order is wrong.

## Useage: process_frames
```
usage: process_frames <infile> [-h] [-o OUTFILE] [-k] [-r] [-s] [--half] [-v]

Process images from geoscan frames

positional arguments:
  infile                Input file with frames (default in hex)

options:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Output file prefix
  -k, --kiss            Input file format: KISS
  -r, --raw             Store raw frames
  -s, --single          Write to single file, accumulating data
  --half                Switch to 16k blocks, 32k default for jpeg
  -v, --verbosity       Increase verbosity
```
The outfile default name is the same as input file, with `_0.dat` `_1.jpg` etc appended.<br>
KISS format of the input, used for `gr_satellites ... --kiss_out result.kiss` or similar.<br>
Raw mode outputs additional files with the raw frames for each of the outputs.<br>
Single mode accumulates all frames in a single file, useful when combining transmissions.<br>
Verbosity increases with the amount of v's used, `-vvv` is quite chatty.<br>

## Useage: db_search
```
usage: db_search.py [-h] [-o OUTFILE] [-s | -e] [-m MATCH] [-d DIST] [-n SKIP] [-a] [-v] infile

Search SatNOGS DB export for images

positional arguments:
  infile                Input file with frames

options:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Output file
  -s, --start           List START frames, then exit
  -e, --end             List END frames, then exit
  -m MATCH, --match MATCH
                        What to match in END frame
  -d DIST, --dist DIST  Search distance in rows to next frame (def: 100)
  -n SKIP, --skip SKIP  Skip this many END frames
  -a, --all             Loop through entire file
  -v, --verbosity       Increase verbosity
```
This program is made to search a DB Export from SatNOGS for start/end frames and manage the data
when it's jumbled together and hard to manually cut to contain a single image.

## Examples
Example with `geoscan-mon241122-0954.txt` posted on the [community forum](https://community.libre.space/t/geoscan-edelveis-mission/9644/104).

```
$ ./process_frames.py geoscan-mon241122-0954.txt -o test
Writing to: test_0.dat
Writing to: test_1.jpg
```
By looking at the files it looks like 0 and 2 are similar, and 1 and 3 also pretty similar.
This can be done with `hexdump -v -C test_0.dat` and comparing, there's probably better tools out there.
So to further process this we can enable raw output which takes all the raw frames and puts them in to a file.

```
$ ./process_frames.py geoscan-mon241122-0954.txt -o test -r
Writing to: test_0.dat
Raw file to: test_0.raw
Writing to: test_1.jpg
Raw file to: test_1.raw
```

The two files of interest can be concatenated to a new file and processed in single-mode:
```
$ cat test_0.raw test_2.raw > geoscan.raw
$ ./process_frames.py geoscan.raw -s
Writing to: geoscan.jpg
```

Result:<br>
![geoscan](geoscan.jpg)
