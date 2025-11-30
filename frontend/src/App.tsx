import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import TransactionsPage from './pages/TransactionsPage'
import ImportPage from './pages/ImportPage'
import MerchantsPage from './pages/MerchantsPage'
import TagsPage from './pages/TagsPage'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav style={{
          background: '#1f2937',
          color: 'white',
          padding: '1rem 2rem',
          marginBottom: '2rem'
        }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Finance Manager</h1>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
                Transactions
              </Link>
              <Link to="/merchants" style={{ color: 'white', textDecoration: 'none' }}>
                Merchants
              </Link>
              <Link to="/tags" style={{ color: 'white', textDecoration: 'none' }}>
                Tags
              </Link>
              <Link to="/import" style={{ color: 'white', textDecoration: 'none' }}>
                Import CSV
              </Link>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<TransactionsPage />} />
          <Route path="/merchants" element={<MerchantsPage />} />
          <Route path="/tags" element={<TagsPage />} />
          <Route path="/import" element={<ImportPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
