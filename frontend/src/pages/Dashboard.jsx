import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState({
    total_bus_lines: 0,
    total_schedules: 0,
    total_bike_stations: 0
  });

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/stats/')
      .then(res => setStats(res.data))
      .catch(err => console.error("Veri hatası:", err));
  }, []);

  return (
    <div>
      <h2 className="mb-4 text-secondary">Genel Durum Paneli</h2>

      <div className="row g-4">
        {/* Otobüs Kartı */}
        <div className="col-md-4">
          <div className="card h-100 border-0 shadow-sm border-start border-4 border-primary">
            <div className="card-body">
              <h6 className="text-uppercase text-muted">Toplam Hat</h6>
              <h2 className="display-4 fw-bold text-primary">{stats.total_bus_lines}</h2>
              <p className="text-muted small mb-0">Aktif Otobüs Hattı</p>
            </div>
          </div>
        </div>

        {/* Sefer Kartı */}
        <div className="col-md-4">
          <div className="card h-100 border-0 shadow-sm border-start border-4 border-success">
            <div className="card-body">
              <h6 className="text-uppercase text-muted">Planlı Sefer</h6>
              <h2 className="display-4 fw-bold text-success">{stats.total_schedules}</h2>
              <p className="text-muted small mb-0">Veritabanındaki Kayıt</p>
            </div>
          </div>
        </div>

        {/* Bisiklet Kartı */}
        <div className="col-md-4">
          <div className="card h-100 border-0 shadow-sm border-start border-4 border-warning">
            <div className="card-body">
              <h6 className="text-uppercase text-muted">Bisiklet İstasyonu</h6>
              <h2 className="display-4 fw-bold text-warning">{stats.total_bike_stations}</h2>
              <p className="text-muted small mb-0">Hizmet Veren Nokta</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;