import matplotlib.pyplot as plt

import wx
import cv2
import numpy as np

class PlotUtils:
    @staticmethod
    def image_format_to_wx(im):
        return np.stack([(255*(im.copy().astype(np.float32) - im.min())/(im.max() - im.min())).astype(np.uint8)]*3, axis=-1)
    
    @staticmethod
    def image_to_wx(im, resize=None):
        im_norm = PlotUtils.image_format_to_wx(im)
        if resize!=None:
            im_norm= cv2.resize(im_norm,resize)
        height, width = im_norm.shape[:2]
        bitmap = wx.Bitmap.FromBuffer(width, height, im_norm)
        return bitmap

    @staticmethod
    def image_to_wx_on_click( parent, im, image_index, callback,resize=None):
        bitmap = PlotUtils.image_to_wx(im,resize)
        bitmap_control = wx.StaticBitmap(parent, wx.ID_ANY, bitmap)

        bitmap_control.Bind(wx.EVT_LEFT_DOWN, lambda event, idx=image_index: callback(event, idx))
        
        return bitmap_control


    @staticmethod
    def set_fig_size(fig,size):
        dpi = 100

        # Convertir la taille en pixels en pouces
        inches_width = size[0] / dpi
        inches_height = size[1] / dpi
        fig.set_dpi(dpi)
        fig.set_figheight(inches_height)
        fig.set_figwidth(inches_width)

    @staticmethod
    def get_figure():
        fig,ax= plt.subplots()
        return fig,ax
    

    @staticmethod
    def generate_matplotlib(figure, graph):
        fig, ax = figure
        
        if graph.type=='image':
            ax.imshow(graph.graph,cmap=graph.cmap)
        elif graph.type=='plot':
            (x,y) = graph.graph
            ax.plot(x,y)
        
        if graph.lines!=None:
            for i in graph.lines:
                ax.axvline(x=i, color='r', linestyle='--')


        ax.set_title(graph.title)
        return fig,ax


    @staticmethod
    def close():
        plt.close()