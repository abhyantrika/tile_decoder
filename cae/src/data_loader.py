from pathlib import Path
from typing import Tuple

import numpy as np
import torch as T
from PIL import Image
from torch.utils.data import Dataset


import os

import cv2 as cv
import numpy as np
from torch.utils.data import Dataset

from PIL import Image
from torchvision import transforms
import image_slicer
import patchify
import torch

class ImageFolder720p(Dataset):
    """
    Image shape is (720, 1280, 3) --> (768, 1280, 3) --> 6x10 128x128 patches
    """

    def __init__(self, root: str):
        self.files = sorted(Path(root).iterdir())

    def __getitem__(self, index: int) -> Tuple[T.Tensor, np.ndarray, str]:
        path = str(self.files[index % len(self.files)])
        img = np.array(Image.open(path))

        pad = ((24, 24), (0, 0), (0, 0))

        # img = np.pad(img, pad, 'constant', constant_values=0) / 255
        img = np.pad(img, pad, mode="edge") / 255.0

        img = np.transpose(img, (2, 0, 1))
        img = T.from_numpy(img).float()

        patches = np.reshape(img, (3, 6, 128, 10, 128))
        patches = np.transpose(patches, (0, 1, 3, 2, 4))

        return img, patches, path

    def __len__(self):
        return len(self.files)


class custom_single(Dataset):
    def __init__(self,patch_size=128):
        self.file = 'rome.jpg' #-> from (4098,4177) ->  w 4096 x h 4224: (32x33). 128x128 patches.
        
        self.patch_size = patch_size

        pil_img = Image.open(self.file)
        pil_img = pil_img.resize((4096,4177))

        img = np.array(pil_img)

        pad = ((24, 23), (0, 0), (0, 0))

        img = np.pad(img,pad,mode='edge') / 255.0

        self.img = T.from_numpy(img).float()

        # patches = np.reshape(img, (3, 32, 128, 33, 128))
        # self.patches = np.transpose(patches, (0, 1, 3, 2, 4))

        self.patches = patchify.patchify(img,(self.patch_size,self.patch_size,3),step=self.patch_size)
        print('patch shape: ',self.patches.shape)

        self.patches = np.squeeze(self.patches)

        tile_row,tile_col,tile_w,tile_h,ch = self.patches.shape

        self.patches = self.patches.reshape(tile_row*tile_col,tile_w,tile_h,ch)
        self.patches = torch.tensor(self.patches)
        self.patches = self.patches.permute(0,3,1,2)

        # #self.img = Image.open(self.file).convert('RGB')
        # self.image_list = image_slicer.slice(self.file,15,save=False)

        # self.transform = transforms.Compose([
        #     #transforms.RandomHorizontalFlip(),
        #     transforms.ToTensor()])

        #self.x = self.transform(s)

    def __getitem__(self, i):

        return self.patches[i],self.file
        #return self.img,self.patches,self.file

    def __len__(self):
        return len(self.patches)

