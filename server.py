import csv
try:
    import simplejson as json
except ImportError:
    import json
from flask import Flask,request,Response,render_template
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

#app = Flask(__name__,template_folder='.')
app = Flask(__name__)

with open('config.yaml') as fout:
  config = yaml.load(fout,Loader=yaml.FullLoader) 

model = utils.load_model(config)
latent_code = utils.get_encoders(model,config)

@app.route('/')
def renderPage():
	return render_template("index.html")

@app.route('/decode_cae')
def decode_cae():
	#API for decoding.

	#tile_coord = request.args.get('coordinates').strip()
	#tile_x,tile_y = tile_coord

	tile_x,tile_y = (0,0)
	decoded_numpy_image = utils.decode(model,latent_code[tile_x][tile_y])

	#base64 encoding.
	pil_img = Image.fromarray(decoded_numpy_image)
	im_file = BytesIO()
	pil_img.save(im_file, format="JPEG")
	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)

	return im_b64


# @app.route('/')
# def renderPage():
#   return render_template("index.html")



if __name__ == "__main__":
  app.run(debug=True,port=8000)
