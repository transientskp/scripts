#!/usr/bin/python
import coords as C
import optparse

def main(opts,args):
    max_sep_cutoff = opts.max_sep_cutoff
#Check for transient associations across all images 
    f = open('transients.txt','r')
    lines=f.readlines()
    f.close()
    lines2=[]
    outtext = ['%d %s' % (i, line) for i, line in enumerate(lines)]
    g = open('transients.txt','w')
    g.writelines(str("".join(outtext)))
    g.close()
    f = open('transients.txt','r')
    lines=f.readlines()
    f.close()
    f2 = open('transients.txt','a')
    for line in lines:
        assoc=[]
        n=0
        info=line.split(' ')
        x1 = C.Position((float(info[1]), float(info[2])))
        for line2 in lines:
            info2=line2.split(' ')
            x2 = C.Position((float(info2[1]), float(info2[2])))
            posdif = x1.angsep(x2)
            if posdif < max_sep_cutoff:
                if info[0] != info2[0]:
                    assoc.append(info2[0])
        if assoc:
            f2.write('Transients associated! '+str(info[0])+' and '+str(", ".join(assoc))+'\n')
    f2.close()

opt = optparse.OptionParser()
opt.add_option('-s','--max_sep_cutoff',help='The maximum separation allowed for associated sources (degrees)',default='0.05',type='float')

opts,args = opt.parse_args()

if len(args) != 0: 
	print 'Need required argument max sep'
else:
	main(opts,args)
