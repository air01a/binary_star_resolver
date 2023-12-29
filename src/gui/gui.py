import wx
from gui.main_window import MainFrame

def start_gui(broadcaster_in, broadcaster_out):
    app = wx.App(False)
    frame = MainFrame(broadcaster_in,broadcaster_out)
    app.MainLoop()