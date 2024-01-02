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
        self.panel2 = wx.ScrolledWindow(self.splitter2, style=wx.SUNKEN_BORDER)
        self.panel2.SetScrollbars(20, 20, 50, 50)
        self.graph_sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=10)# Sizer to organize graph
        self.panel2.SetSizer(self.graph_sizer)


        # Panel with sliders
        self.panel3 = wx.Panel(self.splitter_sliders, style=wx.SUNKEN_BORDER)
        self.add_sliders_to_panel(self.panel3)

        self.panel4 = wx.Panel(self.splitter_sliders, style=wx.SUNKEN_BORDER)
        self.result_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel4.SetSizer(self.result_sizer)

        # Panel for error messages
        self.panel_error = wx.Panel(self.splitter_error, style=wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Créer une barre de progression
        self.progress_bar = wx.Gauge(self.panel_error, range=100, style=wx.GA_HORIZONTAL)
        self.progress_bar.Hide()
        sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 10)
        self.no_error()

        self.splitter_images.SplitHorizontally(self.scrolled_panel1, self.zoom_image)
        self.splitter1.SplitVertically(self.splitter_images, self.splitter_error)
        self.splitter2.SplitVertically(self.panel2, self.splitter_sliders)
        self.splitter_error.SplitHorizontally(self.splitter2, self.panel_error)
        self.splitter_sliders.SplitHorizontally(self.panel3, self.panel4)
        self.splitter2.SetSashGravity(0.8)
        self.splitter1.SetSashPosition(200) 


        self.splitter_sliders.SetSashPosition(200) 
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
        self.panel_error.SetBackgroundColour("green")

    def on_resize(self, event):
        # Ajuster la position du séparateur pour fixer la taille du panneau inférieur
        self.splitter_error.SetSashPosition(self.GetSize().GetHeight() - 70)

        left_panel_width = self.splitter1.GetSashPosition()
        self.splitter_images.SetSashPosition(self.GetSize().GetHeight() - 250)
        #self.canvas.SetSize(self.panel4.GetSize())
        event.Skip() 

    def event_rooting(self, event_type, event_data):
        match event_type:
            case 1:
                wx.CallAfter(self.add_matplotlib_graphs,event_data)
                
            case 2:
                self.images = event_data
                self.reset_image_sizer()
                self.reset_result_sizer()
                for index,im in enumerate(self.images[:100]):
                    wx.CallAfter(self.add_numpy_grayscale_image_to_scrolled_panel,self.scrolled_panel1,im,index)
                    self.scrolled_panel1.FitInside()
                self.close_loading_dialog()

            case 3:
                self.clear_graphs()
                self.reset_result_sizer()

            case 4:
                wx.CallAfter(self.add_matplotlib_peak,event_data)

            case 2001:
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

    def reset_result_sizer(self):
        self.reset_sizer(self.result_sizer)
        self.result_sizer.Clear()
        self.panel4.Layout()
        self.Layout()

    def on_image_click(self, event, image_index):
        im_norm = cv2.resize(image_format_to_wx(self.images[image_index]),(200,200))
        height, width = im_norm.shape[:2]
        bitmap = wx.Bitmap.FromBuffer(width, height, im_norm)
        wx.StaticBitmap(self.zoom_image, -1, bitmap)


    def clear_graphs(self):
        # Méthode pour effacer les graphiques existants
        for child in self.graph_sizer.GetChildren():
            widget = child.GetWindow()
            if widget: 
                widget.Destroy()
        self.graph_sizer.Clear()
        self.panel2.Refresh()
        self.panel2.Update()


    def generate_matplotlib(self, graph, size=None):
        fig, ax = plt.subplots()
        if size!=None:
            dpi = 100

            # Convertir la taille en pixels en pouces
            inches_width = size[0] / dpi
            inches_height = size[1] / dpi
            fig.set_dpi(dpi)
            fig.set_figheight(inches_height)
            fig.set_figwidth(inches_width)
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

    def add_matplotlib_graphs(self, graph):
        (fig,ax) = self.generate_matplotlib(graph)
        canvas = FigureCanvas(self.panel2, -1, fig)
        self.graph_sizer.Add(canvas, 1, wx.EXPAND)

        self.graph_sizer.Layout()
        self.panel2.FitInside()
        plt.close()

    def add_matplotlib_peak(self, graph):
        self.peak_graph = plt.Figure()
        self.canvas = FigureCanvas(self.panel4, -1, self.peak_graph)
        (graph, peak1, peak2, lm, lr)=graph
        (self.fig_peak,ax) = self.generate_matplotlib(graph,(self.panel4.GetSize()[0],self.panel4.GetSize()[0]))
        self.canvas = FigureCanvas(self.panel4, -1, self.fig_peak)
        self.result_sizer.Add(self.canvas)
        if graph.lines!=None:
            x1 = graph.lines[0]
            x2 = graph.lines[1]
            dist = (abs(x1)+abs(x2))/2 * 0.099
            text = wx.StaticText( self.panel4, label="Rho " + str(dist))
            self.result_sizer.Add(text)
            text2 = wx.StaticText( self.panel4, label="Peak1 " + str(abs(x1)))
            text3 = wx.StaticText( self.panel4, label="Peak1 " + str(abs(x2)))
            self.result_sizer.Add(text2)
            self.result_sizer.Add(text3)
        self.result_sizer.Layout()
        self.panel4.FitInside()
        plt.close()


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
        self.sliders = [slider1, slider2, slider3]
        slider_sizer.Add(self.label_min, 0, wx.ALL | wx.LEFT, 5)
        slider_sizer.Add(slider1, 1, wx.EXPAND | wx.ALL, 1)
        slider_sizer.Add(self.label_max, 0, wx.ALL | wx.LEFT, 5)
        slider_sizer.Add(slider2, 1, wx.EXPAND | wx.ALL, 1)
        slider_sizer.Add(self.label_radius, 0, wx.ALL | wx.LEFT, 5)

        slider_sizer.Add(slider3, 1, wx.EXPAND | wx.ALL, 1)

        panel.SetSizer(slider_sizer)
        slider_sizer.Layout()

    def on_slider_change(self, event):
        min = self.sliders[0].GetValue()
        max = self.sliders[1].GetValue()
        radius = self.sliders[2].GetValue()
        self.broadcaster_out.put(Message_Queue(1002,{"min":min, "max":max,"radius":radius}))
        event.Skip()  