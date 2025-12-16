import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Leaflet ikon düzeltmesi
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function BikePage() {
  const [stations, setStations] = useState([]);
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/bike-stations/')
      .then(res => setStations(res.data.results || res.data));

    axios.get('http://127.0.0.1:8000/api/predict-demand/')
      .then(res => {
         if(Array.isArray(res.data)) {
             setPredictions(res.data);
         }
      })
      .catch(err => console.log("Tahmin verisi yok"));
  }, []);

  return (
    <div>
      <h2 className="mb-4 text-secondary">Akıllı Bisiklet Ağı & Tahmin</h2>

      <div className="row g-4">
        {/* SOL: Harita */}
        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">İstasyon Haritası</div>
            <div className="card-body p-2" style={{ height: '400px' }}>
              <MapContainer center={[37.8716, 32.4852]} zoom={13} scrollWheelZoom={true}>
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {stations.map((station) => (
                  <Marker key={station.id} position={[station.enlem, station.boylam]}>
                    <Popup>
                      <strong>{station.istasyon_adi}</strong><br />
                      Kapasite: {station.kapasite}
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
          </div>
        </div>

        {/* SAĞ: Tahmin Grafiği */}
        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">24 Saatlik Talep Tahmini (Yapay Zeka)</div>
            <div className="card-body d-flex align-items-center justify-content-center" style={{ height: '400px' }}>
              {predictions.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={predictions} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="prediction" name="Tahmini Talep" stroke="#0d6efd" strokeWidth={3} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center text-muted">
                  <p className="mb-0">Henüz yeterli sürüş verisi yüklenmedi.</p>
                  <small>Veri yüklendiğinde Prophet modeli burada grafik oluşturacak.</small>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BikePage;