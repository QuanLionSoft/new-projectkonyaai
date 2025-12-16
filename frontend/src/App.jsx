import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import BusPage from './pages/BusPage';
import BikePage from './pages/BikePage';

function App() {
  return (
    <Router>
      <div className="min-vh-100 d-flex flex-column">
        {/* Navbar */}
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
          <div className="container">
            <Link className="navbar-brand fw-bold" to="/">
              🚀 Konya Ulaşım
            </Link>
            <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarNav">
              <ul className="navbar-nav ms-auto">
                <li className="nav-item">
                  <Link className="nav-link" to="/">Panel</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/bus">Otobüsler</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/bike">Akıllı Bisiklet</Link>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        {/* İçerik Alanı */}
        <div className="container py-5">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/bus" element={<BusPage />} />
            <Route path="/bike" element={<BikePage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;