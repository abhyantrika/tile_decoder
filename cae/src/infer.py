import os
import yaml
import argparse
from pathlib import Path

import numpy as np
import torch as T
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from data_loader import ImageFolder720p,custom_single
from utils import save_imgs

from bagoftools.namespace import Namespace
from bagoftools.logger import Logger

from models.cae_32x32x32_zero_pad_bin import CAE
import torch
import cv2
import patchify

def to_numpy(img):
    """
        Takes in tensor in 1,C,H,W format and returns H,W,C format in numpy
    """

    img = torch.squeeze(img)
    img = img.cpu().detach().numpy()
    img = np.transpose(img,(1,2,0))

    return img

def save_tensor(tensor,filename='temp.png'):
    """
        Tensor is in C,H,W. Convert to H,W,C numpy and save.
    """
    tensor = torch.squeeze(tensor)
    img = to_numpy(tensor)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite(filename,img*255.0)


path = '../experiments/training/checkpoint/model_50.pth'
exp_dir = 'output/'

os.makedirs(exp_dir,exist_ok=True)
dataset = custom_single()
dataloader = DataLoader(
    dataset=dataset,
    batch_size=16,
    shuffle=False,
    num_workers=4,
)


model = CAE()
model.eval()

state_dict = torch.load(path)
model.load_state_dict(state_dict)
model = model.cuda()

# for batch_idx, data in enumerate(dataloader, start=1):
#     patches, _ = data
#     patches = patches.float().cuda()
#     break 

# out = T.zeros(33, 32, 3, 128, 128)
# all_patches = dataset.patches

# all_patches = all_patches.reshape(33,32,3,128,128)
# for i in range(33):
#     for j in range(32):
#         x = all_patches[i,j,...].unsqueeze(0).cuda().float()
#         out[i, j] = model(x.float()).cpu().data



# out = out.permute(0,1,3,4,2)
# out = torch.unsqueeze(out,2)
# out = patchify.unpatchify(out.numpy(),(4224,4096,3))

output = []
encoded = []
all_patches = dataset.patches
for i in range(len(all_patches)):
	x = all_patches[i].unsqueeze(0).cuda().float()
	with torch.no_grad():
		out = model(x)
	output.append(out.cpu())
	encoded.append(model.encoded)


output = torch.stack(output)
output = output.permute(0,1,3,4,2)
output = output.reshape(33,32,1,128,128,3)
out = patchify.unpatchify(output.numpy(),(4224,4096,3))
cv2.imwrite('out.png',out*255)

encoded = torch.stack(encoded).squeeze()
encoded = encoded.bool().cpu().numpy()
np.save('encoded',encoded)

#out = out.reshape(33*32,3,128,128)
#out = np.transpose(out, (0, 3, 1, 4, 2))
#out = np.reshape(out, (4096, 4224, 3))
#out = np.transpose(out, (2, 0, 1))

# y = T.cat((img[0], out), dim=2).unsqueeze(0)
# save_imgs(
#     imgs=y,
#     to_size=(3, 4096, 2 * 4224),
#     name=exp_dir / f"out/{epoch_idx}_{batch_idx}.png",
# )

# save_imgs(
#     imgs=out.unsqueeze(0),
#     to_size=(3, 4096,4224),
#     name=exp_dir + f"/out.png",
# )
