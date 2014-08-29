#!/usr/bin/env python
"""
Tools to query the database to extract the transient and extracted source tables. Files saved in working directory as "ds_${dataset id}_transients.csv" and "ds_${dataset id}_sources.csv
"""

import tkp.config
import tkp.db
import csv

def dump_trans(dbname, dataset_id, engine, host, port, user, pword):
    tkp.db.Database(
        database=dbname, user=user, password=pword,
        engine=engine, host=host, port=port
    )

    #Note it is possible to query the database using the python routines 
    #in tkp.database.utils.generic, without any knowledge of SQL.
    #But for the data requested here it's much easier to use proper queries.
    transients_query = """\
    SELECT  tr.runcat
           ,tr.newsource_type
    FROM newsource tr
    """
    cursor = tkp.db.execute(transients_query, (dataset_id,))
    transients = tkp.db.generic.get_db_rows_as_dicts(cursor)
    print "Found", len(transients), "new sources"

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
            ,im.band
            ,ax.v_int
            ,ax.eta_int
            ,ax.f_datapoints
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

def dump_list_of_dicts_to_csv(data, outfile):
    if data:
        with open(outfile, 'w') as fout:
            dw = csv.DictWriter(fout, fieldnames=sorted(data[0].keys()))
            dw.writerows(data)
