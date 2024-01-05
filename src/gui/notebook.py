import wx
from .graph_panel import GraphsPanel
from .frequency_graph_panel import FrequencyGraphsPanel

class NoteBookResults(wx.Notebook):
    """
    Un simple panel de contenu pour chaque onglet.
    """
    def __init__(self, parent, style, callback):
        super(NoteBookResults, self).__init__(parent, style=style)
        self.callback=callback
        self.frequency = FrequencyGraphsPanel(self, style=style)
        self.visible = GraphsPanel(self, style=style)
        self.AddPage(self.frequency, "Correlation")
        self.AddPage(self.visible, "Visible")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_change)

    def get_page(self):
        slct = self.GetSelection()
        return (slct,  self.GetPageText(slct))
        
    def on_page_change(self, event):
        print("page changed")
        self.callback(self.get_page())
        event.Skip()
        
    

