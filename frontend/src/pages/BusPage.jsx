import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Marker, Popup, LayersControl, LayerGroup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// --- İKON TANIMLAMALARI ---
import iconMarker from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// 1. Otobüs Durağı İkonu (Mavi - Standart)
const busStopIcon = new L.Icon({
    iconUrl: iconMarker,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// 2. Bisiklet İstasyonu İkonu (Kırmızı - CSS Filter ile)
const bikeIcon = new L.Icon({
    iconUrl: iconMarker,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
    className: 'bike-marker-icon' // CSS'de kırmızı yapılacak
});

// 3. Kullanıcı Konumu İkonu (Yeşil - CSS Filter ile)
const userIcon = new L.Icon({
    iconUrl: iconMarker,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
    className: 'user-marker-icon' // CSS'de yeşil yapılacak
});

// --- Harita Odaklama Bileşeni ---
function MapRecenter({ lat, lng }) {
    const map = useMap();
    useEffect(() => {
        if (lat && lng) {
            map.flyTo([lat, lng], 16); // Yakınlaştırma seviyesi 16
        }
    }, [lat, lng]);
    return null;
}

function BusPage() {
  const [lines, setLines] = useState([]);
  const [selectedLine, setSelectedLine] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [routePoints, setRoutePoints] = useState([]);
  const [busStops, setBusStops] = useState([]); // Seçilen hattın durakları
  const [bikeStations, setBikeStations] = useState([]); // Tüm bisiklet istasyonları

  const [userLocation, setUserLocation] = useState(null);
  const [nearestData, setNearestData] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Başlangıçta Hatları ve Bisikletleri Çek
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/bus-lines/')
      .then(res => setLines(res.data.results || res.data || []));

    axios.get('http://127.0.0.1:8000/api/bike-stations/')
      .then(res => setBikeStations(res.data.results || res.data || []));
  }, []);

  // Hat Seçimi
  const handleLineSelect = (lineId) => {
    if (!lineId) return;
    setSelectedLine(lineId);

    // Tarifeler
    axios.get(`http://127.0.0.1:8000/api/bus-schedules/`)
      .then(res => {
          const all = res.data.results || res.data || [];
          setSchedules(all.filter(s => s.line === parseInt(lineId)));
      });

    // Rota (Çizgi)
    axios.get(`http://127.0.0.1:8000/api/bus-routes/?line_id=${lineId}`)
      .then(res => {
          const points = (res.data.results || res.data).map(p => [p.enlem, p.boylam]);
          setRoutePoints(points);
      });

    // Duraklar (Nokta)
    axios.get(`http://127.0.0.1:8000/api/bus-stops/?line_id=${lineId}`)
      .then(res => {
          setBusStops(res.data.results || res.data || []);
      });
  };

  // Canlı Konum Bul
  const handleLocateMe = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        updateLocationAndFindNearest(latitude, longitude);
      }, () => alert("Konum alınamadı. Lütfen izin verin."));
    } else {
      alert("Tarayıcınız konum servisini desteklemiyor.");
    }
  };

  // Adres Arama (Nominatim API)
  const handleSearch = () => {
    if(!searchQuery) return;
    axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${searchQuery}+Konya`)
         .then(res => {
             if(res.data && res.data.length > 0) {
                 const lat = parseFloat(res.data[0].lat);
                 const lng = parseFloat(res.data[0].lon);
                 updateLocationAndFindNearest(lat, lng);
             } else {
                 alert("Adres bulunamadı.");
             }
         });
  };

  // Konumu Güncelle ve En Yakını Bul (Backend API çağrısı)
  const updateLocationAndFindNearest = (lat, lng) => {
      setUserLocation({ lat, lng });

      axios.get(`http://127.0.0.1:8000/api/nearest/?lat=${lat}&lng=${lng}`)
           .then(res => setNearestData(res.data))
           .catch(err => console.error("En yakın bulunamadı:", err));
  };

  return (
    <div className="container-fluid py-3">
      {/* İkon Renkleri İçin CSS */}
      <style>{`
        .bike-marker-icon { filter: hue-rotate(140deg); } /* Kırmızı */
        .user-marker-icon { filter: hue-rotate(260deg); } /* Yeşil/Mor */
      `}</style>

      {/* Üst Panel: Arama ve Hat Seçimi */}
      <div className="row mb-3 g-2">
        <div className="col-md-6 d-flex gap-2">
            <input
                type="text"
                className="form-control"
                placeholder="Gideceğiniz yeri yazın..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button className="btn btn-primary" onClick={handleSearch}>Ara</button>
            <button className="btn btn-success text-nowrap" onClick={handleLocateMe}>📍 Konumum</button>
        </div>
        <div className="col-md-6">
             <select className="form-select" onChange={(e) => handleLineSelect(e.target.value)}>
                <option value="">Otobüs Hattı Seçin...</option>
                {lines.map(l => (
                    <option key={l.id} value={l.id}>
                        {l.ana_hat_no} - {l.ana_hat_adi}
                    </option>
                ))}
            </select>
        </div>
      </div>

      {/* Bilgi Paneli: En Yakın İstasyonlar */}
      {nearestData && (
          <div className="alert alert-info shadow-sm d-flex flex-wrap justify-content-around align-items-center mb-3">
              {nearestData.nearest_bus && (
                  <div className="text-center">
                      <strong>🚌 En Yakın Durak</strong><br/>
                      {nearestData.nearest_bus.name}<br/>
                      <span className="badge bg-primary">{nearestData.nearest_bus.dist_m} metre</span>
                  </div>
              )}
              <div className="border-end d-none d-md-block mx-3" style={{height:'40px'}}></div>
              {nearestData.nearest_bike && (
                  <div className="text-center">
                      <strong>🚲 En Yakın Bisiklet</strong><br/>
                      {nearestData.nearest_bike.name}<br/>
                      <span className="badge bg-danger">{nearestData.nearest_bike.dist_m} metre</span>
                  </div>
              )}
          </div>
      )}

      <div className="row">
        {/* Sol Panel: Sefer Saatleri */}
        <div className="col-md-3 mb-3">
             <div className="card h-100 shadow-sm">
                 <div className="card-header bg-light fw-bold">Sefer Saatleri</div>
                 <div className="card-body p-0" style={{overflowY: 'auto', maxHeight: '500px'}}>
                     {selectedLine ? (
                        <ul className="list-group list-group-flush">
                            {schedules.length > 0 ? schedules.map(s => (
                                <li key={s.id} className="list-group-item d-flex justify-content-between">
                                    <span>{new Date(s.kalkis_tarihi).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
                                    <span className="badge bg-secondary">{s.tarife_tipi}</span>
                                </li>
                            )) : <li className="list-group-item text-muted text-center p-3">Sefer bilgisi yok.</li>}
                        </ul>
                     ) : (
                         <p className="text-muted text-center p-4">Bir hat seçtiğinizde saatler burada listelenir.</p>
                     )}
                 </div>
             </div>
        </div>

        {/* Sağ Panel: Harita */}
        <div className="col-md-9">
            <div className="card shadow-sm h-100">
                <div className="card-body p-0" style={{height: '600px'}}>
                    <MapContainer center={[37.8716, 32.4852]} zoom={13} style={{height: '100%', width: '100%'}}>
                        <TileLayer
                            attribution='&copy; OpenStreetMap'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />

                        {/* Otomatik Odaklama */}
                        {userLocation && <MapRecenter lat={userLocation.lat} lng={userLocation.lng} />}

                        {/* Kullanıcı Konumu */}
                        {userLocation && (
                            <Marker position={[userLocation.lat, userLocation.lng]} icon={userIcon}>
                                <Popup>Sizin Konumunuz</Popup>
                            </Marker>
                        )}

                        {/* KATMAN KONTROLÜ */}
                        <LayersControl position="topright">

                            {/* Bisiklet İstasyonları (Her zaman açık gelebilir) */}
                            <LayersControl.Overlay checked name="🚲 Bisiklet İstasyonları">
                                <LayerGroup>
                                    {bikeStations.map(s => (
                                        <Marker key={s.id} position={[s.enlem, s.boylam]} icon={bikeIcon}>
                                            <Popup>
                                                <b>{s.istasyon_adi}</b><br/>
                                                Kapasite: {s.kapasite}
                                            </Popup>
                                        </Marker>
                                    ))}
                                </LayerGroup>
                            </LayersControl.Overlay>

                            {/* Otobüs Hattı ve Durakları */}
                            <LayersControl.Overlay checked name="🚌 Otobüs Hattı">
                                <LayerGroup>
                                    {/* Rota Çizgisi */}
                                    {routePoints.length > 0 && (
                                        <Polyline positions={routePoints} pathOptions={{color: 'blue', weight: 5}} />
                                    )}

                                    {/* Durak Noktaları */}
                                    {busStops.map(stop => (
                                        <Marker key={stop.id} position={[stop.enlem, stop.boylam]} icon={busStopIcon}>
                                            <Popup>
                                                <b>Durak No: {stop.durak_no}</b><br/>
                                                Yön: {stop.istikamet}
                                            </Popup>
                                        </Marker>
                                    ))}
                                </LayerGroup>
                            </LayersControl.Overlay>

                        </LayersControl>
                    </MapContainer>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}

export default BusPage;