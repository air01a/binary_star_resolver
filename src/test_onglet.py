import wx

class TabPanel(wx.Panel):
    """
    Un simple panel de contenu pour chaque onglet.
    """
    def __init__(self, parent, title):
        super(TabPanel, self).__init__(parent)

        text = wx.StaticText(self, label="Contenu de l'onglet " + title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 10)
        self.SetSizer(sizer)

class MainWindow(wx.Frame):
    """
    La fenêtre principale contenant le widget Notebook.
    """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Créer le widget Notebook
        notebook = wx.Notebook(self)

        # Créer les onglets
        tab1 = TabPanel(notebook, "1")
        tab2 = TabPanel(notebook, "2")
        tab3 = TabPanel(notebook, "3")

        # Ajouter les onglets au notebook
        notebook.AddPage(tab1, "Onglet 1")
        notebook.AddPage(tab2, "Onglet 2")
        notebook.AddPage(tab3, "Onglet 3")

        self.SetTitle("Exemple d'Onglets avec wxPython")
        self.Show()

if __name__ == "__main__":
    app = wx.App(False)
    window = MainWindow(None)
    app.MainLoop()
