#!/usr/bin/env python
"""A specific example of how one might access the MonetDB database.

Try running with flag '--help' for information on the command line options.

"""

import optparse
import sys
import os
import tkp.config
import tkp.db
import csv

def dump_images(dbname,username,password,dataset_id, dataset_id2, engine, host, port):
    tkp.db.Database(
        database=dbname, user=username, password=password,
        engine=engine, host=host, port=port
    )

    sources_query = """\
    SELECT  im.id
            ,im.freq_eff
            ,im.url
            ,im.taustart_ts
            ,im.rb_smaj
            ,im.rb_smin
            ,sr.centre_ra
            ,sr.centre_decl
            ,r.comment
            ,im.rms_qc
    FROM image im
         ,rejectreason rr
         ,rejection r
         ,skyregion sr
    WHERE im.dataset = %s
      AND im.id=r.image
      AND r.rejectreason=rr.id
      AND im.skyrgn=sr.id
      ORDER BY im.id
    """
    cursor = tkp.db.execute(sources_query, (dataset_id,))
    sources = tkp.db.generic.get_db_rows_as_dicts(cursor)
    print "Found", len(sources), "images"
    outfile_prefix = './ds_' + str(dataset_id) + '_'
    dump_list_of_dicts_to_csv(sources, outfile_prefix + 'images.csv')

    if len(sources)==0:
        print "No quality control steps completed, not LOFAR images?"
        print "Querying without rejection tables"
        sources_query = """\
        SELECT  im.id
            ,im.freq_eff
            ,im.url
            ,im.taustart_ts
            ,im.rb_smaj
            ,im.rb_smin
            ,sr.centre_ra
            ,sr.centre_decl
            ,im.rms_qc
        FROM image im
            ,skyregion sr
        WHERE im.dataset = %s
        AND im.skyrgn=sr.id                                                                                                                                 
        ORDER BY im.id
        """
        cursor = tkp.db.execute(sources_query, (dataset_id,))
        sources = tkp.db.generic.get_db_rows_as_dicts(cursor)
        print "Found", len(sources), "images"
        sources = [dict(list(x.items())+[('comment','')]) for x in sources]
        outfile_prefix = './ds_' + str(dataset_id) + '_'
        dump_list_of_dicts_to_csv(sources, outfile_prefix + 'images.csv')

    if dataset_id2!='N':
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
            ,im.url
            ,ex.extract_type
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
        cursor = tkp.db.execute(sources_query, (dataset_id2,))
        sources = tkp.db.generic.get_db_rows_as_dicts(cursor)
        print "Found", len(sources), "source datapoints"
        outfile_prefix = './ds_' + str(dataset_id2) + '_'
        dump_list_of_dicts_to_csv(sources, outfile_prefix + 'sources.csv')

    return 0


def dump_list_of_dicts_to_csv(data, outfile):
    if data:
        with open(outfile, 'w') as fout:
            dw = csv.DictWriter(fout, fieldnames=sorted(data[0].keys()))
            dw.writerows(data)

