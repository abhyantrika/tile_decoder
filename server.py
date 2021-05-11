import csv
try:
    import simplejson as json
except ImportError:
    import json
from flask import Flask,request,Response,render_template, send_file
#import psycopg2 # use this package to work with postgresql
import yaml
import pandas as pd
#from sqlalchemy import create_engine
from collections import defaultdict
import re 
import patchify
import utils
import base64
from io import BytesIO
from PIL import Image
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from flask_cors import CORS
import io

from compressai.zoo import bmshj2018_hyperprior

#app = Flask(__name__,template_folder='.')
app = Flask(__name__)
CORS(app)

with open('config.yaml') as fout:
  config = yaml.load(fout,Loader=yaml.FullLoader) 

cae_model = utils.load_cae_model(config)
cae_latent_code = utils.get_encoders_cae(cae_model,config)

compressai_model = utils.load_compress_ai_model(config)
compressai_latent_code = utils.get_encoders_compress_ai(compressai_model,config)


@app.route('/')
def renderPage():
	return render_template("index.html")

@app.route('/decode_cae')
def decode_cae():
	#API for decoding.

	#tile_coord = request.args.get('coordinates').strip()
	#tile_x,tile_y = tile_coord
	x = int(request.args.get('x'))
	y = int(request.args.get('y'))

	tile_x,tile_y = (0,0)
	decoded_numpy_image = utils.decode_cae(cae_model,cae_latent_code[tile_x][tile_y])

	#base64 encoding.
	pil_img = Image.fromarray(decoded_numpy_image)
	im_file = BytesIO()
	pil_img.save(im_file, format="JPEG")
	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)

	return send_file(io.BytesIO(im_b64),mimetype='image/jpeg',attachment_filename="cae_output.jpg")


@app.route('/decode_compressai')
def decode_compressai():
	#API for decoding.

	#tile_coord = request.args.get('coordinates').strip()
	#tile_x,tile_y = tile_coord

	x = int(request.args.get('x'))
	y = int(request.args.get('y'))

	tile_x,tile_y = (0,0)
	decoded_numpy_image = utils.decode_compress_ai(compressai_model,compressai_latent_code[(tile_x+1)*tile_y])

	#base64 encoding.
	pil_img = Image.fromarray(decoded_numpy_image)
	im_file = BytesIO()
	pil_img.save(im_file, format="JPEG")
	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)

	return send_file(io.BytesIO(im_b64),mimetype='image/jpeg',attachment_filename="cpa_output.jpg")



if __name__ == "__main__":
  app.run(debug=False,port=8000)
