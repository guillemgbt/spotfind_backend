from spotfind_api.models import Lot, Spot
from spotfind_api.serializers import LotSerializer, SpotSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class LotList(APIView):
    """
    List all Lots or create one
    """
    def get(self, request, format=None):
        lots = Lot.objects.all()
        serializer = LotSerializer(lots, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = LotSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LotDetail(APIView):
    """
    Retrieve, update or delete a lot instance.
    """
    def get_object(self, pk):
        try:
            return Lot.objects.get(pk=pk)
        except Lot.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        lot = self.get_object(pk)
        serializer = LotSerializer(lot)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        lot = self.get_object(pk)
        serializer = LotSerializer(lot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        lot = self.get_object(pk)
        lot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SpotList(APIView):
    """
    List all Spots or create one
    """
    def get(self, request, format=None):
        spots = Spot.objects.all()
        serializer = SpotSerializer(spots, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = SpotSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpotDetail(APIView):
    """
    Retrieve, update or delete a spot instance.
    """
    def get_object(self, pk):
        try:
            return Spot.objects.get(pk=pk)
        except Spot.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        spot = self.get_object(pk)
        serializer = SpotSerializer(spot)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        spot = self.get_object(pk)
        serializer = SpotSerializer(spot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        spot = self.get_object(pk)
        spot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LotSpots(APIView):
    """
    List all spots of an lot_id.
    """

    def get_lot(self, pk):
        try:
            return Lot.objects.get(pk=pk)
        except Lot.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        lot = self.get_lot(pk)
        spots = Spot.objects.filter(lot_id=lot.id)
        serializer = SpotSerializer(spots, many=True)
        return Response(serializer.data)
