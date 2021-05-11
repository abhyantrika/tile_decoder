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
from models import cae_32
from compressai.zoo import bmshj2018_hyperprior


def load_cae_model(config):
	device = 'cuda' if torch.cuda.is_available() else 'cpu'
	#if config['model'] =='cae':
	model = cae_32.CAE()
	state_dict = torch.load('resources/'+config['trained_path'],map_location=device)
	model.load_state_dict(state_dict)
	model = model.to(device)
	model = model.eval()
	print('loaded cae model')
	return model

def load_compress_ai_model(config):
	device = 'cuda' if torch.cuda.is_available() else 'cpu'
	net = bmshj2018_hyperprior(quality=2, pretrained=True).eval().to(device)
	print('loaded compressai model')
	return net


def get_patches(config):
	pil_img = Image.open('static/images/'+config['input_img'])
	pil_img = pil_img.resize(config['img_size'])
	img = np.array(pil_img)
	pad = ((24, 23), (0, 0), (0, 0)) #Calculated for this image.
	img = np.pad(img,pad,mode='edge') / 255.0
	patches = patchify.patchify(img,config['tile_size'],step=int(config['step_size']))

	#We reuse these shapes:
	with open('resources/patch_info.pkl','wb') as fout:
		pickle.dump(patches.shape,fout)
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

def decode_cae(model,latent):
	with torch.no_grad():
		output = model.decode(latent)
	output_tile = to_numpy(output)
	output_tile = output_tile * 255
	output_tile = output_tile.astype(np.uint8)
	return output_tile


def get_encoders_cae(model,config):
	device = 'cuda' if torch.cuda.is_available() else 'cpu'
	patches = get_patches(config)
	size = patches.shape
	patches = to_torch(patches)
	encoded = []
	for i in range(len(patches)):
		x = patches[i].unsqueeze(0).to(device).float()
		with torch.no_grad():
			out = model(x)
		encoded.append(model.encoded.byte())

	encoded = torch.stack(encoded)
	total,a,b,c,d =  encoded.shape #a,b,c,d are latent dimensions
	row,col = size[:2]
	encoded = encoded.view(row,col,a,b,c,d)
	
	print("Encoders generated for cae")

	return encoded

def decode_all_cae(encoders,model,config):
	device = 'cuda' if torch.cuda.is_available() else 'cpu'	
	enc_shape = encoders.shape

	decoded = []
	for i in range(enc_shape[0]):
		for j in range(enc_shape[1]):
			with torch.no_grad():
				out = model.decode(encoders[i][j])
			decoded.append(out)

	decoded = torch.stack(decoded)
	dec_shape = decoded.shape 
	decoded = decoded.view(enc_shape[0],enc_shape[1],dec_shape[1],dec_shape[2],dec_shape[3],dec_shape[4])
	decoded = decoded.permute(0,1,2,4,5,3).cpu().detach().numpy()

	out_img = patchify.unpatchify(decoded,(config['img_size'][1],config['img_size'][0],3)) #opposite notation. H,W
	out_img = out_img*255
	out_img = out_img.astype(np.uint8)

	pil_img = Image.fromarray(out_img)
	pil_img.save('resources/out_decoded.jpg')


def get_encoders_compress_ai(model,config):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    patches = get_patches(config)
    size = patches.shape
    patches = to_torch(patches)
    encoded = []
    for i in range(len(patches)):
        x = patches[i].unsqueeze(0).to(device).float()
        with torch.no_grad():
            out = model.compress(x)
        encoded.append(out)    
    print("Encoders generated: compressai")

    return encoded

def decode_compress_ai(model,latent):
	with torch.no_grad():
		output = model.decompress(latent['strings'],latent['shape'])
		output = output['x_hat']
	output_tile = to_numpy(output)
	output_tile = output_tile * 255
	output_tile = output_tile.astype(np.uint8)
	return output_tile



def decode_all_compress_ai(encoders,model,config):
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 

    decoded = []
    for i in range(config['patch_tile_size'][0]*config['patch_tile_size'][1]):
            with torch.no_grad():
                out = model.decompress(encoders[i]["strings"], encoders[i]["shape"])
            decoded.append(out['x_hat'])

    decoded = torch.stack(decoded)
    dec_shape = decoded.shape 
    decoded = decoded.view(config['patch_tile_size'][0],config['patch_tile_size'][1],dec_shape[1],dec_shape[2],dec_shape[3],dec_shape[4])
    decoded = decoded.permute(0,1,2,4,5,3).cpu().detach().numpy()

    out_img = patchify.unpatchify(decoded,(config['img_size'][1],config['img_size'][0],3)) #opposite notation. H,W
    out_img = out_img*255
    out_img = out_img.astype(np.uint8)

    pil_img = Image.fromarray(out_img)
    pil_img.save('resources/out_decoded.jpg')


if __name__ =='__main__':
	with open('config.yaml') as fout:
	  config = yaml.load(fout,Loader=yaml.FullLoader) 

	model = load_cae_model(config)
	encoders = get_encoders(model,config)

	tile_x,tile_y = (0,0)
	decoded_numpy_image = decode_cae(model,encoders[tile_x][tile_y])
	
	#print(decoded_numpy_image)
	
	#base64 encoding.
	pil_img = Image.fromarray(decoded_numpy_image)

	im_file = BytesIO()
	pil_img.save(im_file, format="JPEG")
	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)

