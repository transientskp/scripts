#!/bin/bash
#
#
#
# Author: Antonia Rowlinson
# E-mail: b.a.rowlinson@uva.nl

export PYTHONPATH=$PYTHONPATH:/home/rowlinson/lib/python2.6/site-packages
old_IFS=$IFS
search_radius=`cat find_flash.parset | grep 'search_radius=' | sed -e 's/search_radius=//g'`
flux_limit=`cat find_flash.parset | grep 'flux_limit=' | sed -e 's/flux_limit=//g'`
flux_ratio=`cat find_flash.parset | grep 'flux_ratio=' | sed -e 's/flux_ratio=//g'`
abit=`cat find_flash.parset | grep 'systematic_error=' | sed -e 's/systematic_error=//g'`
PYSE_detection=`cat find_flash.parset | grep 'PYSE_detection=' | sed -e 's/PYSE_detection=//g'`
PYSE_analysis=`cat find_flash.parset | grep 'PYSE_analysis=' | sed -e 's/PYSE_analysis=//g'`
PYSE_grid=`cat find_flash.parset | grep 'PYSE_grid=' | sed -e 's/PYSE_grid=//g'`
PYSE_margin=`cat find_flash.parset | grep 'PYSE_margin=' | sed -e 's/PYSE_margin=//g'`
PYSE_radius=`cat find_flash.parset | grep 'PYSE_radius=' | sed -e 's/PYSE_radius=//g'`

list=$@
echo Sourcefinder  > find_flash.log
date >> find_flash.log
    
for n in $list; do
    echo $n
    echo Fits file being analysed: $fitsfile >> find_flash.log
    date >> find_flash.log
    IFS=$old_IFS
    fits=$n
    fits=`echo $fits | sed -e 's/.fits//g'`
    fitsfile=$fits
    pysefile=${fitsfile}.csv
    skymodel=${fitsfile}.skymodel    
    declare RESULT=$(/home/rowlinson/scripts/fits_info.py ${fitsfile}.fits)
    stuff=$(eval echo $RESULT)
    IFS=" "
    set -- $stuff
    numbers=( $@ )
    echo Making skymodel >> find_flash.log
    date  >> find_flash.log
    gsm.py ${skymodel} ${numbers[0]} ${numbers[1]} ${search_radius} ${flux_limit}
    echo Running PySE  >> find_flash.log
    date  >> find_flash.log
    /home/swinbank/sourcefinder/tkp/bin/pyse --detection=${PYSE_detection} --analysis=${PYSE_analysis} --grid=${PYSE_grid} --margin=${PYSE_margin} --csv --regions --deblend --radius=${PYSE_radius} ${fitsfile}.fits
    echo PySE Complete and running source comparison script >> find_flash.log
    date  >> find_flash.log
    echo /home/rowlinson/scripts/find_flash_script.py ${skymodel} -a ${abit} -p ${pysefile} -s ${numbers[2]} -x ${numbers[5]} -r ${numbers[0]} -d ${numbers[1]} -f ${flux_limit} -y ${numbers[2]} -z ${numbers[3]} -q ${numbers[4]} -g $flux_ratio -o ${fitsfile}.pdf
    /home/rowlinson/scripts/find_flash_script.py ${skymodel} -a ${abit} -p ${pysefile} -s ${numbers[2]} -x ${numbers[5]} -r ${numbers[0]} -d ${numbers[1]} -f ${flux_limit} -y ${numbers[2]} -z ${numbers[3]} -q ${numbers[4]} -g $flux_ratio -o ${fitsfile}.pdf
    echo Source comparison script completed >> find_flash.log
    date  >> find_flash.log
done
