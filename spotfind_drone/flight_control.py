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

        flight_state = self.get_flight_state()
        lot = self.get_lot()

        Utils.printInfo('Flight state ' + flight_state.state)
        Utils.printInfo('Analysing lot ' + lot.name)

        self.set_up_drone()
        self.set_initial_position()



    def get_flight_state(self):
        state = FlightState.objects.filter(lot_id=self.lot_id).first()
        if state is None:
            Utils.printError('No flight state when starting flight.')
            exit(0)
        return state

    def get_lot(self):
        lot = Lot.objects.filter(id=self.lot_id).first()
        if lot is None:
            Utils.printError('No flight state when starting flight.')
            self.set_state_to(constants.STATE_ERROR)
            exit(0)
        return lot

    def set_state_to(self, new_state):
        flight_state = self.get_flight_state()
        flight_state.state = new_state
        flight_state.save(update_fields=['state'])
        Utils.printInfo('setting flight state to: '+flight_state.state)

    def set_up_drone(self):

        self.drone = Tello()

        if not self.drone.connect():
            Utils.printError('Tello not connected')
            self.set_state_to(constants.STATE_ERROR)
            exit(0)

        if not self.drone.set_speed(self.drone_speed):
            Utils.printError('Not set speed to lowest possible')
            self.set_state_to(constants.STATE_ERROR)
            exit(0)

        if not self.drone.streamoff():
            Utils.printError('Could not stop video stream')
            self.set_state_to(constants.STATE_ERROR)
            exit(0)

        if not self.drone.streamon():
            Utils.printError('Could not start video stream')
            self.set_state_to(constants.STATE_ERROR)
            exit(0)

        Utils.printInfo('Drone setup successful')

    def set_initial_position(self):
        self.drone.takeoff()
        time.sleep(3)
        self.drone.land()
        time.sleep(3)

