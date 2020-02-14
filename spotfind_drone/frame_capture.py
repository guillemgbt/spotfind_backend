from threading import Thread
import cv2
import numpy as np
from djitellopy import Tello
from spotfind_drone.utils import Utils


class FrameCapture:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, drone=None):
        self.i = 0
        self.frame = None
        self.stream = None
        self.grabbed = False
        if drone:
            self.ip = drone.get_udp_video_address()
            self.stream = cv2.VideoCapture(self.ip)
        else:
            self.stream = cv2.VideoCapture(0)
        self.prepare_frame_from_stream()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                Utils.printInfo('NOT GRABBED')
                self.stop()
            else:
                self.prepare_frame_from_stream()

        if self.stream:
            self.stream.release()
            Utils.printInfo('stream released')

        Utils.printInfo('Final get background thread')

    def prepare_frame_from_stream(self):
        (self.grabbed, _frame) = self.stream.read()
        if self.grabbed:
            _frame = cv2.cvtColor(_frame, cv2.COLOR_BGR2RGB)
            self.frame = _frame

    def stop(self):
        self.stopped = True
