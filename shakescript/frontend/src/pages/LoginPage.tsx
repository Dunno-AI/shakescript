import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoginButton } from '../components/Login/LoginButton';

const LoginPage = () => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && user) {
      navigate('/dashboard');
    }
  }, [user, loading, navigate]);

  if (loading || user) {
    return <div>Loading...</div>; // Or a loading spinner
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#0A0A0A] text-white">
        <Link to="/" className="flex-shrink-0 mb-8">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21.3333 4L14.3333 11L21.3333 18H14.3333L7.33334 11L14.3333 4H21.3333Z" fill="#3ECF8E" />
                <path
                d="M7.33334 4L14.3333 11L7.33334 18H14.3333L21.3333 11L14.3333 4H7.33334Z"
                fill="#3ECF8E"
                fillOpacity="0.4"
                />
            </svg>
        </Link>
        <h1 className="text-4xl font-bold mb-4">Welcome to ShakeScript</h1>
        <p className="text-zinc-400 mb-8">Please login to continue</p>
        <LoginButton />
    </div>
  );
};

export default LoginPage;