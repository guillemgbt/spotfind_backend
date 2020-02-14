import os
import django
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--lot",
                  dest="lot",
                  help="Lot to fly the drone over.")
(options, args) = parser.parse_args()

if not options.lot:
    parser.error('Error: lot to scan must be specified. Pass --lot to command line')

LOT_ID = options.lot

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotfind_backend.settings")
django.setup()
from spotfind_api.models import *
from spotfind_drone.flight_control import FlightControl
from spotfind_drone.utils import Utils


def fetch_lot(id):
    lot = Lot.objects.filter(id=LOT_ID).first()

    if lot is None:
        Utils.printError('Lot '+str(LOT_ID) + ' does not exists.')
        exit(0)

    return lot


def get_create_flight_state(lot_id):
    state = FlightState.objects.filter(lot_id=lot_id).first()

    if state is None:
        state = FlightState(lot_id=lot_id)
    state.state = constants.STATE_STARTING
    state.save()

    return state


def start_flight_at(lot):
    flight_control = FlightControl(lot_id=lot.id)
    flight_control.start()

def main():
    lot = fetch_lot(id=LOT_ID)
    get_create_flight_state(lot_id=lot.id)
    start_flight_at(lot=lot)


if __name__ == "__main__":
    main()

