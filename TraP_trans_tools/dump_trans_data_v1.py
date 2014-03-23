#!/usr/bin/env python
"""A specific example of how one might access the MonetDB database.

Try running with flag '--help' for information on the command line options.

"""

import optparse
import sys
import tkp.config
import os
import tkp.config
import tkp.db
import csv

def dump_trans(dbname, dataset_id, engine, host, port):
    tkp.db.Database(
        database=dbname, user=dbname, password=dbname,
        engine=engine, host=host, port=port
    )

    #Note it is possible to query the database using the python routines 
    #in tkp.database.utils.generic, without any knowledge of SQL.
    #But for the data requested here it's much easier to use proper queries.
    transients_query = """\
    SELECT  tr.*
           ,rc.dataset
           ,rc.wm_ra
           ,rc.wm_decl
    FROM transient tr
         ,runningcatalog rc
         ,runningcatalog_flux rf
    WHERE tr.runcat = rc.id
      AND rf.runcat = rc.id
      AND tr.band = rf.band
      AND rc.dataset = %s
    """
    cursor = tkp.db.execute(transients_query, (dataset_id,))
    transients = tkp.db.generic.get_db_rows_as_dicts(cursor)
    print "Found", len(transients), "transients"

    sources_query = """\
    SELECT  im.taustart_ts
            ,im.tau_time
            ,ex.f_int
            ,ex.f_int_err
            ,ax.xtrsrc
            ,rc.id as runcatid
            ,rc.dataset
            ,rc.wm_ra
            ,rc.wm_decl
            ,rf.avg_f_int
            ,rf.avg_f_int_sq
            ,im.freq_eff
    FROM extractedsource ex
         ,assocxtrsource ax
         ,image im
         ,runningcatalog rc
         ,runningcatalog_flux rf
    WHERE rf.runcat = rc.id
      and ax.runcat = rc.id
      AND ax.xtrsrc = ex.id
      and ex.image = im.id
      AND rc.dataset = %s
      ORDER BY rc.id
    """
    cursor = tkp.db.execute(sources_query, (dataset_id,))
    sources = tkp.db.generic.get_db_rows_as_dicts(cursor)

    print "Found", len(sources), "source datapoints"

    outfile_prefix = './ds_' + str(dataset_id) + '_'
    dump_list_of_dicts_to_csv(transients, outfile_prefix + 'transients.csv')
    dump_list_of_dicts_to_csv(sources, outfile_prefix + 'sources.csv')

    return 0

def handle_args():
    """
    Default values are defined here.
    """
    usage = """usage: %prog [options] dataset_id"""
    parser = optparse.OptionParser(usage)

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    print "Grabbing data for dataset id:", args[0]
    return options, int(args[0])

def dump_list_of_dicts_to_csv(data, outfile):
    if data:
        with open(outfile, 'w') as fout:
            dw = csv.DictWriter(fout, fieldnames=sorted(data[0].keys()))
            dw.writerows(data)
