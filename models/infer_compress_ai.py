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

forward("./rome.png")
