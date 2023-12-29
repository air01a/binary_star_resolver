import wx

class MenuBar:

    def __init__(self, parent, callback):
        # Créer une barre de menu
        self.callback = callback
        self.parent = parent
        menu_bar = wx.MenuBar()

        # Créer un menu
        file_menu = wx.Menu()

        # Ajouter un item de menu
        open_dir = file_menu.Append(wx.ID_ANY, "&Ouvrir un répertoire...\tCtrl-O", "Ouvrir un répertoire")
        parent.Bind(wx.EVT_MENU, self.on_open_dir, open_dir)

        open_ser = file_menu.Append(wx.ID_ANY, "&Ouvrir un fichier SER...\tCtrl-O", "Ouvrir un fichier SER")
        parent.Bind(wx.EVT_MENU, self.on_open_file, open_ser)

        # Ajouter le menu à la barre de menu
        menu_bar.Append(file_menu, "&Fichier")

        
        
        parent.SetMenuBar(menu_bar)

    def on_open_dir(self, event):
        with wx.DirDialog(self.parent, "Choisir un répertoire", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                print("Répertoire sélectionné :", dirDialog.GetPath())
                self.callback(2001, dirDialog.GetPath())

    def on_open_file(self, event):
        # Ouvrir un FileDialog avec un filtre pour les fichiers .txt
        with wx.FileDialog(self.parent, "Ouvrir un fichier texte", wildcard="Fichiers ser (*.ser)|*.ser",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                file_path = fileDialog.GetPath()
                print("Fichier sélectionné :", file_path)
                self.callback(2001, file_path)
                # Ici, vous pouvez ouvrir et lire le fichier