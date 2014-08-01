from dump_trans_data_v1 import dump_trans
import generic_tools

def get_data(database, dataset_id, release, host, port, user, pword):
#
# Calls a function to dump the image data from the TraP database into a CSV file
#
    if release == 'm':
        dump_trans(database,dataset_id, 'monetdb', host, port, user, pword)
        return
    elif release == 'p':
        dump_trans(database,dataset_id, 'postgresql', host, port, user, pword)
        return
    else:
        print 'This script is for either MonetDB (m) or Postgres (p) databases, please specify m or p.'
        exit()

def read_src_lc(sources):
    runcat=0
    new_source={}
    frequencies=[]
    for a in range(len(sources)):
        new_runcat=sources[a][6]
        new_freq=int((float(sources[a][5])/1e6)+0.5)
        if new_runcat != runcat:
            runcat=new_runcat
            new_source[runcat]=[sources[a]]
        else:
            new_source[runcat]=new_source[runcat]+[sources[a]]
        if new_freq not in frequencies:
            frequencies.append(new_freq)
    return frequencies, new_source

def collate_trans_data(new_source,frequencies,transients):
    trans_data=[]
    bands={}
    for freq in frequencies:
        for keys in new_source.keys():
            flux=[]
            flux_err=[]
            date=[]
            band=[]
            for b in range(len(new_source[keys])):
                if int((float(new_source[keys][b][5])/1e6)+0.5)==freq:
                    band.append(new_source[keys][b][11])
                    flux.append(float(new_source[keys][b][3]))
                    flux_err.append(float(new_source[keys][b][4]))
            bands[freq]=band
    ### Calculate the ratios...
            avg_flux_ratio = [x/(sum(flux)/len(flux)) for x in flux]
    ### Collate and store the transient parameters (these are across all the pipeline runs for the final figures)
            for n in range(len(transients)):
                if keys == transients[n][5] and transients[n][9] in bands[freq]:
                    trans_data.append([transients[n][4], float(transients[n][3]), float(transients[n][6]), float(transients[n][11]), max(flux), max(avg_flux_ratio),freq,len(flux),transients[n][9]])
    print 'Number of transients in sample: '+str(len(trans_data))
    return trans_data

def format_data(database, dataset_id, release,host,port):
    get_data(database, dataset_id, release,host,port)
    transients = generic_tools.extract_data('ds_'+str(dataset_id)+'_transients.csv')
    sources = generic_tools.extract_data('ds_'+str(dataset_id)+'_sources.csv')
    frequencies, new_source = read_src_lc(sources)
    trans_data = collate_trans_data(new_source,frequencies,transients)
    output3 = open('ds'+str(dataset_id)+'_trans_data.txt','w')
    output3.write('#Trans_id, eta_nu, signif, V_nu, flux, fluxrat, freq, dpts, trans_type \n')
    for x in range(len(trans_data)):
        string='%s' % ', '.join(str(val) for val in trans_data[x])
        output3.write(string+'\n')
    output3.close()
    print 'Data extracted and saved'
    return
