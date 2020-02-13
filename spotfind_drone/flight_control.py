import threading
import time
from spotfind_api.models import *
from spotfind_api import constants
from djitellopy import Tello
from spotfind_drone.utils import Utils
from spotfind_drone.frame_capture import FrameCapture


class FlightControl:

    def __init__(self, lot_id):
        self.lot_id = lot_id
        self.time_constant = 0.2
        self.drone_speed = 10
        self.drone = None

    def async_start(self):
        t = threading.Thread(target=self.start, name='flight_thread')
        t.start()

    def start(self):
        Utils.printInfo('Flight control start')
