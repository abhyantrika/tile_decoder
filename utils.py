import torch 
import numpy as np 
import patchify
from PIL import Image
import yaml 
import pickle
import models
import base64
from io import BytesIO
from PIL import Image


def load_model(config):
	if config['model'] =='cae':
		from models import cae_32
		model = cae_32.CAE()

	state_dict = torch.load('resources/'+config['trained_path'])
	model.load_state_dict(state_dict)
	
	device = 'cuda' if torch.cuda.is_available() else 'cpu'
	model = model.to(device)

	print('loading: ',config['model'])
	model = model.eval()

	return model


def get_patches(config):
	pil_img = Image.open('static/images/'+config['input_img'])
	pil_img = pil_img.resize(config['img_size'])
	img = np.array(pil_img)
	pad = ((24, 23), (0, 0), (0, 0)) #Calculated for this image.
	img = np.pad(img,pad,mode='edge') / 255.0
	patches = patchify.patchify(img,config['tile_size'],step=int(config['step_size']))
	#print('patch shape: ',patches.shape)

	#We reuse these shapes:
	with open('resources/patch_info.pkl','wb') as fout:
		pickle.dump(patches.shape,fout)

	# dummy = np.zeros_like(patches)
	# with open('resources/patch_example.pkl','wb') as fout:
	# 	pickle.dump(dummy,fout)

	return patches

def to_torch(patches):
	patches = np.squeeze(patches)
	patches = torch.tensor(patches)
	w_blocks,h_blocks,tile_w,tile_h,ch = patches.shape
	patches = patches.contiguous().view(-1,w_blocks*h_blocks,tile_w,tile_h,ch).squeeze()
	patches = patches.permute(0,3,1,2).float()
	return patches

def to_numpy(tensor):
	tensor = torch.squeeze(tensor).cpu().detach().permute(1,2,0).numpy()
	return tensor

def decode(model,latent):
	with torch.no_grad():
		output = model.decode(latent)
	output_tile = to_numpy(output)
	output_tile = output_tile * 255
	output_tile = output_tile.astype(np.uint8)
	return output_tile


def get_encoders(model,config):
	device = 'cuda' if torch.cuda.is_available() else 'cpu'
	patches = get_patches(config)
	size = patches.shape
	patches = to_torch(patches)
	encoded = []
	for i in range(len(patches)):
		x = patches[i].unsqueeze(0).cuda().float()
		with torch.no_grad():
			out = model(x)
		encoded.append(model.encoded.byte())

	encoded = torch.stack(encoded)
	total,a,b,c,d =  encoded.shape #a,b,c,d are latent dimensions
	row,col = size[:2]
	encoded = encoded.view(row,col,a,b,c,d)
	
	print("Encoders generated.")

	return encoded

if __name__ =='__main__':
	with open('config.yaml') as fout:
	  config = yaml.load(fout,Loader=yaml.FullLoader) 

	#patches = get_patches(config)
	#patches = to_torch(patches)
	model = load_model(config)
	encoders = get_encoders(model,config)

	tile_x,tile_y = (0,0)
	decoded_numpy_image = decode(model,encoders[tile_x][tile_y])
	
	#print(decoded_numpy_image)
	
	#base64 encoding.
	pil_img = Image.fromarray(decoded_numpy_image)

	im_file = BytesIO()
	pil_img.save(im_file, format="JPEG")
	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)

