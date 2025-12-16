from rest_framework import serializers
from bus.models import BusLine, BusSchedule, BusRoute, BusStop
from bike.models import BikeStation

class BusLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusLine
        fields = '__all__'

class BusScheduleSerializer(serializers.ModelSerializer):
    hat_bilgisi = serializers.CharField(source='line.__str__', read_only=True)
    class Meta:
        model = BusSchedule
        fields = ['id', 'line', 'hat_bilgisi', 'kalkis_tarihi', 'tarife_tipi']

class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = ['enlem', 'boylam', 'sira', 'yon']

# YENİ: Otobüs Durakları için Serializer
class BusStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusStop
        fields = ['durak_no', 'sira', 'istikamet', 'enlem', 'boylam']

class BikeStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeStation
        fields = '__all__'