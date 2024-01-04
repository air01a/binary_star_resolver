import wx
from .plot_utils import PlotUtils
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import cv2

class ImagesPanel(wx.ScrolledWindow):

    def __init__(self,parent, style):
        super(ImagesPanel, self).__init__(parent, style=style)
        self.callback=None
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
       
        self.SetSizer(self.image_sizer)
        
        self.SetScrollbars(20, 20, 50, 50)
        self.images = []


    def show_images(self, images):
        self.images=images
        self.image_sizer.Clear(True)
        for index,im in enumerate(images):
            bitmap_control=PlotUtils.image_to_wx_on_click(self,im,index,self.callback,(100,100))
            self.image_sizer.Add(bitmap_control, 0, wx.ALL | wx.EXPAND, 5)
        self.FitInside()
        self.Refresh()
        self.Update()
        print("show images end")

    def on_image_click(self, event, id):
        print("id :"+str(id))

    def set_callback(self,callback):
        self.callback = callback



class SplitterImages(wx.SplitterWindow):

    def __init__(self,parent):
        super(SplitterImages, self).__init__(parent)
        self.panel_images_list = ImagesPanel(self, style=wx.SUNKEN_BORDER)
        self.panel_images_zoom = wx.Panel(self, style=wx.SUNKEN_BORDER)

        self.panel_images_list.set_callback(self.show_zoom_images)
        self.SplitHorizontally(self.panel_images_list, self.panel_images_zoom)
        self.Layout()
        
    def show_zoom_images(self, event,image_index):
        bitmap = PlotUtils.image_to_wx(self.panel_images_list.images[image_index],(200,200))
        wx.StaticBitmap(self.panel_images_zoom, -1, bitmap)