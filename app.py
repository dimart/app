from flask import Flask, url_for, jsonify, request, flash, abort, json
from werkzeug import secure_filename

from skimage import io
from scripts.segment import segment, SegType
import numpy as np

import os, uuid

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

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
    pathToImg = os.path.join(app.config['UPLOAD_FOLDER'], "images", fname)
    if (not os.path.isfile(pathToImg)):
        abort(404)

    pathToLabels = os.path.join(app.config['UPLOAD_FOLDER'], "labels", fname) + '.lab'
    with open(pathToLabels, 'w') as file_:
        file_.write(str(jfile["labels"]))

    return "Success", 200

# Route that will process the AJAX request,
# save image, segment it and return the
# result as a proper JSON response (Content-Type, etc.)
@app.route('/api/1.0/process_image', methods=['POST'])
def process_image():
    file = request.files['file']

    if not file and not allowed_file(file.filename):
        return jsonify(error="Not allowed file format.")

    # Save file on the server
    filename = str(uuid.uuid5(uuid.NAMESPACE_DNS, secure_filename(file.filename)))
    path = os.path.join(app.config['UPLOAD_FOLDER'], "images", filename)
    # if (os.path.isfile(fname)):

    file.save(path)
    file.close()

    # Segment the image
    img      = io.imread(path)
    segments = segment(img)
    segnum   = len(np.unique(segments))

    fseg      = segments.flatten().tolist()
    h, w, nc  = img.shape

    print w, h

    alpha = np.zeros(w * h).reshape(h, w)
    imgData = np.dstack((img, alpha)).flatten().tolist()

    return jsonify(width = w, height = h, nc = nc, \
                   indexMap = fseg, size = segnum, \
                   rgbData = imgData)

if __name__ == '__main__':
    # app.run(host="0.0.0.0")
    app.run(debug=True)