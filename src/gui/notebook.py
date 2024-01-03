import wx
from .graph_panel import GraphsPanel
from .frequency_graph_panel import FrequencyGraphsPanel

class NoteBookResults(wx.Notebook):
    """
    Un simple panel de contenu pour chaque onglet.
    """
    def __init__(self, parent, style):
        super(NoteBookResults, self).__init__(parent, style=style)
    
        self.frequency = FrequencyGraphsPanel(self, style=style)
        self.visible = GraphsPanel(self, style=style)
        self.AddPage(self.frequency, "Correlation")
        self.AddPage(self.visible, "Visible")

    

