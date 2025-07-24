import { AuthProvider } from './contexts/AuthContext';
import { BrowserRouter as Router, Route, Routes, useLocation } from "react-router-dom";
import { Suspense, lazy } from 'react';
import Footer from "./components/Navigation/Footer";
import { Navbar } from "./components/Navigation/Navbar";
import LoginPage from './pages/LoginPage';
import AuthCallbackPage from './pages/AuthCallbackPage';
import FullScreenLoader from "./components/utils/FullScreenLoader";

// --- Lazy-loaded Page Components ---
const HomePage = lazy(() => import('./pages/HomePage'));
const Layout = lazy(() => import('./components/Dashboard/Layout'));
const StatsDashboard = lazy(() => import('./components/Statistics/StatsDashboard'));

const AppLayout = () => {
  const location = useLocation();
  const isDashboardRoute = location.pathname.startsWith('/dashboard');

  return (
    <>
      {!isDashboardRoute && <Navbar />}
      
      <Suspense fallback={<FullScreenLoader />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard/*" element={<Layout />} />
          <Route path="/stats" element={<StatsDashboard />} />
          <Route path="/product" element={<div>Product Page</div>} />
          <Route path="/developers" element={<div>Developers Page</div>} />
          <Route path="/pricing" element={<div>Pricing Page</div>} />
          <Route path="/enterprise" element={<div>Enterprise Page</div>} />
          <Route path="/blog" element={<div>Blog Page</div>} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
        </Routes>
      </Suspense>
      
      {!isDashboardRoute && <Footer />}
    </>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </Router>
  );
}

export default App;
