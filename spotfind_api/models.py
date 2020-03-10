from django.db import models
from spotfind_api import constants
from spotfind_backend import settings

class Lot(models.Model):
    name = models.CharField(max_length=100, blank=False, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(blank=True, null=True)
    occupancy = models.FloatField(blank=True, null=True)
    tendency = models.CharField(max_length=100, blank=False, default=constants.LOT_TENDENCY_SAME)

    class Meta:
        ordering = ('-created',)


class Spot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True)
    is_free = models.BooleanField()
    lot_id = models.IntegerField()

    def get_img_file(self):
        return str(self.id)+'_'+str(self.lot_id)+'_img.jpg'

    def get_img_path(self):
        return settings.BASE_DIR + settings.MEDIA_URL+self.get_img_file()

    class Meta:
        ordering = ('-created',)


class FlightState(models.Model):
    state = models.CharField(max_length=100, blank=False, default=constants.STATE_LANDED)
    lot_id = models.IntegerField()
    enabled = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

