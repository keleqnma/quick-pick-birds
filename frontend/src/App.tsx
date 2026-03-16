import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import './index.css'
import Home from './pages/Home'
import Scan from './pages/Scan'
import PhotoScoring from './pages/PhotoScoring'
import Map from './pages/Map'
import Calendar from './pages/Calendar'
import Summary from './pages/Summary'
import Statistics from './pages/Statistics'
import Settings from './pages/Settings'
import Checklists from './pages/Checklists'
import SpeciesExplorer from './pages/SpeciesExplorer'

function NavBar() {
  const location = useLocation()

  return (
    <header className="header">
      <div className="container header-content">
        <h1>Quick Pick Birds</h1>
        <nav className="nav">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>首页</Link>
          <Link to="/scoring" className={location.pathname === '/scoring' ? 'active' : ''}>筛图</Link>
          <Link to="/checklists" className={location.pathname === '/checklists' ? 'active' : ''}>清单</Link>
          <Link to="/species" className={location.pathname === '/species' ? 'active' : ''}>物种</Link>
          <Link to="/map" className={location.pathname === '/map' ? 'active' : ''}>地图</Link>
          <Link to="/statistics" className={location.pathname === '/statistics' ? 'active' : ''}>统计</Link>
          <Link to="/calendar" className={location.pathname === '/calendar' ? 'active' : ''}>日历</Link>
          <Link to="/summary" className={location.pathname === '/summary' ? 'active' : ''}>小结</Link>
          <Link to="/settings" className={location.pathname === '/settings' ? 'active' : ''}>设置</Link>
        </nav>
      </div>
    </header>
  )
}

function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/scoring" element={<PhotoScoring />} />
          <Route path="/checklists" element={<Checklists />} />
          <Route path="/species" element={<SpeciesExplorer />} />
          <Route path="/map" element={<Map />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/summary" element={<Summary />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App
