#!/bin/bash
declare -x EXTRA="--disable_dc_block --throttle --samp_rate 48e3"
#declare -x EXTRA="--disable_dc_block"
declare -x NORAD=53385
FILES=(satnogs_*.ogg)

demod() {
    F=${1%.*}
    D=${F#*_*_}
    B=${D//-/:}
    K=$F.kiss
    L=$F.log
    DF=${D:0:11}${B:11:8}
    gr_satellites "$NORAD" --wavfile "$1" --kiss_out "$K" --start_time "$DF" $EXTRA > "$L"
    kiss_satnogs.py "$K" -x -d "$F"
}
export -f demod

parallel -j20 --progress demod {} ::: "${FILES[@]}"

