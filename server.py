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
	hardcoded_grid_x = 32
	hardcoded_grid_y = 33

	x = int(request.args.get('x'))
	y = int(request.args.get('y'))
	
	xSize = int(request.args.get('gridXSize'))
	ySize = int(request.args.get('gridYSize'))
	width = int(float(request.args.get('totalWidth')))
	height = int(float(request.args.get('totalHeight')))
	new_x_size = int(hardcoded_grid_x / xSize)
	new_y_size = int(hardcoded_grid_y / ySize)
	# new_x_size = 600
	# new_y_size = 600
	new_im = Image.new('RGB', (128*(new_x_size), 128*(new_y_size)))
	x_offset = 0
	y_offset = 0
	x_size = 0
	y_size = 0
	for i in range(x * new_x_size, (1+x) * (new_x_size)):
		for j in range(y * new_y_size, (1+y) * new_y_size):
			tile_x, tile_y = (i, j)
			decoded_numpy_image = utils.decode_cae(cae_model,cae_latent_code[tile_x][tile_y])
			pil_img = Image.fromarray(decoded_numpy_image)
			new_im.paste(pil_img, (y_offset, x_offset))
			x_size = pil_img.size[0]
			y_size = pil_img.size[1]

			y_offset += y_size
		x_offset += x_size
		y_offset = 0
	
	im_file = BytesIO()
	new_im.save(im_file, format="JPEG")

	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)

	# tile_x,tile_y = (x,y)
	# decoded_numpy_image = utils.decode_cae(cae_model,cae_latent_code[tile_x][tile_y])

	#base64 encoding.
	# pil_img = Image.fromarray(decoded_numpy_image)
	# im_file = BytesIO()
	# pil_img.save(im_file, format="JPEG")
	# im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	# im_b64 = base64.b64encode(im_bytes)

	res = {"data":im_b64.hex(),"data2":im_bytes.hex()}
	resp = Response(response=json.dumps(res),status=200,mimetype='application/json')
	return resp
	# return send_file(io.BytesIO(im_b64),mimetype='image/jpeg',attachment_filename="cae_output.jpg")


@app.route('/decode_compressai')
def decode_compressai():
	#API for decoding.

	#tile_coord = request.args.get('coordinates').strip()
	#tile_x,tile_y = tile_coord

	hardcoded_grid_x = 32
	hardcoded_grid_y = 33

	x = int(request.args.get('x'))
	y = int(request.args.get('y'))
	
	xSize = int(request.args.get('gridXSize'))
	ySize = int(request.args.get('gridYSize'))
	width = int(float(request.args.get('totalWidth')))
	height = int(float(request.args.get('totalHeight')))

	new_x_size = int(hardcoded_grid_x / xSize)
	new_y_size = int(hardcoded_grid_y / ySize)
	# new_x_size = 600
	# new_y_size = 600
	new_im = Image.new('RGB', (128*new_x_size , 128*(new_y_size)))
	# new_im = Image.new('RGB', (128*new_x_size + 5, 128*new_y_size +5))
	x_offset = 0
	y_offset = 0
	x_size = 0
	y_size = 0

	starting_idx = (x * new_x_size + 1) * (y * new_y_size)
	ctr = 0 
	for idx, i  in enumerate(range(x * new_x_size, (1+x) * (new_x_size))):
		# starting_idx = (i+1) * ((y)  * new_y_size)
		starting_idx = (x * new_x_size + 1 + (idx*2)) * (y*new_y_size)
		for idx2, j in enumerate(range(y * new_y_size, (1+y) * new_y_size)):
			tile_x, tile_y = (i, j)
			decoded_numpy_image = utils.decode_compress_ai(compressai_model,compressai_latent_code[starting_idx + ctr])
			# decoded_numpy_image = utils.decode_compress_ai(compressai_model,compressai_latent_code[starting_idx + ctr])

			pil_img = Image.fromarray(decoded_numpy_image)
			new_im.paste(pil_img, (y_offset, x_offset))
			x_size = pil_img.size[0]
			y_size = pil_img.size[1]
			ctr += 1

			y_offset += y_size
			
		x_offset += x_size
		y_offset = 0
		ctr = 0
	# print(im_b64)
	# print(im_bytes)
	im_file = BytesIO()
	new_im.save(im_file, format="JPEG")

	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)

	res = {"data":im_b64.hex(),"data2":im_bytes.hex()}
	resp = Response(response=json.dumps(res),status=200,mimetype='application/json')
	return resp
	# return send_file(io.BytesIO(im_b64),mimetype='image/jpeg',attachment_filename="cpa_output.jpg")



if __name__ == "__main__":
  app.run(debug=False,port=8000)
