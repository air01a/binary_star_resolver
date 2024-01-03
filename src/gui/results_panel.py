import wx
from .plot_utils import PlotUtils

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class ResultsPanel(wx.Panel):

    def __init__(self, parent, style):
        super(ResultsPanel, self).__init__(parent,style=style)
        self.graph = None
        self.parent = parent
        self.visible_result = wx.TextCtrl(self, value="Waiting for result",style=wx.TE_READONLY)
        self.frequency_result = wx.TextCtrl(self, value="Waiting for result",style=wx.TE_READONLY)
        self.figure = PlotUtils.get_figure()
        PlotUtils.set_fig_size(self.figure[0],(200,200))
        self.canvas = FigureCanvas(self, -1, self.figure[0])
        self.canvas.SetMinSize((-1, 300))

          # Gérer l'événement de redimensionnement

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)

        self.vbox.Add(self.visible_result, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self. vbox.Add(self.frequency_result, proportion=0, flag=wx.EXPAND | wx.ALL,border= 5)
        self.SetSizer(self.vbox)
        self.Bind(wx.EVT_SIZE, self.on_resize)


    def update_graph(self, graph):
        self.graph = graph
        PlotUtils.set_fig_size(self.figure[0],(self.GetSize()[0],self.GetSize()[0]))
        if graph!=None:
            self.figure[1].clear()
            (graph, peak1, peak2, lm, lr)=graph
            self.figure = PlotUtils.generate_matplotlib(self.figure, graph)
            self.canvas.draw()
        self.Refresh()  # Marquer le panel pour le rafraîchissement
        self.Update() 

    def update_results_visible(self, result_visible):
        self.visible_result.SetValue(f"Result visible : rho={result_visible}")

    def update_results_frequency(self, result_frequency):
        r, r1, r2 = result_frequency
        self.frequency_result.SetValue(f"Result Frequency : rho={r:.2f} [{r1}/{r2}]")


    def on_resize(self, event):
        # Cette méthode est appelée à chaque redimensionnement du panel
        if self.canvas:
            self.canvas.SetSize((self.GetSize()[0],self.GetSize()[0]))
            self.update_graph(self.graph)
        self.vbox.Layout()
        self.Layout()
        event.Skip() 




