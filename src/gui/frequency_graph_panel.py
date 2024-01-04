import wx
from .plot_utils import PlotUtils

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class FrequencyGraphsPanel(wx.ScrolledWindow):

    def __init__(self,*args, **kwargs):
        super(FrequencyGraphsPanel, self).__init__(*args, **kwargs)

        self.SetScrollbars(20, 20, 50, 50)
        self.graph = []
        self.graph_sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=10)# Sizer to organize graph

        self.figure_psd = PlotUtils.get_figure()
        self.figure_mean_filter = PlotUtils.get_figure()
        self.figure_ellipse = PlotUtils.get_figure()
        self.figure_minus = PlotUtils.get_figure()

        self.figures = [self.figure_psd, self.figure_mean_filter,self.figure_ellipse,self.figure_minus]

        self.canvas_psd = FigureCanvas(self, -1, self.figure_psd[0])
        self.canvas_mean_filter = FigureCanvas(self, -1, self.figure_mean_filter[0])
        self.canvas_ellipse = FigureCanvas(self, -1, self.figure_ellipse[0])
        self.canvas_minus = FigureCanvas(self, -1, self.figure_minus[0])

        self.canvas = [self.canvas_psd, self.canvas_mean_filter, self.canvas_ellipse, self.canvas_minus]
        self.graph_sizer.Add(self.canvas_psd, 1, wx.EXPAND)
        self.graph_sizer.Add(self.canvas_mean_filter, 1, wx.EXPAND)
        self.graph_sizer.Add(self.canvas_ellipse, 1, wx.EXPAND)
        self.graph_sizer.Add(self.canvas_minus, 1, wx.EXPAND)

        self.SetSizer(self.graph_sizer)


    def clear(self, which=None):
        if which!=None:
            for num in which:
                self.figures[num][1].clear()
                self.canvas[num].draw()
        else:
            for fig in self.figures:
                fig[1].clear()
            for canva in self.canvas:
                canva.draw()
        self.Refresh()
        self.Update()

    
    def add_graph_with_num(self, num, graph):
        self.graph = graph
        self.figures[num][1].clear()
        self.figure = PlotUtils.generate_matplotlib(self.figures[num], graph)
        self.canvas[num].draw()
        self.Refresh()  # Marquer le panel pour le rafraîchissement
        self.Update() 
        
    def add_graph(self, graph):
        if graph.num!=None:
            self.add_graph_with_num(graph.num, graph)
        