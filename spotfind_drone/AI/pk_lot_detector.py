import tensorflow as tf
import numpy as np
from PIL import Image
import os
from matplotlib import pyplot as plt
from matplotlib import patches
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class PKLotBox(object):
    def __init__(self, xmin, ymin, xmax, ymax, occupancy, confidence):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.occupancy = occupancy
        self.confidence = confidence

    def get_box(self):
        return np.array([self.xmin, self.ymin, self.xmax, self.ymax])

    def get_class(self):
        return "occupied" if self.occupancy == 1.0 else "free"

    @staticmethod
    def parse_classification(image, boxes, scores, classes, confidence):
        width = image.shape[1]
        height = image.shape[0]

        pk_boxes = [PKLotBox(xmin=boxes[0][index][1] * width,
                             ymin=boxes[0][index][0] * height,
                             xmax=boxes[0][index][3] * width,
                             ymax=boxes[0][index][2] * height,
                             occupancy=classes[0][index],
                             confidence=score) for index, score in enumerate(scores[0]) if score > confidence]

        return pk_boxes


class ParkingLotDetector(object):
    def __init__(self, model_filepath='frozen_networks/frcnn_resnet50_frozen_network.pb'):
        self.model_filepath = os.path.dirname(os.path.abspath(__file__)) + '/' + model_filepath
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.model_filepath, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            self.d_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.d_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.d_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_d = self.detection_graph.get_tensor_by_name('num_detections:0')
        self.sess = tf.Session(graph=self.detection_graph)

    def get_classification_from_path(self, img_path, confidence):

        image = ParkingLotDetector.load_image_into_numpy_array(Image.open(img_path))

        with self.detection_graph.as_default():
            # Expand dimension since the model expects image to have shape [1, None, None, 3].
            img_expanded = np.expand_dims(image, axis=0)
            (boxes, scores, classes, num) = self.sess.run(
                [self.d_boxes, self.d_scores, self.d_classes, self.num_d],
                feed_dict={self.image_tensor: img_expanded})

        return PKLotBox.parse_classification(image, boxes, scores, classes, confidence)

    def detect_drone_img(self, image, confidence):

        with self.detection_graph.as_default():
            # Expand dimension since the model expects image to have shape [1, None, None, 3].
            img_expanded = np.expand_dims(image, axis=0)
            (boxes, scores, classes, num) = self.sess.run(
                [self.d_boxes, self.d_scores, self.d_classes, self.num_d],
                feed_dict={self.image_tensor: img_expanded})
        return PKLotBox.parse_classification(image, boxes, scores, classes, confidence)

    @staticmethod
    def load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

    @staticmethod
    def visualize(image, detections, score_threshold):
        fig, ax = plt.subplots(1)

        # add axes to the image
        ax = fig.add_axes([0, 0, 1, 1])

        # add bounding boxes to the image
        for index, detection in enumerate(detections):
            if detection.confidence >= score_threshold:
                y_min = detection.ymin
                x_min = detection.xmin
                y_max = detection.ymax
                x_max = detection.xmax
                occupancy = detection.get_class()

                color = 'r'
                if occupancy == 'free':
                    color = 'b'

                box_width = x_max - x_min
                box_height = y_max - y_min

                rect = patches.Rectangle((x_min, y_min), box_width, box_height, edgecolor=color, facecolor='none')
                ax.add_patch(rect)

        ax.imshow(image)
        plt.show()


class FasterRCNNResnet50PKLotDetector(ParkingLotDetector):
    def __init__(self):
        super().__init__(model_filepath='frozen_networks/frcnn_resnet50_frozen_network.pb')


class SSDMobilenetV2PKLotDetector(ParkingLotDetector):
    def __init__(self):
        super().__init__(model_filepath='frozen_networks/ssd_mobilenet_v2_frozen_network.pb')


class SSDInceptionPKLotDetector(ParkingLotDetector):
    def __init__(self):
        super().__init__(model_filepath='frozen_networks/ssd_inception_frozen_network.pb')


class FasterRCNNInceptionPKLotDetector(ParkingLotDetector):
    def __init__(self):
        super().__init__(model_filepath='frozen_networks/frcnn_inception_frozen_network.pb')
