import wx
from .plot_utils import PlotUtils

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class GraphsPanel(wx.ScrolledWindow):

    def __init__(self,*args, **kwargs):
        super(GraphsPanel, self).__init__(*args, **kwargs)

        self.SetScrollbars(20, 20, 50, 50)
        self.graph = []
        self.graph_sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=10)# Sizer to organize graph
        self.SetSizer(self.graph_sizer)


    def clear(self):
        for child in self.graph_sizer.GetChildren():
            widget = child.GetWindow()
            if widget: 
                widget.Destroy()
        self.graph_sizer.Clear()
        self.Refresh()
        self.Update()

    
    def add_graph(self, graph):
        (fig,ax) = PlotUtils.get_figure()
        fig = PlotUtils.generate_matplotlib((fig,ax), graph)
        canvas = FigureCanvas(self, -1, fig[0])
        self.graph_sizer.Add(canvas, 1, wx.EXPAND)
        self.graph_sizer.Layout()


        self.FitInside()
        self.Refresh()  # Marquer le panel pour le rafraîchissement
        self.Update() 
        print("add graph end")
        
        
        