import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ParcelSearch from './pages/ParcelSearch'
import ParcelDetail from './pages/ParcelDetail'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="topbar">
          <div className="brand">VK-LIP</div>
          <nav>
            <Link to="/">Dashboard</Link>
            <Link to="/search">Parcel Search</Link>
          </nav>
        </header>

        <div className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/search" element={<ParcelSearch />} />
            <Route path="/parcels/:parcelNumber" element={<ParcelDetail />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
