import pickle
import gzip

def save_img_mdata(path, imdata, segments, nseg):
    '''
    Save the image metadata: the image name and the oversegmentation
    (1..N indicate segments) into a file using pickle and compress it
    with gzip.
    '''
    with gzip.open(path, 'wb') as f:
        mdata = { 
            "imdata"   : imdata,
            "nseg"     : nseg, # segments.max() + 1,
            "segimage" : segments
        }
        pickle.dump(mdata, f)

def add_lab_mdata(path, labels):
    obj = load_mdata(path)
    obj["labels"] = labels
    save_obj_mdata(path, obj)

def save_obj_mdata(path, obj):
    '''
    Save the object metadata into a file using pickle and compress it
    with gzip.
    '''
    # fname = obj['name'] if obj.has_key('name') else "obj_mdata"
    with gzip.open(path, 'wb') as f:
        pickle.dump(obj, f)

def load_mdata(path):
    '''
    Restore image metadata from the 'fname' file.
    '''
    with gzip.open(path, 'rb') as f:
        obj = pickle.load(f)
        return obj