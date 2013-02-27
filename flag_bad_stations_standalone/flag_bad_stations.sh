#!/bin/bash
# Author: A. Rowlinson
# E-mail: b.a.rowlinson@uva.nl

declare -a BAD_STATION_LIST
declare -i ctr=0 # length of BAD_STATION_LIST 
args=("$@")
measurement_set=${args[0]}
echo $measurement_set

echo "Flagging bad stations" 
rm -rf stats
~rowlinson/scripts/asciistats.py -i ${measurement_set} -r stats > asciistats.txt
~rowlinson/scripts/statsplot.py -i `pwd`/stats/${measurement_set}.stats -o statsplots > statsplot.txt
for station in `grep True$ statsplots.tab | cut -f2`; do
    echo Bad Station: ${station}
    BAD_STATION_LIST[$((ctr++))]=${station}
done
    
if [ ${BAD_STATION_LIST} ]; then
    FILTER=`echo "!${BAD_STATION_LIST[*]}" | tr '\n' ' ' | sed 's/[ \t]*$//'| sed -e's/ /; !/g'`
else
    FILTER=""
fi

msselect in=${measurement_set} out=${measurement_set}.flag baseline="${FILTER}" deep=True > msselect.log 2>&1
