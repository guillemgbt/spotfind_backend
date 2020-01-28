from django.db import models
from spotfind_api import constants


class Lot(models.Model):
    name = models.CharField(max_length=100, blank=False, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
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

    class Meta:
        ordering = ('-created',)

