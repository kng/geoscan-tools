# Demodulating images from Geoscan-Edelveis
###### By SA2KNG 2023-01-03

This is a quick guide on two ways to demodulate images from 
[geoscan-edelveis](https://dashboard.satnogs.org/d/9DnJFFO4z/geoscan-edelveis).

What you will need is the frames from one image dump, either by observing the satellite yourself or getting the frames
from other [observations](https://network.satnogs.org/observations/?future=0&bad=0&failed=0&norad=53385).<br>
Please see the [community thread](https://community.libre.space/t/geoscan-edelveis-mission/9644) for more info on this.

The scripts required are found in this repo, additionally you will need 
[gr_satellites](https://gr-satellites.readthedocs.io/en/latest/installation_intro.html).<br> 
Optionally [GNU parallel](https://www.gnu.org/software/parallel/) 
and [sox](https://sox.sourceforge.net/) depending on methods and versions.

## Method #1 - download frames from SatNOGS DB
This relies on the stations having demodulated the frames, this is not the case when I'm writing this guide, as the 
stations need [additional demodulation](https://github.com/kng/satnogs_gr-satellites) software running to provide these.

Log in to DB first, then go to the DB [Data Export](https://db.satnogs.org/satellite/QNCD-8954-6090-5430-2718#data) and 
select the timespan needed for the image you’re interested in, getting all the frames will take some time thou. 
This CSV will be emailed to your address. Download this to a working directory, in this example `~/geoscan/`.<br>

To select only the frames of the timestamp of interest, we can use grep to do this:<br>
`grep '^2023-01-02 23' QNCD-8954-6090-5430-2718-1481-20230103T094910Z-week.csv > 2023-01-02_23.csv`<br>

This results in a 840K csv that has all that is needed, a bunch of duplicates as well. We now just run process on it:<br>
`process_simple.py 2023-01-02_23.csv` which results in `Writing image to: 2023-01-02_23.jpg`.<br>

That's it, when the images are separated in time and all the frames are available, this is all that is needed.

## Method #2 - download audio from single observation
First an example of a single station, the incredible Dwingeloo [@radiotelescoop](https://twitter.com/radiotelescoop).
Open the [observation page](https://network.satnogs.org/observations/6969073/) and download the audio at the bottom left
to a working directory, for example `~/geoscan/6969073/`.<br>
Then process it with audiodemod in fast mode, it searches for all files named `satnogs_*.ogg` so it's important to keep
other observation ogg separate:<br>
```commandline
audiodemod.sh 

Found 1 files to process...
running fast demodulation
satnogs_6969073_2023-01-03T08-39-08.ogg
```
This results in a bunch of files, and it's the .csv we want, so run this through process_simple:<br>
```commandline
process_simple.py satnogs_6969073_2023-01-03T08-39-08.csv

Writing image to: satnogs_6969073_2023-01-03T08-39-08.jpg
```
If the observation is this complete this is all that is needed, but the next example uses a lot of stations to possibly 
collect all frames.

## Method #3 - download all observations in selected timeframe 
This method has the advantage of getting frames from stations not demodulating this in the first place, 
althou it is a tiny bit less sensitive due to the lossy ogg format.

Make a working directory for the observation data, for example: `~/geoscan/2022-12-15_15/` and enter it.<br>
Run the audio downloader with either the transmitter UUID or NORAD and the timestamp of interest:<br>
`satnogs_fetch_audio.py -u RzkypM3s5zPQf2PC9iY8Ki -s 2022-12-15T15:00:00Z -d 60`
This will fetch 30 observations from DB, to process them for frames we run audiodemod:<br>
```commandline
audiodemod.sh 

Found 30 files to process...
running fast demodulation
satnogs_6878606_2022-12-15T15-24-01.ogg
satnogs_6878633_2022-12-15T15-23-21.ogg
satnogs_6878639_2022-12-15T15-23-13.ogg
satnogs_6878927_2022-12-15T15-23-13.ogg
.....
```
To process them as one big observation we contatenate the files together:<br>
`cat *.csv > 2022-12-15_15.csv`<br>
And finally run process_simple on that csv:<br>
```commandline
process_simple.py 2022-12-15_15.csv 

Writing image to: 2022-12-15_15.jpg
```

## Additional notes

### audiodemod.sh
The script can be passed a single argument to make it run in realtime: `audiodemod.sh -r`<br>
This makes `gr_satellites` run with --throttle and results in timestamps for the frames being correct, else it gets
bunched up in the short time it takes to run. This is a shortcoming that is oftesn not critical, like when there's only
one image sent. The program GNU parallel is used to run these in - you guessed it - parallel, this is because of the
sum of the observation time is required, and it draws very little cpu, so the main limit is memory. Feel free to adjust
the `-j20` parameter here, it's the number of parallel processes that are allowed at the same time.

### satnogs_fetch_audio.py
```commandline
usage: satnogs_fetch_audio.py [-h] [-n NORAD | -u UUID] -s START [-e END] [-d DURATION] [-w] [--dryrun]

options:
  -h, --help            show this help message and exit
  -n NORAD, --norad NORAD
                        Satellite norad cat id
  -u UUID, --uuid UUID  Transmitter uuid
  -s START, --start START
                        Start is greater than or equal to YYYY-mm-ddThh:mm:SSZ
  -e END, --end END     End is less than or equal to
  -d DURATION, --duration DURATION
                        End time after start (minutes)
  -w, --withsignal      Only observations vetted with signal
  --dryrun              Dry run, get list of files but no download

```