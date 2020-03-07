from spotfind_api.models import Lot, Spot
from spotfind_drone.utils import Utils
from spotfind_api import constants
import os
import cv2


class PKLotDataRetriever(object):

    def __init__(self, lot_id):
        self.lot_id = lot_id

    def retrieve_data_from(self, lot_image, predictions, should_clear_spots=False, confidence=None):
        """
        :param lot_image: original image where detections have been found
        :param predictions: predictions form pk lot detector
        :return:
        """

        if should_clear_spots:
            Utils.printInfo('Clearing spots')
            self.clear_spots()

        _preds = predictions
        if confidence is not None:
            _preds = [prediction for prediction in _preds if prediction.confidence >= confidence]

        lot = self.fetch_lot()

        Utils.printInfo('Analysing lot: ' + lot.name)
        Utils.printInfo('Processing {} lots'.format(len(_preds)))

        self.compute_spots_from(image=lot_image, predictions=_preds)
        self.compute_lot_state_info()


    def compute_spots_from(self, image, predictions):
        for pred in predictions:
            pred_img_crop = self.compute_crop_prediction_img(pred, image)
            self.register_spot(pred, pred_img_crop)

    def compute_crop_prediction_img(self, prediction, image, box_offset=50):
        width = image.shape[1]
        height = image.shape[0]
        x_min_off = int(max(prediction.xmin - box_offset, 0))
        x_max_off = int(min(prediction.xmax + box_offset, width))
        y_min_off = int(max(prediction.ymin - box_offset, 0))
        y_max_off = int(min(prediction.ymax + box_offset, height))
        return image[y_min_off:y_max_off, x_min_off:x_max_off, :]

    def register_spot(self, prediction, spot_image):
        spot = Spot(is_free=prediction.get_class() == 'free', lot_id=self.lot_id)
        spot.save()
        cv2.imwrite(spot.get_img_path(), img=cv2.cvtColor(spot_image, cv2.COLOR_BGR2RGB))
        spot.image = '/' + spot.get_img_file()
        spot.save()

    def compute_lot_state_info(self):
        spots = Spot.objects.filter(lot_id=self.lot_id)
        lot = self.fetch_lot()
        old_occupancy = lot.occupancy
        new_occupancy = sum(not spot.is_free for spot in spots)/spots.count()
        new_tendency = self.get_tendency_from(new_occupancy, old_occupancy)
        Utils.printInfo('New occupancy: {}, Old occupancy: {}'.format(new_occupancy, old_occupancy))
        Utils.printInfo('New tendency: {}, Old tendency: {}'.format(new_tendency, lot.tendency))
        lot.occupancy = new_occupancy
        lot.tendency = new_tendency
        lot.save()

    def get_tendency_from(self, new_o, old_o):
        diff = new_o - old_o
        if abs(diff) <= 0.01:
            return constants.LOT_TENDENCY_SAME
        if diff > 0:
            if abs(diff) > 0.4:
                return constants.LOT_TENDENCY_HIGHER
            else:
                return constants.LOT_TENDENCY_HIGH
        else:
            if abs(diff) > 0.4:
                return constants.LOT_TENDENCY_LOWER
            else:
                return constants.LOT_TENDENCY_LOW

    def fetch_lot(self):
        lot = Lot.objects.filter(id=self.lot_id).first()
        if lot is None:
            Utils.printError('Could not fetch lot from PKLotDataRetriever')
            exit(0)
        return lot

    def clear_spots(self):
        spots = Spot.objects.filter(lot_id=self.lot_id)
        for spot in spots:
            img_path = '.'+spot.image.url
            os.remove(img_path)
        spots.delete()
