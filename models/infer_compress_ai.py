import math
import io
import torch
from torchvision import transforms
import numpy as np

from PIL import Image

import matplotlib.pyplot as plt
from pytorch_msssim import ms_ssim

from compressai.zoo import bmshj2018_hyperprior

from ipywidgets import interact, widgets
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)

net = bmshj2018_hyperprior(quality=2, pretrained=True).eval().to(device)
print(f'Parameters: {sum(p.numel() for p in net.parameters())}')

img = Image.open('./rome.png').convert('RGB')
generate_reconstructed_image(img)

#%matplotlib inline


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
