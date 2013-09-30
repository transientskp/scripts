#!/usr/bin/env python
"""A specific example of how one might access the MonetDB database.

Try running with flag '--help' for information on the command line options.

"""

import optparse
import sys
import tkp.config
from tkp.database import DataBase
import tkp.database.utils as dbu
import csv

def main(dbname, dataset_id):
    db = DataBase(name=dbname, user=dbname, password=dbname)

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
    db.execute(sources_query, dataset_id)
    raw_sources_results = db.fetchall()
    sources = convert_results_to_list_of_dicts(raw_sources_results,
                                               db.cursor.description)

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

    dbname_default = tkp.config.config['database']['name']
    parser.add_option("--dbname", default=dbname_default,
                       help="Database name, default: " + dbname_default)

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    print "Grabbing data for dataset id:", args[0]
    return options, args[0]


def convert_results_to_list_of_dicts(raw_results, cursor_description):
    """Simply re-organises the database results into a nicer format."""
    description = dict([(d[0], i) for i, d in enumerate(cursor_description)])
    converted = []
    for row in raw_results:
        converted.append(
          dict([(key, row[column]) for key, column in description.iteritems()]))
    return converted

def dump_list_of_dicts_to_csv(data, outfile):
    if data:
        with open(outfile, 'w') as fout:
            dw = csv.DictWriter(fout, fieldnames=sorted(data[0].keys()))
#            dw.writeheader()
            dw.writerows(data)


if __name__ == "__main__":
    options, ds_id = handle_args()
    sys.exit(main(options.dbname, ds_id))
