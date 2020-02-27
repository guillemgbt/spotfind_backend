import threading
import time
from spotfind_api.models import *
from spotfind_api import constants
from djitellopy import Tello
from spotfind_drone.utils import Utils
from spotfind_drone.frame_capture import FrameCapture
from spotfind_drone.AI.is_lot_cnn import IsLotCNN
from spotfind_drone.AI.pk_lot_detector import SSDInceptionPKLotDetector, FasterRCNNResnet50PKLotDetector
import matplotlib.pyplot as plt


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
        #self.set_initial_position()

        stream = self.prepare_stream()

        Utils.printInfo('Stream set up')

        cnn = IsLotCNN()
        detector = FasterRCNNResnet50PKLotDetector()

        should_stop = False
        plt.ion()
        self.set_state_to(constants.STATE_SCANNING)
        while not should_stop:
            time.sleep(2)
            img = stream.frame

            print('-----')

            lot_prob = cnn.predict_drone_img(image=img)
            pk_boxes = detector.detect_drone_img(img, confidence=0.8)

            print('-> Is lot with {} of probability'.format(lot_prob))
            print('-> {} lot detections at {} conf. level'.format(len(pk_boxes), 0.8))
            [print(' -> {} - {}'.format(box.get_class(), box.get_box())) for box in pk_boxes]
            print('-----')

            plt.imshow(img)
            plt.pause(0.05)

            height = self.drone.get_height()
            Utils.printInfo('drone height: '+str(height))

            flight_state = self.get_flight_state()
            should_stop = flight_state.state == constants.STATE_STOPPING
            should_stop = True


            # Adjust position with SSD and Img Class (4 positions (90 degrees))
                #if successful -> Obj Detection + process
            # Far movement. Stop using SSD and Img Class



        Utils.printInfo('Loop Done')

        stream.stop()
        self.finish_flight()


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

    def prepare_stream(self):
        stream = FrameCapture(drone=self.drone)
        stream.start()
        time.sleep(3)
        return stream

    def set_initial_position(self):
        self.drone.takeoff()
        time.sleep(3)

    def finish_flight(self):
        self.drone.land()
        time.sleep(2)
        self.set_state_to(constants.STATE_LANDED)  # 17
        self.drone.end()


