from spotfind_api.models import Lot, Spot
from spotfind_drone.utils import Utils
import os


class PKLotDataRetriever(object):

    def __init__(self, lot_id):
        self.lot_id = lot_id

    def retrieve_data_from(self, lot_image, predictions, confidence=None):
        """
        :param lot_image: original image where detections have been found
        :param predictions: predictions form pk lot detector
        :return:
        """

        self.clear_spots()

        _preds = predictions
        if confidence is not None:
            _preds = [prediction for prediction in _preds if prediction.confidence >= confidence]

        lot = self.fetch_lot()

        print('Analysing lot: '+lot.name)
        print('{} filtered predictions'.format(len(_preds)))

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
