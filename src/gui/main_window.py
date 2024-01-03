import wx
import threading
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from structure.message_queue import Message_Queue
from .image_format import image_format_to_wx
import cv2
from .loader import LoadingDialog
from .menubar import MenuBar
from .results_panel import ResultsPanel
from .notebook import NoteBookResults
import utils.constant as CONSTANT

class MainFrame(wx.Frame):
    def __init__(self,broadcaster_in, broadcaster_out):
        super().__init__(None, title="Despeckle", size=(800, 600))

        self.Bind(wx.EVT_CLOSE, self.on_close)


        self.images_ptr = []
        self.menubar = MenuBar(self, self.event_rooting)
        self.loading_dialog = None 
        self.broadcaster_in = broadcaster_in
        self.broadcaster_out = broadcaster_out
        self.thread = threading.Thread(target=self.listener)


        # Screen splitting
        self.splitter1 = wx.SplitterWindow(self)
        self.splitter_images = wx.SplitterWindow(self.splitter1)
        self.splitter_error = wx.SplitterWindow(self.splitter1)
        self.splitter2 = wx.SplitterWindow(self.splitter_error)
        self.splitter_sliders = wx.SplitterWindow(self.splitter2)


        # Panel with images from sensor
        self.scrolled_panel1 = wx.ScrolledWindow(self.splitter_images, style=wx.SUNKEN_BORDER)
        self.scrolled_panel1.SetScrollbars(20, 20, 50, 50)
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_panel1.SetSizer(self.image_sizer)
        self.scrolled_panel1.Layout()
        
        # Panel with zoom images
        self.zoom_image = wx.Panel(self.splitter_images, style=wx.SUNKEN_BORDER)

        # Panel with graphs
        self.panel_graph = NoteBookResults(parent=self.splitter2, style=wx.SUNKEN_BORDER)

        # Panel with sliders
        self.panel3 = wx.Panel(self.splitter_sliders, style=wx.SUNKEN_BORDER)
        self.add_sliders_to_panel(self.panel3)

        self.resultsPanel = ResultsPanel(self.splitter_sliders, style=wx.SUNKEN_BORDER)


        # Panel for error messages
        self.panel_error = wx.Panel(self.splitter_error, style=wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Créer une barre de progression
        #self.progress_bar = wx.Gauge(self.panel_error, range=100, style=wx.GA_HORIZONTAL)
        #self.progress_bar.Hide()
        #sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 10)
        self.error = wx.StaticText(self.panel_error, label="Max Value :")
        sizer.Add( self.error)
        self.no_error()

        self.splitter_images.SplitHorizontally(self.scrolled_panel1, self.zoom_image)
        self.splitter1.SplitVertically(self.splitter_images, self.splitter_error)
        self.splitter2.SplitVertically(self.panel_graph, self.splitter_sliders)
        self.splitter_error.SplitHorizontally(self.splitter2, self.panel_error)
        self.splitter_sliders.SplitHorizontally(self.panel3, self.resultsPanel)
        self.splitter2.SetSashGravity(0.8)
        self.splitter1.SetSashPosition(200) 


        self.splitter_sliders.SetSashPosition(220) 
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.thread.start()
        self.Maximize()
        self.Show()
        self.open_loader()

    def on_close(self,event):
        self.broadcaster_out.put(Message_Queue(0,None))
        self.broadcaster_in.put(Message_Queue(0,None))
        self.Destroy()
        wx.Exit()

    def open_loader(self, event=None):
        if not self.loading_dialog:
            self.loading_dialog = LoadingDialog(self, "Chargement...")

    
    def close_loading_dialog(self):
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None

    def no_error(self):
        self.error.SetLabel("No error")
        self.panel_error.SetBackgroundColour("green")
        self.panel_error.Refresh()
        self.panel_error.Update()

    def show_error(self,error):
        self.panel_error.SetBackgroundColour("red")
        self.error.SetLabel(error)
        self.panel_error.Refresh()
        self.panel_error.Update()


    def on_resize(self, event):
        # Ajuster la position du séparateur pour fixer la taille du panneau inférieur
        self.splitter_error.SetSashPosition(self.GetSize().GetHeight() - 100)

        left_panel_width = self.splitter1.GetSashPosition()
        self.splitter_images.SetSashPosition(self.GetSize().GetHeight() - 250)
        print("on resize end")

    def event_rooting(self, event_type, event_data):
        print("Main window event rooting : "+str(event_type))

        match event_type:
            case CONSTANT.EVENT_ADD_FREQUENCY_GRAPH:
                wx.CallAfter(self.panel_graph.frequency.add_graph,event_data)
            case CONSTANT.EVENT_ADD_VISIBLE_GRAPH:
                wx.CallAfter(self.panel_graph.visible.add_graph,event_data)
            case CONSTANT.EVENT_ADD_SPECKLE_IMAGE:
                self.no_error()
                self.images = event_data
                self.reset_image_sizer()
                for index,im in enumerate(self.images[:100]):
                    wx.CallAfter(self.add_numpy_grayscale_image_to_scrolled_panel,self.scrolled_panel1,im,index)
                    self.scrolled_panel1.FitInside()
                self.close_loading_dialog()

            case CONSTANT.EVENT_CLEAR_FREQUENCY_GRAPH:
                self.panel_graph.frequency.clear()
            case CONSTANT.EVENT_CLEAR_VISIBLE_GRAPH:
                self.panel_graph.visible.clear()
            case CONSTANT.EVENT_UPDATE_RESULT_GRAPH:
                wx.CallAfter(self.resultsPanel.update_graph,event_data)

            case CONSTANT.EVENT_UPDATE_RESULT_VISIBLE:
                wx.CallAfter(self.resultsPanel.update_results_visible,event_data)

            case CONSTANT.EVENT_UPDATE_RESULT_CORRELATION:
                wx.CallAfter(self.resultsPanel.update_results_frequency,event_data)
            case CONSTANT.EVENT_NO_ERROR:
                self.no_error()

            case CONSTANT.EVENT_ERROR:
                self.show_error(event_data)

            case CONSTANT.EVENT_CLEAR_FREQUENCY:
                self.panel_graph.frequency.clear(event_data)
            
            case CONSTANT.EVENT_NEW_SPECKLES_IMAGE:
                self.broadcaster_out.put(Message_Queue(1001,event_data))
                self.open_loader()


    def listener(self):
        while True:
            message = self.broadcaster_in.get()
            if message.get_type() == 0:
                break
            self.event_rooting(message.get_type(), message.get_data())
            self.broadcaster_in.task_done()
        

    def start_listener(self):
        thread = threading.Thread(target=self.listener)
        thread.daemon = True
        thread.start()



    def add_numpy_grayscale_image_to_scrolled_panel(self, panel, im, image_index):
        im_norm = image_format_to_wx(im)
        height, width = im_norm.shape[:2]
        bitmap = wx.Bitmap.FromBuffer(width, height, im_norm)
        bitmap_control = wx.StaticBitmap(panel, wx.ID_ANY, bitmap)
        bitmap_control.Bind(wx.EVT_LEFT_DOWN, lambda event, idx=image_index: self.on_image_click(event, idx))
        self.image_sizer.Add(bitmap_control, 0, wx.ALL | wx.EXPAND, 5)
        self.images_ptr.append(bitmap_control)
        self.image_sizer.Layout()


    def reset_sizer(self, sizer):
        for child in self.image_sizer.GetChildren():
            widget = child.GetWindow()
            self.image_sizer.Remove(0)
            if widget:
                widget.Destroy()
            del child


    def reset_image_sizer(self):


        self.reset_sizer(self.image_sizer)
        self.image_sizer.Clear()
        
        self.scrolled_panel1.Layout()
        self.Layout()



    def on_image_click(self, event, image_index):
        im_norm = cv2.resize(image_format_to_wx(self.images[image_index]),(200,200))
        height, width = im_norm.shape[:2]
        bitmap = wx.Bitmap.FromBuffer(width, height, im_norm)
        wx.StaticBitmap(self.zoom_image, -1, bitmap)


    def add_sliders_to_panel(self, panel):
        slider_sizer = wx.BoxSizer(wx.VERTICAL)


        self.label_min = wx.StaticText(panel, label="Min Value :")
        
        slider1 = wx.Slider(panel, value=4000, minValue=2000, maxValue=10000, style=wx.SL_HORIZONTAL)
        slider1.Bind(wx.EVT_LEFT_UP, self.on_slider_change)

        self.label_max = wx.StaticText(panel, label="Max Value :")
        
        slider2 = wx.Slider(panel, value=40000, minValue=1000, maxValue=65000, style=wx.SL_HORIZONTAL)
        slider2.Bind(wx.EVT_LEFT_UP, self.on_slider_change)

        self.label_radius = wx.StaticText(panel, label="Radius :")
        slider3 = wx.Slider(panel, value=1, minValue=1, maxValue=10, style=wx.SL_HORIZONTAL)
        slider3.Bind(wx.EVT_LEFT_UP, self.on_slider_change)

        self.label_images_number = wx.StaticText(panel, label="Number of images :")
        slider4 = wx.Slider(panel, value=10, minValue=10, maxValue=100, style=wx.SL_HORIZONTAL)
        slider4.Bind(wx.EVT_LEFT_UP, self.on_slider_change_images_number)

        self.sliders = [slider1, slider2, slider3, slider4]
        slider_sizer.Add(self.label_min, 0, wx.ALL | wx.LEFT, 5)
        slider_sizer.Add(slider1, 0, wx.EXPAND | wx.ALL, 1)
        slider_sizer.Add(self.label_max, 0, wx.ALL | wx.LEFT, 5)
        slider_sizer.Add(slider2, 0, wx.EXPAND | wx.ALL, 1)
        slider_sizer.Add(self.label_radius, 0, wx.ALL | wx.LEFT, 5)
        slider_sizer.Add(slider3, 0, wx.EXPAND | wx.ALL, 1)
        slider_sizer.Add(self.label_images_number, 0, wx.ALL | wx.LEFT, 5)
        slider_sizer.Add(slider4, 0, wx.EXPAND | wx.ALL, 1)

        panel.SetSizer(slider_sizer)
        slider_sizer.Layout()

    def on_slider_change(self, event):
        print(event)
        min = self.sliders[0].GetValue()
        max = self.sliders[1].GetValue()
        radius = self.sliders[2].GetValue()
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_NEW_PARAMS,{"min":min, "max":max,"radius":radius}))
        event.Skip() 


    def on_slider_change_images_number(self, event):
        print(event)
        images_number = self.sliders[3].GetValue()
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_NEW_NUMBER,{"number":images_number}))
        event.Skip()   

