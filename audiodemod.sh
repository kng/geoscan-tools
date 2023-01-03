#!/bin/bash

declare -x NORAD=53385
declare -x FILES=(satnogs_*.ogg)

# Use sox to convert ogg to wav, for gnuradio-3.8 which do not use libsndfile
if gnuradio-config-info -v | grep -q '^3.8'; then
    if command -v sox >/dev/null; then
        echo "Using sox to convert ogg to wav"
        declare -x SOX=1
    else
        echo "ERROR: sox missing, please install"
        exit 1
    fi
fi

if ! command -v gr_satellites >/dev/null; then
    echo "ERROR: gr_satellites missing, please install"
    exit 1
fi
if ! command -v kiss_csv.py >/dev/null; then
    echo "ERROR: kiss_csv.py missing, please install"
    exit 1
fi

echo "Found ${#FILES[@]} files to process..."

demod() {
    F=${1%.*}
    D=${F#*_*_}
    B=${D//-/:}
    K=$F.kiss
    L=$F.log
    W=$F.wav
    DF=${D:0:11}${B:11:8}
    if [ -z "$SOX" ]; then
        W="$1"
    else
        sox "$1" "$W"
    fi
    echo "${W}"
    gr_satellites "$NORAD" --wavfile "$W" --kiss_out "$K" --start_time "$DF" $EXTRA > "$L"
    kiss_csv.py "$K"
}
export -f demod

if [ "$1" = "-r" ]; then
    echo "running realtime demodulation"
    declare -x EXTRA="--disable_dc_block --throttle --samp_rate 48e3"
    if ! command -v parallel >/dev/null; then
        echo "ERROR: parallel missing, please install"
        exit 1
    fi
    parallel -j20 --progress demod {} ::: "${FILES[@]}"
else
    echo "running fast demodulation"
    declare -x EXTRA="--disable_dc_block"
    for F in "${FILES[@]}"; do
        demod "$F"
    done
fi

