import math
import io
import torch
from torchvision import transforms
import torch.nn.functional as F
import numpy as np

from PIL import Image

import matplotlib.pyplot as plt
from pytorch_msssim import ms_ssim

from compressai.zoo import bmshj2018_hyperprior

from ipywidgets import interact, widgets
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)

#%matplotlib inline

def pad(x, p=2 ** 6):
    h, w = x.size(2), x.size(3)
    H = (h + p - 1) // p * p
    W = (w + p - 1) // p * p
    padding_left = (W - w) // 2
    padding_right = W - w - padding_left
    padding_top = (H - h) // 2
    padding_bottom = H - h - padding_top
    return F.pad(
        x,
        (padding_left, padding_right, padding_top, padding_bottom),
        mode="constant",
        value=0,
    )

def crop(x, h,w):
    H, W = x.size(2), x.size(3)
    #h, w = size
    padding_left = (W - w) // 2
    padding_right = W - w - padding_left
    padding_top = (H - h) // 2
    padding_bottom = H - h - padding_top
    return F.pad(
        x,
        (-padding_left, -padding_right, -padding_top, -padding_bottom),
        mode="constant",
        value=0,
    )

def torch2img(x: torch.Tensor) -> Image.Image:
    return transforms.ToPILImage()(x.clamp_(0, 1).squeeze())


def _encode(img, net):
    x = transforms.ToTensor()(img).unsqueeze(0).to(device)
    
    h, w = x.size(2), x.size(3)
    p = 64  # maximum 6 strides of 2
    x = pad(x, p)
    
    with torch.no_grad():
        out = net.compress(x)
    
    #keys are strings and shape

    return out

def _decode(out_tensor, original_img, net):
    o_img = transforms.ToTensor()(original_img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        out = net.decompress(out_tensor["strings"], out_tensor["shape"])
    
    h, w = o_img.size(2), o_img.size(3)
    x_hat = crop(out["x_hat"], h,w)
    img = torch2img(x_hat)
    
    img.save("Decoded_image.png")  
    return x_hat 

def forward(img_path):
    net = bmshj2018_hyperprior(quality=2, pretrained=True).eval().to(device)
    print(f'Parameters: {sum(p.numel() for p in net.parameters())}')

    img = Image.open(img_path).convert('RGB')

    encoded = _encode(img, net) # return torch tensor
    decoded = _decode(encoded, img, net) # return torch tensor


def generate_reconstructed_image(img):
    x = transforms.ToTensor()(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        out_net = net.forward(x)
    print(out_net['x_hat'].shape)
    out_net['x_hat'].clamp_(0, 1)
    #print(out_net.keys())

    rec_net = transforms.ToPILImage()(out_net['x_hat'].squeeze().to(device))

    diff = torch.mean((out_net['x_hat'] - x).abs(), axis=1).squeeze().cpu()
    print(diff)

    loss=torch.nn.MSELoss()
    v = loss(x,out_net['x_hat'])
    print("MSELoss:" + str(v))
    
    fix, axes = plt.subplots(1, 3, figsize=(16, 12))
    for ax in axes:
        ax.axis('off')
        
    axes[0].imshow(img)
    axes[0].title.set_text('Original')

    axes[1].imshow(rec_net)
    axes[1].title.set_text('Reconstructed')

    axes[2].imshow(diff, cmap='viridis')
    axes[2].title.set_text('Difference')

    plt.savefig("reconstructed_image.png")
    plt.show()
    
    return rec_net

def get_patches(config):
    pil_img = Image.open('../resources/resized_img.png')
    pil_img = pil_img.resize(config['img_size'])
    img = np.array(pil_img)
    pad = ((24, 23), (0, 0), (0, 0)) #Calculated for this image.
    img = np.pad(img,pad,mode='edge') / 255.0
    patches = patchify.patchify(img,config['tile_size'],step=int(config['step_size']))
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


def get_encoders(model,config):
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
    print("Encoders generated.")

    return encoded

def decode_all_comp(encoders,model,config):
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

import yaml
import patchify

with open('../config.yaml') as fout:
  config = yaml.load(fout,Loader=yaml.FullLoader) 

patches = get_patches(config)
patches = to_torch(patches)


#forward("../resources/resized_img.png")
