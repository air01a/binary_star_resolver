import numpy as np

def image_format_to_wx(im):
    return np.stack([(255*(im.copy().astype(np.float32) - im.min())/(im.max() - im.min())).astype(np.uint8)]*3, axis=-1)