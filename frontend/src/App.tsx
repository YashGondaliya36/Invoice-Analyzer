import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Home from './pages/Home';
import UploadInvoices from './pages/UploadInvoices';
import Invoices from './pages/Invoices';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import Visualizations from './pages/Visualizations';

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<UploadInvoices />} />
          <Route path="/invoices" element={<Invoices />} />
          <Route path="/visualizations" element={<Visualizations />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/reports" element={<Reports />} />
          {/* Catch all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}

export default App;

