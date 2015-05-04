import pickle
import gzip

def save_seg_mdata(imname, segments):
    '''
    Save the image metadata: the image name and the oversegmentation
    (1..N indicate segments) into a file using pickle and compress it
    with gzip.
    '''
    with gzip.open('{0}_mdata'.format(imname), 'wb') as f:
        mdata = { 
            "imname"   : imname,
            "nseg"     : seg.max() + 1,
            "segimage" : segments
        }
        pickle.dump(mdata, f)

def save_obj_mdata(obj):
    '''
    Save the object metadata into a file using pickle and compress it
    with gzip.
    '''
    fname = obj['name'] if obj.has_key('name') else "obj_mdata"
    with gzip.open('{0}'.format(fname), 'wb') as f:
        mdata = obj
        pickle.dump(mdata, f)

def load_mdata(fname):
    '''
    Restore image metadata from the 'fname' file.
    '''
    with gzip.open(fname,'rb') as f:
        obj = pickle.load(f)
        return obj