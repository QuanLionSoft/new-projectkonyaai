from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardStats, PredictDemand, NearestStationView,
    BusLineViewSet, BusScheduleViewSet, BusRouteViewSet,
    BusStopViewSet, BikeStationViewSet
)

router = DefaultRouter()
router.register(r'bus-lines', BusLineViewSet)
router.register(r'bus-schedules', BusScheduleViewSet)
router.register(r'bus-routes', BusRouteViewSet, basename='bus-routes')
router.register(r'bus-stops', BusStopViewSet, basename='bus-stops') # YENİ
router.register(r'bike-stations', BikeStationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', DashboardStats.as_view(), name='dashboard-stats'),
    path('predict-demand/', PredictDemand.as_view(), name='predict-demand'),
    path('nearest/', NearestStationView.as_view(), name='nearest-station'), # YENİ
]
