import os
import django
import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotfind_backend.settings")
django.setup()

from spotfind_drone.pk_lot_data_retriever import *
from spotfind_drone.AI.pk_lot_detector import *


def main():

    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    image = ParkingLotDetector.load_image_into_numpy_array(Image.open(img_path))

    detector = FasterRCNNInceptionPKLotDetector()
    boxes = detector.detect_drone_img(image, confidence=0.8)

    print('{} Detections'.format(len(boxes)))

    retriever = PKLotDataRetriever(lot_id=1)
    retriever.retrieve_data_from(lot_image=image, predictions=boxes, confidence=0.9)


    #plt.imshow(image)
    #plt.show()


if __name__ == "__main__":
    main()
