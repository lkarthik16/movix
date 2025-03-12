from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField()
    runtime = models.IntegerField()
    plot_summary = models.TextField()
    rating = models.FloatField()
    poster_url = models.URLField()

    def __str__(self):
        return self.title