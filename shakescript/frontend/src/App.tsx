import { AuthProvider } from './contexts/AuthContext';
import { BrowserRouter as Router, Route, Routes, useLocation } from "react-router-dom";
import { HeroSection } from "./components/Home/Hero";
import Home from "./components/Home/Home";
import { StartBuildingSection } from "./components/Home/StartBuilding";
import Footer from "./components/Navigation/Footer";
import { Navbar } from "./components/Navigation/Navbar";
import { Layout } from "./components/Dashboard/Layout";
import StatsDashboard from "./components/Statistics/StatsDashboard";
import LoginPage from './pages/LoginPage';
import AuthCallbackPage from './pages/AuthCallbackPage';

// Wrapper component to conditionally render Navbar and Footer
const AppLayout = () => {
  const location = useLocation();
  const isDashboardRoute = location.pathname.startsWith('/dashboard');

  return (
    <>
      {!isDashboardRoute && <Navbar />}
      <Routes>
        <Route path="/" element={
          <>
            <HeroSection />
            <StartBuildingSection />
            <Home />
          </>
        } />
        <Route path="/dashboard/*" element={<Layout/>} />
        <Route path="/product" element={<div>Product Page</div>} />
        <Route path="/developers" element={<div>Developers Page</div>} />
        <Route path="/pricing" element={<div>Pricing Page</div>} />
        <Route path="/enterprise" element={<div>Enterprise Page</div>} />
        <Route path="/blog" element={<div>Blog Page</div>} />
        <Route path="/stats" element={<StatsDashboard />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
      </Routes>
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
