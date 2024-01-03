from image_utils.image_utils import sum_aligned_images,isolate_peaks, find_brightest_pixel
from image_utils.processing import AstroImageProcessing
import numpy as np
from cv2 import circle

class VisibleAnalyzer:

    def __init__(self):
        self.number_of_images = 10

    
    def stack_best(self, images):
        n = int(self.number_of_images/100 * len(images))
        self.stacked_image = (sum_aligned_images(images[0:n]))
        self.speckle_image = AstroImageProcessing.apply_mean_mask_subtraction(self.stacked_image,7)

        self.speckle_image[self.speckle_image<0]=0
        speckle_image = self.speckle_image.copy()

        (x,y)=find_brightest_pixel(speckle_image)
        speckle_image[y,x]=0
        speckle_image[y,x]=speckle_image.max()

        return self.stacked_image, speckle_image


    def get_peaks(self):
        im = np.clip(self.speckle_image.copy(),self.speckle_image.mean()*5/2, self.speckle_image.max())
        x,y,x2,y2 = isolate_peaks(im)
        return x,y, x2, y2

    def draw_peaks(self, image, x, y, x2, y2):
        im = image.copy()
        circle(im,(x2,y2),2,im.max()*1.1,-1)
        circle(im,(x,y),2,im.max()*1.1,-1)
        return im
    
