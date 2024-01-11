from image_utils.image_utils import sum_aligned_images,isolate_peaks, find_brightest_pixel,angle_with_y_axis
from image_utils.processing import AstroImageProcessing
import numpy as np
from cv2 import circle

class VisibleAnalyzer:

    def __init__(self):
        self.number_of_images = 10
        self.min_value = 4000
        self.max_value = 40000
        self.mean_f = 7
        self.radius=2


    def stack_best(self, images):
        n = int(self.number_of_images/100 * len(images))
        self.stacked_image = (sum_aligned_images(images[0:n]))
        self.speckle_image = AstroImageProcessing.normalize(AstroImageProcessing.apply_mean_mask_subtraction(self.stacked_image,self.mean_f))*65535

        self.speckle_image[self.speckle_image<0]=0
        self.speckle_image=(np.clip(self.speckle_image, self.min_value,self.max_value) - self.min_value)/(self.max_value-self.min_value)
        speckle_image = self.speckle_image.copy()

        (x,y)=find_brightest_pixel(speckle_image)
        speckle_image[y,x]=0
        speckle_image[y,x]=speckle_image.max()

        return self.stacked_image, speckle_image


    def get_peaks(self):
        #im = np.clip(self.speckle_image.copy(),self.min_value, self.speckle_image.max())
        x,y,x2,y2 = isolate_peaks(self.speckle_image.copy(), radius = self.radius)
        angle = angle_with_y_axis(x, y, x2, y2)

        return x,y, x2, y2, angle

    def draw_peaks(self, image, x, y, x2, y2):
        im = image.copy()
        circle(im,(x2,y2),2,im.max()*1.1,-1)
        circle(im,(x,y),2,im.max()*1.1,-1)
        return im
    
