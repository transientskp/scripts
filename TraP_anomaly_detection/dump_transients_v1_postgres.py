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

def dump_trans(dbname, dataset_id, engine='postgresql', host='heastrodb', port=5432):
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
    outfile_prefix = './ds_' + str(dataset_id) + '_'
    dump_list_of_dicts_to_csv(transients, outfile_prefix + 'transients.csv')

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
#            dw.writeheader()
            dw.writerows(data)


#if __name__ == "__main__":
#    options, ds_id = handle_args()
#    sys.exit(main(ds_id))
