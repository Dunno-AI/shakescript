import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const AuthCallbackPage = () => {
  const navigate = useNavigate();
  const { session } = useAuth();

  useEffect(() => {
    if (session) {
      console.log("Logged in")
      toast.success('Successfully logged in!');
      navigate('/dashboard');
    }
  }, [session, navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#0A0A0A] text-white">
      <Loader2 className="w-12 h-12 animate-spin text-emerald-500 mb-4" />
      <p className="text-lg text-zinc-300">Please wait, authenticating...</p>
    </div>
  );
};

export default AuthCallbackPage;