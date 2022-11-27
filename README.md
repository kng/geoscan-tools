# geoscan-tools
Process frames from satellite Geoscan-Edelveis

## Description
The satellite can send frames that are part of bigger files. This program makes an attempt at solving this.

## Useage

```
usage: process_frames <infile> [-h] [-o OUTFILE] [-k] [-r] [-s] [-v]

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
  -v, --verbosity       Increase verbosity
```
The outfile default name is the same as input file, with `_0.dat` `_1.jpg` etc appended.<br>
KISS format of the input, used for `gr_satellites ... --kiss_out result.kiss` or similar.<br>
Raw mode outputs additional files with the raw frames for each of the outputs.<br>
Single mode accumulates all frames in a single file, useful when combining transmissions.<br>
Verbosity increases with the amount of v's used, `-vvv` is quite chatty.<br>

## Examples
Example with `geoscan-mon241122-0954.txt` posted on the [community forum](https://community.libre.space/t/geoscan-edelveis-mission/9644/104).

```
$ ./process_frames.py geoscan-mon241122-0954.txt -o test
Writing to: test_0.dat
Writing to: test_1.dat
Writing to: test_2.jpg
Writing to: test_3.dat
```
By looking at the files it looks like 0 and 2 are similar, and 1 and 3 also pretty similar.
This can be done with `hexdump -v -C test_0.dat` and comparing, there's probably better tools out there.
So to further process this we can enable raw output which takes all the raw frames and puts them in to a file.

```
$ ./process_frames.py geoscan-mon241122-0954.txt -o test -r
Writing to: test_0.dat
Raw file to: test_0.raw
Writing to: test_1.dat
Raw file to: test_1.raw
Writing to: test_2.jpg
Raw file to: test_2.raw
Writing to: test_3.dat
Raw file to: test_3.raw
```

The two files of interest can be concatenated to a new file and processed in single-mode:
```
$ cat test_0.raw test_2.raw > geoscan.raw
$ ./process_frames.py geoscan.raw -s
Writing to: geoscan.jpg
```

Result:<br>
![geoscan](geoscan.jpg)
