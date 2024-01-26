from django.db import models
from django.utils.html import mark_safe


def quest_directiory_path(instance, filename):
    return "quest_points/{0}".format(filename)


class Coordinate(models.Model):
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


class QuestPoint(models.Model):
    title = models.CharField(
        max_length=100, blank=False, null=False, default="No title"
    )
    description = models.TextField(blank=False, null=False, default="No description")
    location = models.ForeignKey(Coordinate, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to=quest_directiory_path, null=True)

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
