

from gui.gui import start_gui
import time
import queue
import threading
from structure.message_queue import Message_Queue

from controller.main_controller import MainController


path = "../../speckles-interferometry/imagesrepo/A1174/"

def send_path(broadcaster):
    time.sleep(2)
    broadcaster.put(Message_Queue(1001,path))
    

if __name__ == "__main__":
    broadcaster_controller = queue.Queue()
    broadcaster_gui = queue.Queue()
    controller = MainController(broadcaster_gui,broadcaster_controller)
    thread = threading.Thread(target=send_path,args=(broadcaster_gui,))
    thread.start()

    start_gui(broadcaster_controller,broadcaster_gui)

