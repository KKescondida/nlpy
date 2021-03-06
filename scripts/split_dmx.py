#!/usr/bin/python

"""
Created on Mon Oct  8 19:35:00 2012

@author: ilya

Silly little script to split a demultiplexed fastq file produced
by qiime package into individual sample files (also fastq)

split_libraries_fastq function prepends a string to the read id
constructed from the sample_id and the read no.

"""

MAX_SAMPLES = 12 # Maximum number of multiplexed samples in a lane

infile = 'seq.fastq'
# To keep track of opened output files and close them when done
outfiles = {} 
# For stats - keeps track of the number of reads in each file
counts = {}

def get_next_read(handle):
    '''
    Here we assume the file is properly formatted fastq
    and read all four lines at once.
    '''
    try: # TODO: Use fastq parser instead!
        r_id = handle.readline()
        r = handle.readline()
        plus = handle.readline()
        q = handle.readline()
    except IOError:
        return None
    return {'read_id': r_id, 'read_seq': r, 'read_q' :q,}
    
def write_fastq(handle, **kwargs):
    '''
    Writes fastq record into the file given by handle.
    The record is constructed from kwargs.    
    '''
    template = '{read_id}\n{read-seq}\n+\n{read_q}'
    handle.write(template.format(
        read_id=kwargs.get('read_id','NONE'),
        read_seq=kwargs.get('read_seq','NONE'),
        read_q=kwargs.get('read_q','NONE'))
        )

def get_sample_id(header):
    '''
    Extracts a sample_id from fastq file generated by qiime
    split_libraries_fastq.py script.
    '''
    qiime_id = header.split()[0]
    return qiime_id.split('_')[0][1:]

def print_stat(total):
    print "Summary"
    print "Total reads processed:\t%d" % total
    for (sample, count) in counts.items():
        print "Sample: %s\t%d reads" % (sample, count)

total_reads = 0
with open(infile) as fq:
    while True:
        next_read = get_next_read(fq)
        if not next_read:
            break
        total_reads += 1
        if total_reads % 10000 == 0:
            print "Processed\t%d reads so far" % total_reads
        sample_id = get_sample_id(next_read.get('read_id'))
        if outfiles.has_key(sample_id):
            f = outfiles.get(sample_id)
            counts[sample_id] += 1
        elif len(outfiles) < MAX_SAMPLES:
            print "New sample [%i]:\t%s" % (len(outfiles)+1,sample_id)
            f = open(sample_id+'.fastq', 'w')
            outfiles.update({sample_id: f,})
            counts.update({sample_id: 0,})
        else:
            # We've reached maximum number of samples per lane
            # and still got a new id. Ignore it.
            continue
        write_fastq(f, next_read)
        
# Clean-up
print "Cleaning up ..."
for (k,v) in outfiles.items():
    print "Closing file for sample:\t %s" % k
    v.close()
    
print_stat(total_reads)
print "Done."
