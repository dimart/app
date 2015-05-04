from flask import Flask, url_for, jsonify, request, flash, abort, json
from werkzeug import secure_filename

from skimage import io
from scripts.segment import segment, SegType
from scripts.util import save_img_mdata, add_lab_mdata
import numpy as np

import os, uuid

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Ground = 1
# Vertical = 2
# Sky = 3

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/api/1.0/get_images')
def send_images():
    abort(404)
    return

@app.route('/api/1.0/send_labels', methods=['POST'])
def process_labels():
    jfile = request.json

    fname = str(uuid.uuid5(uuid.NAMESPACE_DNS, secure_filename(jfile['imageName'])))
    path  = os.path.join(app.config['UPLOAD_FOLDER'], fname)
    if (not os.path.isfile(path)):
        abort(404)

    labs = np.array(jfile["labels"])
    add_lab_mdata(path, labs)
    return "Success", 200

# Route that will process the AJAX request,
# save image, segment it and return the
# result as a proper JSON response (Content-Type, etc.)
@app.route('/api/1.0/process_image', methods=['POST'])
def process_image():
    file = request.files['file']

    if not file and not allowed_file(file.filename):
        return jsonify(error="Not allowed file format")

    filename = str(uuid.uuid5(uuid.NAMESPACE_DNS, secure_filename(file.filename)))
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename);
    # if (os.path.isfile(fname)):
    file.save(path + '_temp')
    file.close()

    # Segment the image
    img      = io.imread(path + '_temp')
    segments = segment(img)
    segnum   = len(np.unique(segments))

    os.remove(path + '_temp')
    save_img_mdata(path, img, segments, segnum)

    fseg      = segments.flatten().tolist()
    h, w, nc  = img.shape

    alpha = np.zeros(w * h).reshape(h, w)
    imgData = np.dstack((img, alpha)).flatten().tolist()

    return jsonify(width = w, height = h, nc = nc, \
                   indexMap = fseg, size = segnum, \
                   rgbData = imgData)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    # app.run(host="0.0.0.0")
    app.run(debug=True)