from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from bus.models import BusLine, BusSchedule, BusRoute, BusStop
from bike.models import BikeStation
from .serializers import (
    BusLineSerializer, BusScheduleSerializer, BusRouteSerializer,
    BusStopSerializer, BikeStationSerializer
)
import math


# Mesafe Hesaplama Fonksiyonu (Haversine)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Dünya yarıçapı (metre)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# 1. Dashboard İstatistikleri
class DashboardStats(APIView):
    def get(self, request):
        return Response({
            "total_bus_lines": BusLine.objects.count(),
            "total_schedules": BusSchedule.objects.count(),
            "total_bike_stations": BikeStation.objects.count(),
            "system_status": "Aktif"
        })


# 2. En Yakın İstasyon/Durak Bulma API'si
class NearestStationView(APIView):
    def get(self, request):
        try:
            user_lat = float(request.query_params.get('lat'))
            user_lng = float(request.query_params.get('lng'))
        except (TypeError, ValueError):
            return Response({"error": "Geçerli lat ve lng parametreleri gerekli"}, status=400)

        # A. En Yakın Bisiklet İstasyonu
        nearest_bike = None
        min_bike_dist = float('inf')

        for station in BikeStation.objects.all():
            dist = calculate_distance(user_lat, user_lng, station.enlem, station.boylam)
            if dist < min_bike_dist:
                min_bike_dist = dist
                nearest_bike = {
                    "type": "Bisiklet",
                    "name": station.istasyon_adi,
                    "lat": station.enlem,
                    "lng": station.boylam,
                    "dist_m": round(dist),
                    "info": f"Kapasite: {station.kapasite}"
                }

        # B. En Yakın Otobüs Durağı
        # Performans için tüm durakları taramak yerine, yaklaşık bir bounding box (kutu) filtrelemesi yapılabilir
        # Şimdilik ilk 5000 durak içinde arıyoruz (veya tümünü tarayabilirsiniz, sunucu hızına bağlı)
        nearest_bus = None
        min_bus_dist = float('inf')

        # Sadece koordinatı olan durakları al
        stops = BusStop.objects.exclude(enlem__isnull=True).select_related('line')

        for stop in stops:
            dist = calculate_distance(user_lat, user_lng, stop.enlem, stop.boylam)
            if dist < min_bus_dist:
                min_bus_dist = dist
                nearest_bus = {
                    "type": "Otobüs",
                    "name": f"{stop.line.ana_hat_no} Nolu Hat - Durak {stop.durak_no}",
                    "lat": stop.enlem,
                    "lng": stop.boylam,
                    "dist_m": round(dist),
                    "info": f"İstikamet: {stop.istikamet}"
                }

        return Response({
            "nearest_bike": nearest_bike,
            "nearest_bus": nearest_bus
        })


# 3. Standart ViewSet'ler
class BusLineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusLine.objects.all()
    serializer_class = BusLineSerializer


class BusScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusSchedule.objects.all().order_by('kalkis_tarihi')
    serializer_class = BusScheduleSerializer


class BusRouteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BusRouteSerializer

    def get_queryset(self):
        queryset = BusRoute.objects.all()
        line_id = self.request.query_params.get('line_id')
        if line_id:
            queryset = queryset.filter(line_id=line_id).order_by('sira')
        return queryset


class BusStopViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BusStopSerializer

    def get_queryset(self):
        queryset = BusStop.objects.all()
        line_id = self.request.query_params.get('line_id')
        if line_id:
            queryset = queryset.filter(line_id=line_id).order_by('sira')
        return queryset


class BikeStationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BikeStation.objects.all()
    serializer_class = BikeStationSerializer


# Tahmin endpoint'i (Boş placeholder)
class PredictDemand(APIView):
    def get(self, request):
        return Response([])