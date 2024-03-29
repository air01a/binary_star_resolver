import threading
from structure.message_queue import Message_Queue

from image_utils.image_utils import load_speckle_images, get_image_from_directory
from analyzer.frequency import FrequencyAnalyzer
from analyzer.visible import VisibleAnalyzer
from structure.plot_graph import PlotGraph
from os.path import isdir, basename, splitext
import utils.constant as CONSTANT
from controller.result_controller import ResultController


class MainController:
    def __init__(self, broadcaster_gui, broadcaster_out):
        self.broadcaster_gui = broadcaster_gui
        self.broadcaster_out = broadcaster_out
        self.result_controller = ResultController(0.099)
        thread = threading.Thread(target=self.main_controller)
        self.frequencyAnalyzer = FrequencyAnalyzer(self.result_controller)
        self.visibleAnalyzer = VisibleAnalyzer(self.result_controller)
        thread.start()
        self.star_name=""

    def calculate_psd(self):
        if self.images==None:
            return
        self.spectral_density = self.frequencyAnalyzer.psd(self.images)

    def psd(self):
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_FREQUENCY_GRAPH,PlotGraph(self.spectral_density,f"{self.star_name} : Fonction de densité spectrale", cmap="viridis",num=0)))


    def mean_filter(self):
        self.frequencyAnalyzer.mean_filter()

    def get_ellipse(self):
        try:
            self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_FREQUENCY_GRAPH,PlotGraph(self.frequencyAnalyzer.find_ellipse(),f"{self.star_name} : Ellipse", cmap="viridis",num=2)))
            return True
        except:
            self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ERROR,"Error, no ellipse found, please use cursors to help to identify it"))
            self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_CLEAR_FREQUENCY,[2,3]))
            return False

    def minor_major_star(self):
        try:
            self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_FREQUENCY_GRAPH,PlotGraph(self.frequencyAnalyzer.get_minus_major_star(),f"{self.star_name} : Minus major star", cmap="gray",num=3)))
            return True
        except Exception as e:
            self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ERROR,"Error minoring main peak, the ellipse may be not a good one, please use cursor to redefine it"))
            self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_CLEAR_FREQUENCY,[3]))
            print(e)
            return False

    def find_peaks(self):
        (x,y, lines, dist1, dist2, lm, lr, angle) = self.frequencyAnalyzer.analyze_peaks()
        if angle<0:
            angle+=360
        graph = (PlotGraph((x,y),"Peaks", cmap="viridis", type='plot',lines=lines), dist1, dist2, lm, lr)

        self.broadcaster_out.put(Message_Queue(4,graph))
        self.broadcaster_out.put(Message_Queue(6,(0.099*min(abs(dist1),abs(dist2)), dist1, dist2, angle)))
        x,y,y2 = self.frequencyAnalyzer.approximate()
        graph = PlotGraph((x,y,y2),"Peaks", cmap="viridis", type='plot',num=4, lines=lines,markers=['x','o'], colors=['green','red'],linestyle=['-','--'])
        #self.broadcaster_out.put(Message_Queue(4,graph))
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_FREQUENCY_GRAPH,graph))

        #self.broadcaster_out.put(Message_Queue(5,self.frequencyAnalyzer.rho))

    def clip(self):
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_FREQUENCY_GRAPH,PlotGraph(self.frequencyAnalyzer.clip(),f"{self.star_name} : Mean filter", cmap="viridis",num=1)))

    def calculation_loop(self):
        #self.frequencyAnalyzer.process(self.psd)
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_NO_ERROR,None))
        self.psd()
        self.clip()
        if self.get_ellipse():
            if self.minor_major_star():
                self.find_peaks()
        

    def visible_calculation_loop(self):
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_CLEAR_VISIBLE_GRAPH,None))
        (im1, im2) = self.visibleAnalyzer.stack_best(self.images)
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_VISIBLE_GRAPH,PlotGraph(im1,f"{self.star_name} : Visible stacking", cmap="viridis")))
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_VISIBLE_GRAPH,PlotGraph(im2,f"{self.star_name} : Visible stacking mean", cmap="viridis")))
        x1,y1,x2,y2,rho, angle = self.visibleAnalyzer.get_peaks()
        im = self.visibleAnalyzer.draw_peaks(im1,x1,y1,x2,y2)
        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_VISIBLE_GRAPH,PlotGraph(im,f"{self.star_name} : Peaks in visible", cmap="viridis")))
        if angle<0:
            angle+=360


        self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_UPDATE_RESULT_VISIBLE,(rho,angle)))



    def event_routing(self, event_type, event_data):
        print("Main controller event rooting : "+str(event_type))
        match event_type:
            # New directory
            case CONSTANT.EVENT_NEW_DIR:
                self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_CLEAR_FREQUENCY_GRAPH,None))
                if isdir(event_data):
                    paths = get_image_from_directory(event_data)
                    self.star_name = basename(event_data.rstrip('/'))
                else:
                    paths=event_data
                    self.star_name = splitext(basename(event_data))[0]
                self.images = load_speckle_images(paths)
                self.broadcaster_out.put(Message_Queue(CONSTANT.EVENT_ADD_SPECKLE_IMAGE,self.images))
                self.calculate_psd()
                self.mean_filter()
                self.calculation_loop()
                self.visible_calculation_loop()
            # Sliders change
            case CONSTANT.EVENT_NEW_PARAMS:
                if event_data["type"][0]==0:
                    self.frequencyAnalyzer.min_value = event_data["min"]
                    self.frequencyAnalyzer.max_value = event_data["max"]
                    self.frequencyAnalyzer.radius = event_data["radius"]
                    
                    self.calculation_loop()
                else:
                    self.visibleAnalyzer.min_value = event_data["min"]
                    self.visibleAnalyzer.max_value = event_data["max"]
                    self.visibleAnalyzer.radius = event_data["radius"]
                    
                    self.visible_calculation_loop()
            case CONSTANT.EVENT_NEW_NUMBER:
                
                if event_data["type"][0]==0:
                    self.frequencyAnalyzer.number_of_images=event_data["number"]
                    self.frequencyAnalyzer.mean_f = event_data["mean"]
                    self.calculate_psd()
                    self.mean_filter()
                    self.calculation_loop()
                else:
                    self.visibleAnalyzer.number_of_images=event_data["number"]
                    self.visibleAnalyzer.mean_f = event_data["mean"]
                    self.visible_calculation_loop()
        self.result_controller.populate_result()
        self.result_controller.print_result()


    def main_controller(self):
        while True:
            message = self.broadcaster_gui.get()
            if message.get_type() == 0:
                break
            self.event_routing(message.get_type(), message.get_data())
            self.broadcaster_gui.task_done()

