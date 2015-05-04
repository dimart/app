from segment import segment, SegType
from skimage import io
from skimage.segmentation import mark_boundaries
import os
import numpy as np
import util

inpath  = './in'
segtype = SegType.SLIC
truth   = { 'name' : "GroundTruth" }

# All the possible labels for segments
# Ground   = 1
# Vertical = 2
# Sky      = 3
labels = [1, 2, 3]

# segment number -> [(pi, pj),...,(pl, pk)]
pixelMap = {}

# segment number -> label
labelMap = {}

def display_labels(imdata, segments, segnum, labels):
  pixMap = {}
  for x in xrange(0, segnum):
    pixMap[x] = []

  for i in xrange(0, segments.shape[0]):
    for j in xrange(0, segments.shape[1]):
      pixMap[segments[i,j]].append((i, j))

def update_truth(imname, segments, segnum):
  tobj           = truth[imname] = {}
  tobj['seg']    = segments
  tobj['segnum'] = len(np.unique(segments))
  tobj['labs']   = labelMap
  tobj['pixMap'] = pixelMap

def compute_pixelMap(segments, segnum):
  global pixelMap

  del pixelMap
  pixelMap = {}

  for x in xrange(0, segnum):
    pixelMap[x] = []

  for i in xrange(0, segments.shape[0]):
    for j in xrange(0, segments.shape[1]):
      pixelMap[segments[i,j]].append((i, j))


def assign_label(img, segnum):
  global labelMap

  del labelMap
  labelMap = {}

  for seg in xrange(0, segnum):
    imgcopy = img.copy()
    for pixnum in xrange(0, len(pixelMap[seg])):
      i, j = pixelMap[seg][pixnum]
      imgcopy[i, j, :] = [0, 0, 0]
    io.imshow(imgcopy)
    io.show()
    lab = int(raw_input())
    labelMap[s] = lab
    del imgcopy

def compute_truth(path=inpath):
  for imname in os.listdir(path):
    if (imname[0] == '.'): continue

    img      = io.imread(inpath + '/' + imname)
    segments = segment(img)
    segnum   = len(np.unique(segments))

    print imname, segnum
    compute_pixelMap(segments, segnum)
    assign_label(img, segnum)

    # print pixelMap
    # io.imshow(mark_boundaries(img, segments))
    # io.show()

    update_truth(imname, segments, segnum)

if __name__ == "__main__":
  # compute_truth()
  # util.save_obj_mdata(truth)