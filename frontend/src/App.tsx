import { useState, useEffect } from 'react';
import './App.css';
import { Navbar } from './components/Navbar';
import { AdminPanel } from './components/AdminPanel';
import { CustomerSearch } from './components/CustomerSearch';
import { CampaignBuilder } from './components/CampaignBuilder';
import { Reports } from './components/Reports';
import { Footer } from './components/Footer';
import { getSimulation } from './api';

function App() {
  const [activePage, setActivePage] = useState('overview');
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    // Initial fetch to allow backend to init if needed
    getSimulation()
      .then(res => setStats(res.summary))
      .catch(() => console.log('Backend not ready'));
  }, []);

  const renderPage = () => {
    switch (activePage) {
      case 'customers':
        return <CustomerSearch />;
      case 'campaign':
        return <CampaignBuilder />;
      case 'reports':
        return <Reports />;
      case 'overview':
      default:
        return <AdminPanel stats={stats} />;
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', display: 'flex', flexDirection: 'column' }}>
      <Navbar active={activePage} onNavigate={setActivePage} />

      <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '0 2rem 2rem', flex: 1 }}>
        {renderPage()}
      </main>

      <Footer />
    </div>
  );
}

export default App;

