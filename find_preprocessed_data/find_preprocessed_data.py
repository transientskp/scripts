#!/usr/bin/python
#
# A script to find the preprocessed data. To be run on lhn001
#
# b.a.rowlinson@uva.nl
#

import os
import sys
import optparse

def main(opts,args):
    obsid=args[0]
    ms_files = os.popen("cexec -p locus: 'du -sh  /data/scratch/lofarsys/*/*"+str(obsid)+"*' | grep MS.dppp ").read()
    if len(ms_files) == 0:
        print 'No data found. Incorrect image id for the beam?'
        exit()
    print ms_files

opt = optparse.OptionParser()
opts,args = opt.parse_args()
if len(args) != 1: 
    print 'Need <obsid>'
    exit()
else:
    main(opts,args)
