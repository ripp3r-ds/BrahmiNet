import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Credits from './pages/Credits';
import { Github } from 'lucide-react';

function Navigation() {
  const location = useLocation();

  return (
    <nav>
      <Link to="/" className="logo gradient-text">BrahmiNet</Link>
      <div className="links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Search</Link>
        <Link to="/about" className={location.pathname === '/about' ? 'active' : ''}>About</Link>
        <Link to="/credits" className={location.pathname === '/credits' ? 'active' : ''}>Credits</Link>
        <a href="https://github.com/ripp3r-ds/BrahmiNet" target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <Github size={18} /> Repo
        </a>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <Navigation />
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/credits" element={<Credits />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
