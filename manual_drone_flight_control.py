from djitellopy import Tello
import cv2
import pygame
import numpy as np
import time
import os
from datetime import datetime
import threading
from spotfind_drone.AI.pk_lot_detector import FasterRCNNInceptionPKLotDetector, SSDMobilenetV2PKLotDetector
from spotfind_drone.AI.is_lot_cnn import IsLotCNN
from spotfind_drone.pk_lot_data_retriever import PKLotDataRetriever

# Speed of the drone
S = 60
# Frames per second of the pygame window display
FPS = 25
#Take timestamp
TIME = datetime.now().strftime("%d-%b-%Y-(%H:%M:%S)")
#Script's directory
ROOT = os.path.abspath(os.getcwd())
#Take directory
TAKE_DIR = ROOT+'/Takes/'+TIME+'/'


class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations
            - W and S: Up and down.
    """

    def __init__(self):
        # Init pygame
        pygame.init()

        # Creat pygame window
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False
        self.record_frame = False
        self.is_processing_frame = False
        self.is_computing_spots = False
        self.image_count = 0
        self.isLotCNN = IsLotCNN()
        self.lotDetector = FasterRCNNInceptionPKLotDetector()
        self.fastLotDetector = SSDMobilenetV2PKLotDetector()

        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 50)

    def run(self):

        if not self.tello.connect():
            print("Tello not connected")
            return

        if not self.tello.set_speed(self.speed):
            print("Not set speed to lowest possible")
            return

        # In case streaming is on. This happens when we quit this program without the escape key.
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return

        frame_read = self.tello.get_frame_read()
        
        self.createTakeDir()

        should_stop = False
        while not should_stop:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if frame_read.stopped:
                frame_read.stop()
                break

            self.screen.fill([0, 0, 0])
            frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()
            
            self.captureFrameIfNeeded(frame_read.frame)

            time.sleep(1 / FPS)

        # Call it always before finishing. To deallocate resources.
        self.tello.end()
        
    def createTakeDir(self):
        try:
            os.mkdir(TAKE_DIR)
        except OSError:
            print("Creation of the directory %s failed" % TAKE_DIR)
            exit(0)
        else:
            print("Successfully created the directory %s " % TAKE_DIR)

    def captureFrameIfNeeded(self, frame):
        if self.record_frame & (not self.is_processing_frame):
            self.record_frame = False
            self.is_processing_frame = True
            t = threading.Thread(target=self.compute_frame, args=(frame), name='flight_thread')
            t.start()

    def compute_frame(self, frame):
        print('-- CAPTURING FRAME')
        lot_prob = self.isLotCNN.predict_drone_img(frame)
        if self.is_computing_spots:
            print('-- COMPTUTING SPOTS')
            pred = self.lotDetector.detect_drone_img(image=frame, confidence=0.7)
        else:
            print('-- COMPTUTING POSE')
            pred = self.fastLotDetector.detect_drone_img(image=frame, confidence=0.8)
            pred_count = len(pred)

        isLotText = '[IsLotCNN] IS LOT PROBABILITY: {}%'.format(lot_prob*100)

        print(isLotText)

        img = cv2.putText(img=frame,
                          text=isLotText,
                          org=(50, 50),
                          fontFace=cv2.FONT_HERSHEY_COMPLEX,
                          fontScale=1,
                          color=(255, 0, 0))

        img_path = TAKE_DIR + str(self.image_count) + '.jpg'
        cv2.imwrite(img_path, img=frame)
        self.image_count += 1
        self.is_processing_frame = False


    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
        elif key == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = S
        elif key == pygame.K_c:
            self.record_frame = not self.record_frame
        elif key == pygame.K_s:
            self.is_computing_spots = True
        elif key == pygame.K_p:
            self.is_computing_spots = False

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            self.tello.land()
            self.send_rc_control = False

    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)


def main():
    frontend = FrontEnd()

    # run frontend
    frontend.run()


if __name__ == '__main__':
    main()
