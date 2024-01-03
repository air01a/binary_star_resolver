import wx
import wx.adv
class LoadingDialog:
    def __init__(self, parent, title):
        #wx.Frame.__init__(self, None, wx.ID_ANY, "Tutorial", size=(500,500))
        
        bitmap = wx.Bitmap('images/loader.png')
        self.splash = wx.adv.SplashScreen(
                     bitmap, 
                     wx.adv.SPLASH_CENTER_ON_SCREEN|wx.adv.SPLASH_NO_TIMEOUT, 
                     0, parent)
        self.splash.Show()

    def close(self):
        try:
            self.splash.Close()
        except:
            print("Splash screen already closed")