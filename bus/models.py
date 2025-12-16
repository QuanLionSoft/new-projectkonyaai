from django.db import models


# BusLine ve BusSchedule aynı kalacak...
class BusLine(models.Model):
    ana_hat_no = models.IntegerField()
    alt_hat_no = models.IntegerField()
    ana_hat_adi = models.CharField(max_length=255)
    alt_hat_adi = models.CharField(max_length=255)
    durak_sayisi = models.IntegerField(null=True, blank=True)
    uzunluk_km = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('ana_hat_no', 'alt_hat_no')

    def __str__(self):
        return f"{self.ana_hat_no}-{self.alt_hat_no} {self.alt_hat_adi}"


class BusSchedule(models.Model):
    line = models.ForeignKey(BusLine, on_delete=models.CASCADE, related_name='schedules')
    kalkis_tarihi = models.DateTimeField()
    tarife_tipi = models.CharField(max_length=50)


class BusRoute(models.Model):
    line = models.ForeignKey(BusLine, on_delete=models.CASCADE, related_name='routes')
    yon = models.CharField(max_length=10, null=True, blank=True)
    sira = models.IntegerField()
    enlem = models.FloatField()
    boylam = models.FloatField()

    class Meta:
        ordering = ['sira']


# GÜNCELLENEN MODEL
class BusStop(models.Model):
    line = models.ForeignKey(BusLine, on_delete=models.CASCADE, related_name='stops')
    durak_no = models.CharField(max_length=50)
    sira = models.IntegerField()
    istikamet = models.CharField(max_length=255, null=True, blank=True)
    # Koordinatları ekledik
    enlem = models.FloatField(null=True, blank=True)
    boylam = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Durak {self.durak_no}"