import threading
import time
from spotfind_api.models import *
from spotfind_api import constants
from djitellopy import Tello
from spotfind_drone.utils import Utils
from spotfind_drone.frame_capture import FrameCapture
from spotfind_drone.AI.is_lot_cnn import IsLotCNN
from spotfind_drone.AI.pk_lot_detector import SSDMobilenetV2PKLotDetector, FasterRCNNResnet50PKLotDetector
from spotfind_drone.pk_lot_data_retriever import PKLotDataRetriever
import matplotlib.pyplot as plt
import random


class FlightControl:

    def __init__(self, lot_id):
        self.lot_id = lot_id
        self.initial_height = 500
        self.drone_speed = 10
        self.drone = None
        self.ssd_pklot = None
        self.ssd_lot_thr = 3
        self.ssd_detect_conf = 0.8
        self.frcnn_pklot = None
        self.frcnn_detect_conf = 0.7
        self.cnn_is_lot = None
        self.is_lot_thr = 0.8
        self.info_retriever = PKLotDataRetriever(lot_id=lot_id)

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
        Utils.printInfo('Done is in initial position')

        stream = self.prepare_stream()

        self.set_state_to(constants.STATE_SCANNING)

        while True:
            time.sleep(2)

            img = stream.frame

            Utils.printInfo('Finding initial pose.')

            while not self.is_pointing_to_lot(image=img):
                Utils.printInfo('Not pointing to lot in initial position yet.')
                self.adjust_initial_pose()
                img = stream.frame

                if self.should_finish_flight():
                    break

            if self.should_finish_flight():
                break

            Utils.printInfo('Initial pose found')
            Utils.printInfo('Retrieving info from image.')
            self.retrieve_info_from(image=img, clear_db_spots=True)

            #Adjust height if needed
            height = self.drone.get_height()
            Utils.printInfo('drone height: '+str(height))

            if self.should_finish_flight():
                break

            break #To test only one iteration




        Utils.printInfo('Loop Done')

        stream.stop()
        self.finish_flight()

    def retrieve_info_from(self, image, clear_db_spots):
        detections = self.frcnn_pklot.detect_drone_img(image, confidence=self.frcnn_detect_conf)
        self.info_retriever.retrieve_data_from(lot_image=image,
                                               predictions=detections,
                                               should_clear_spots=clear_db_spots)

    def is_pointing_to_lot(self, image):
        is_lot = self.cnn_is_lot.predict_drone_img(image=image)
        lots = self.ssd_pklot.detect_drone_img(image, confidence=self.ssd_detect_conf)
        lot_count = len(lots)
        Utils.printInfo('isLot: {0:.3f}, ssd lots: {} at {} conf.'.format(is_lot, lot_count, self.ssd_detect_conf))
        return (is_lot >= self.is_lot_thr) & (lot_count >= self.ssd_lot_thr)

    def adjust_initial_pose(self):
        Utils.printInfo('Adjusting initial position')
        rotation_direction = random.randint(0, 1)
        rotation_angle = random.randint(20, 180)
        forward_distance = random.randint(100, 300)

        if rotation_direction:
            Utils.printInfo('Rotating clockwise: {}'.format(rotation_angle))
            self.drone.rotate_clockwise(rotation_angle)
        else:
            Utils.printInfo('Rotating counter clockwise: {}'.format(rotation_angle))
            self.drone.rotate_counter_clockwise(rotation_angle)

        time.sleep(1)

        Utils.printInfo('Moving forward: {}'.format(forward_distance))
        self.drone.move_forward(forward_distance)
        time.sleep(1)


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

    def set_up_networks(self):
        self.frcnn_pklot = FasterRCNNResnet50PKLotDetector()
        self.ssd_pklot = SSDMobilenetV2PKLotDetector()
        self.cnn_is_lot = IsLotCNN()

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
        if not self.drone.move_up(self.initial_height):
            Utils.printError('Could not set initial height')
            self.set_state_to(constants.STATE_ERROR)
            exit(0)

    def should_finish_flight(self):
        flight_state = self.get_flight_state()
        return flight_state.state == constants.STATE_STOPPING or flight_state.state == constants.STATE_ERROR

    def finish_flight(self):
        self.drone.land()
        time.sleep(2)
        self.set_state_to(constants.STATE_LANDED)  # 17
        self.drone.end()


