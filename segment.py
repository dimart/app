import sys
import argparse
import os
import logging

# Multiple Processes
from functools import partial
from multiprocessing.pool import Pool

# Multithreading
from Queue import Queue
from threading import Thread

import numpy as np

from skimage.segmentation import slic, felzenszwalb
from skimage.segmentation import mark_boundaries
from skimage import io

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

inpath  = "."
outpath = "./results"
verbose = False

# SEGMENTATION PARAMETERS

# 'scale' sets an observation level,
# higher scale means less and larger segments.
max_scale  = 150
min_scale  = 10
scale_step = 20
scales     = range(min_scale, max_scale + 1, scale_step)

# 'sigma' is the diameter of a Gaussian kernel,
# it is used for smoothing the image prior to segmentation.
# ex: [0.1 ... 0.9]
sigmas = map(lambda x: x / 10.0, range(2, 10, 3))

# 'min_size' minimum component size
mins = range(10, 101, 30)

# END OF SEGMENTATION PARAMETERS

class SegType:
    FW = "Felzenszwalb"
    SLICK = "SLIC"

def parse_args():
  parser = argparse.ArgumentParser(
    description="segment images with different segmentation algorithms and parameters")
  parser.add_argument("segtype", choices=['F', 'S'],
    help="segmentation type can be either 'F' (for Felzenszwalb) or 'S' (for SLICK)")
  parser.add_argument("i", 
    help="path to the input directory")
  parser.add_argument("o", 
    help="path to the output directory")

  parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

  processing_type = parser.add_mutually_exclusive_group()
  processing_type.add_argument("-p", type=int, help="use several processes")
  processing_type.add_argument("-t", type=int, help="use several threads")

  return parser.parse_args()

def make_full_path(path, subfolders):
  res_path = path
  for sf in subfolders:
    res_path += '/[' + str(sf) + ']'
  if not os.path.exists(res_path):
      os.makedirs(res_path)
  return res_path

def segment_image(segtype, save_img, (img, path)):
  logger.info('Process image: {0}'.format(path))
  for scale in scales:
    for sigma in sigmas:
      for min_size in mins:
        fpath = make_full_path(path, [segtype, scale, sigma])

        if segtype == SegType.FW:
          segments = felzenszwalb(img, scale=scale, sigma=sigma, min_size=min_size)
        else:
          segments = slic(img, n_segments=min_size, compactness=scale, sigma=sigma)
        
        segnum  = len(np.unique(segments))

        if verbose:
          logger.info('{0}: num of segments = {1}'.format(str(segtype), segnum))
        
        if (save_img == True):
          fname = fpath \
                  + '/' \
                  + "ms=" + str(min_size) \
                  + "_ns=" + str(segnum) \
                  + ".jpg"
          io.imsave(fname, mark_boundaries(img, segments))

class SegmentationWorker(Thread):
  def __init__(self, queue):
    Thread.__init__(self)
    self.queue = queue

  def run(self):
    while True:
      # Get the work from the queue
      img, segtype, path = self.queue.get()
      segment_image(segtype, True, (img, path))
      self.queue.task_done()

def run_multiple_processes(pnum, segtype):
  pool = Pool(pnum)
  segment = partial(segment_image, segtype, True)
  fnames = filter(lambda f: f[0] != '.', os.listdir(inpath))
  imgs = map(lambda f: io.imread(inpath + '/' + f), fnames)
  pool.map(segment, zip(imgs, map(lambda f: outpath + '/[image]' + f.split('.')[0], fnames)))

def run_multiple_threads(tnum, segtype):
  # Create a queue to communicate with the worker threads
  queue = Queue()

  # Create 'thum' worker threads
  for x in range(tnum):
    worker = SegmentationWorker(queue)
    worker.daemon = True
    worker.start()

  for imname in os.listdir(inpath):
    if (imname[0] == '.'): continue
    img = io.imread(inpath + '/' + imname)
    if (verbose):
      logger.info('Queueing {}'.format(imname))
    queue.put((img, segtype, outpath + '/[image]' + imname.split('.')[0]))

  # Causes the main thread to wait for the queue to finish processing all the tasks
  queue.join()

def main(argv):
  global inpath, outpath, verbose

  args = parse_args()
  inpath, outpath, verbose = args.i, args.o, args.verbose
  segtype = SegType.FW if args.segtype == 'F' else SegType.SLICK

  if (args.p != None):
    logger.info('Running in multiple processes mode with number of processes = {0}'.format(args.p))
    run_multiple_processes(args.p, segtype)
  elif (args.t != None):
    logger.info('Running in multiple threads mode with number of threads = {0}'.format(args.t))
    run_multiple_threads(args.t, segtype)
  else:
    logger.info("Running in single thread, single process mode")
    for imname in os.listdir(inpath):
      if (imname[0] == '.'): continue
      img = io.imread(inpath + '/' + imname)
      segment_image(segtype, True, (img, outpath + '/[image]' + imname.split('.')[0]))

if __name__ == "__main__":
    main(sys.argv)