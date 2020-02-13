from spotfind_api.models import *
from rest_framework import serializers


class LotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = ('id', 'name', 'created', 'updated', 'image', 'occupancy', 'tendency')


class SpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spot
        fields = ('id', 'created', 'image', 'is_free', 'lot_id')


class FlightStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightState
        fields = ('id', 'state', 'lot_id', 'created')
