import { Suspense, lazy } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import Footer from "./components/Navigation/Footer";
import { Navbar } from "./components/Navigation/Navbar";
import LoginPage from "./pages/LoginPage";
import FullScreenLoader from "./components/utils/FullScreenLoader";
import { Toaster } from "react-hot-toast";

const HomePage = lazy(() => import("./pages/HomePage"));
const Layout = lazy(() => import("./components/Dashboard/Layout"));
const StatsDashboard = lazy(
  () => import("./components/Statistics/StatsDashboard"),
);

const AppLayout = () => {
  const location = useLocation();
  const isDashboardRoute = location.pathname.startsWith("/dashboard");

  return (
    <>
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 2000,
          style: {
            background: "#27272a",
            color: "#e4e4e7",
            border: "1px solid #3f3f46",
          },
        }}
      />

      {!isDashboardRoute && <Navbar />}

      <Suspense fallback={<FullScreenLoader />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard/*" element={<Layout />} />
          <Route path="/stats" element={<StatsDashboard />} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </Suspense>

      {!isDashboardRoute && <Footer />}
    </>
  );
};

function App() {
  return <AppLayout />;
}

export default App;
