import argparse
from PIL import Image
import numpy as np
from skimage.metrics import *

parser = argparse.ArgumentParser(description="Add more options if necessary")
parser.add_argument('--img_1',default='resources/resized_img.png',help='chosor first image')
parser.add_argument('--img_2',default=None,help='chosor second image')
args = parser.parse_args()

img_1 = np.array(Image.open(args.img_1))/255.0
img_2 = np.array(Image.open(args.img_2))/255.0


print(' PSNR: ',peak_signal_noise_ratio(img_1,img_2))
print('SSIM: ',structural_similarity(img_1,img_2,multichannel=True))
print('MSE: ',mean_squared_error(img_1,img_2))


