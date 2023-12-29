import threading
from structure.message_queue import Message_Queue

from image_utils.image_utils import load_speckle_images, get_image_from_directory
from controller.processing_controller import ProcessingController
from structure.plot_graph import PlotGraph
from os.path import splitext, isfile, isdir


class MainController:
    def __init__(self, broadcaster_gui, broadcaster_out):
        self.broadcaster_gui = broadcaster_gui
        self.broadcaster_out = broadcaster_out
        thread = threading.Thread(target=self.main_controller)
        self.processingController = ProcessingController(self.broadcaster_out)
        thread.start()

    def calculate_psd(self):
        if self.images==None:
            return
        self.spectral_density = self.processingController.psd(self.images)

    def psd(self):
        self.broadcaster_out.put(Message_Queue(1,PlotGraph(self.spectral_density,"Fonction de densité spéctrale", cmap="viridis")))


    def mean_filter(self):
        self.processingController.mean_filter()

    def get_ellipse(self):
        self.broadcaster_out.put(Message_Queue(1,PlotGraph(self.processingController.find_ellipse(),"Ellipse", cmap="viridis")))

    def minor_major_star(self):
        self.broadcaster_out.put(Message_Queue(1,PlotGraph(self.processingController.get_minus_major_star(),"Minus major star", cmap="viridis")))

    def find_peaks(self):
        (x,y, lines, dist1, dist2, lm, lr) = self.processingController.analyze_peaks()
        graph = (PlotGraph((x,y),"Peaks", cmap="viridis", type='plot',lines=lines), dist1, dist2, lm, lr)
        self.broadcaster_out.put(Message_Queue(4,graph))

    def clip(self):
        self.broadcaster_out.put(Message_Queue(1,PlotGraph(self.processingController.clip(),"Mean filter", cmap="viridis")))

    def calculation_loop(self):
        #self.processingController.process(self.psd)
        self.psd()
        self.clip()
        self.get_ellipse()
        self.minor_major_star()
        self.find_peaks()

    def event_routing(self, event_type, event_data):
        match event_type:
            # New directory
            case 1001:
                self.broadcaster_out.put(Message_Queue(3,None))
                if isdir(event_data):
                    paths = get_image_from_directory(event_data)
                else:
                    paths=event_data
                self.images = load_speckle_images(paths)
                self.broadcaster_out.put(Message_Queue(2,self.images))
                self.calculate_psd()
                self.mean_filter()
                self.calculation_loop()
            # Sliders change
            case 1002:
                self.processingController.min_value = event_data["min"]
                self.processingController.max_value = event_data["max"]
                self.processingController.radius = event_data["radius"]
                self.broadcaster_out.put(Message_Queue(3,None))
                self.calculation_loop()

    def main_controller(self):

        while True:
            message = self.broadcaster_gui.get()
            if message.get_type() == 0:
                break
            self.event_routing(message.get_type(), message.get_data())
            self.broadcaster_gui.task_done()

