#!/usr/bin/python
"""Generate a voevent alert packet from a given transient_id. 

Voevent parser library docs can be found at http://voevent-parse.readthedocs.org

Try running with flag '--help' for information on the command line options.
(Or see function handle_args.)

"""

import optparse
import sys
import csv
import pprint
import datetime

try:
    import tkp.config
except ImportError:
    print """Could not import tkp config, did you run the lofar init.sh?"""
    sys.exit(1)
from tkp.database import DataBase
import tkp.database.utils as dbu

try:
    import voeparse as vp
except ImportError:
    print """Could not import voevent-parse: see http://github.com/timstaley/voevent-parse"""
    sys.exit(1)

#==========================================================================
#All non-transient-specific attributes should be hardcoded in this section:
# (Easy to implement loading from JSON if desired in future)

sender_attributes = {'stream' : 'vovent.lofar.org/tkp_earlyrelease',
                     'who':{
                            'author_ivorn' : 'vovent.lofar.org',
                            'date' : datetime.datetime.now()
                            },
                     'author':{
                               'title':'LOFAR-TKP Early Release Transients',
                               'shortName' :'LOFAR-TKP',
                               },
                     'how':{'descriptions':'Discovered using the TKP TraP.'}
                     }

role = vp.roles.test
#role = vp.roles.observation #Use this in case of real data

#==========================================================================


def main(dbname, transient_id, voe_stream_id, output_filename):
    db = DataBase(name=dbname, user=dbname, password=dbname)
    transient = get_transient_info(db, transient_id)
    print "**********************************"
    print "Extracted the following transient details:"
    pp = pprint.PrettyPrinter()
    pp.pprint(transient)
    print "**********************************"
    print "Will generate VOEvent with following sender attributes:"
    pp.pprint(sender_attributes)
    print "**********************************"

    event = generate_voevent(transient, sender_attributes, voe_stream_id, role)

    print "Here's the raw xml:\n\n"
    print vp.dumps(event)
    print "\n\n"

    with open(output_filename, 'w') as f:
        vp.dump(event, f)

    return 0

def get_transient_info(database, transient_id):
    """Returns a dictionary of transient event attributes"""
    #WARNING WARNING WARNING
    #wm_ra_err / wm_decl_err may not be a good estimate of real position error
    #ToDo: This needs verifying and probably fixing

    transients_query = """\
    SELECT  tr.*
           ,rc.wm_ra as ra_deg
           ,rc.wm_ra_err as ra_err_arcsec
           ,rc.wm_decl as decl_deg
           ,rc.wm_decl_err as decl_err_arcsec
           ,im.taustart_ts as trigger_time
           ,ex.f_peak as trigger_f_peak
           ,ex.f_peak_err as trigger_f_peak_err
           ,ex.f_int as trigger_f_int
           ,ex.f_int_err as trigger_f_int_err
           ,rf.avg_f_peak as mean_f_peak
           ,(rf.avg_weighted_f_peak / avg_f_peak_weight) as weighted_mean_f_peak
           ,rf.avg_f_int as mean_f_int
           ,(rf.avg_weighted_f_int / avg_f_int_weight) as weighted_mean_f_int
           ,rf.f_datapoints
    FROM transient tr
         ,runningcatalog rc
         ,runningcatalog_flux rf
         ,image im
         ,extractedsource ex
    WHERE tr.id = %(transid)s
      AND tr.runcat = rc.id
      AND rf.runcat = rc.id
      AND rf.band = tr.band
      AND ex.id = tr.trigger_xtrsrc
      AND im.id = ex.image
    """
    cursor = database.connection.cursor()
    cursor.execute(transients_query, {'transid':transient_id})
    raw_transient_results = cursor.fetchall()
    transients = convert_results_to_list_of_dicts(raw_transient_results,
                                                  cursor.description)
    assert len(transients) == 1 #sanity check
    return transients[0]

def generate_voevent(transient, sender, stream_id, role):
    event = vp.Voevent(stream=sender['stream'], stream_id=stream_id,
                   role=role)
    vp.set_who(event, **sender['who'])
    vp.set_author(event, **sender['author'])
    vp.add_how(event, **sender['how'])

    pos_err = 3600. * max(transient['ra_err_arcsec'], transient['decl_err_arcsec'])

    sky_posn = vp.Position2D(ra=transient['ra_deg'], dec=transient['decl_deg'],
                             err=pos_err,
                             units=vp.definitions.coord_units.degrees,
                             system=vp.definitions.sky_coord_system.fk5)

    vp.set_where_when(event, coords=sky_posn, obs_time=transient['trigger_time'],
              observatory_location=vp.definitions.observatory_location.geosurface)

    transient_params = transient.copy()

    for k, v in transient.iteritems():
        event.What.append(vp.Param(name=k, value=v))
    return event

def handle_args():
    """
    Default values are defined here.
    """
    usage = """usage: %prog [options] transient_id voevent_stream_id outputname.xml"""
    parser = optparse.OptionParser(usage)

    dbname_default = tkp.config.config['database']['name']
    parser.add_option("--dbname", default=dbname_default,
                       help="Database name, default: " + dbname_default)

    options, args = parser.parse_args()
    if len(args) != 3:
        parser.print_help()
        sys.exit(1)
    print "Generating VOEvent for transient id:", args[0]
    return options, args


def convert_results_to_list_of_dicts(raw_results, cursor_description):
    """Simply re-organises the database results into a nicer format."""
    description = dict([(d[0], i) for i, d in enumerate(cursor_description)])
    converted = []
    for row in raw_results:
        converted.append(
          dict([(key, row[column]) for key, column in description.iteritems()]))
    return converted

if __name__ == "__main__":
    options, (transient_id, stream_id, outputfilename) = handle_args()
    sys.exit(main(options.dbname, transient_id, stream_id, outputfilename))
