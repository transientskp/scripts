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

def main(dataset_id):

    config_parset = tkp.config.initialize_pipeline_config(
                             os.path.join(os.getcwd(), "pipeline.cfg"),
                             job_name="Script: Dump image data")

    db_config = tkp.config.database_config(config_parset, apply=True)

    sources_query = """\
    SELECT  im.id
            ,im.freq_eff
            ,im.url
            ,im.taustart_ts
            ,sr.centre_ra
            ,sr.centre_decl
            ,r.comment
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

    outfile_prefix = './ds_' + str(ds_id) + '_'
    dump_list_of_dicts_to_csv(sources, outfile_prefix + 'images.csv')

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


if __name__ == "__main__":
    options, ds_id = handle_args()
    sys.exit(main(ds_id))
