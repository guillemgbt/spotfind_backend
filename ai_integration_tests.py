import os
import django
import cv2
import matplotlib.image as mpimg


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotfind_backend.settings")
django.setup()

from spotfind_drone.AI.is_lot_cnn import IsLotCNN
from spotfind_drone.AI.pk_lot_detector import FasterRCNNResnet50PKLotDetector, SSDMobilenetV2PKLotDetector


def predict_drone_img_to_isLot_prob():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    img = cv2.imread(img_path)
    cnn = IsLotCNN()
    out = cnn.predict(image=img)
    print('  -> PROB: {} being lot for image {}'.format(out, img_path))


def predict_drone_img_lot_detection_frcnn_resnet50():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    detector = FasterRCNNResnet50PKLotDetector()
    boxes, scores, classes, num = detector.get_classification(img_path=img_path)
    print()
    print('  -> First PKLot detection with FRCNNResnet50: {} at {} confidance level'.format(boxes[0,0,:], scores[0,0]))

def predict_drone_img_lot_detection_ssd_mobilenet_v2():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    detector = SSDMobilenetV2PKLotDetector()
    boxes, scores, classes, num = detector.get_classification(img_path=img_path)
    print()
    print('  -> First PKLot detection with SSDMobilenetV2: {} at {} confidance level'.format(boxes[0,0,:], scores[0,0]))


def main():
    predict_drone_img_to_isLot_prob()
    predict_drone_img_lot_detection_frcnn_resnet50()
    predict_drone_img_lot_detection_ssd_mobilenet_v2()


if __name__ == "__main__":
    main()

