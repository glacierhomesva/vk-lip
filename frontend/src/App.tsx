import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ParcelSearch from './pages/ParcelSearch'
import ParcelDetail from './pages/ParcelDetail'
import Delinquency from './pages/Delinquency'
import './App.css'

const TONY_STAMP = 'Tony Stamp: 2026-07-13-offer-range-v2'

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="topbar">
          <div className="brand">VK-LIP</div>
          <nav>
            <Link to="/">Dashboard</Link>
            <Link to="/search">Parcel Search</Link>
            <Link to="/delinquency">Delinquency</Link>
          </nav>
          <div className="tony-stamp">{TONY_STAMP}</div>
        </header>

        <div className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/search" element={<ParcelSearch />} />
            <Route path="/delinquency" element={<Delinquency />} />
            <Route path="/parcels/:parcelNumber" element={<ParcelDetail />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
