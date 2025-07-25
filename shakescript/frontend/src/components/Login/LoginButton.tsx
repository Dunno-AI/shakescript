import { supabase } from '../../lib/supabaseClient';

export const LoginButton = () => {
  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      // options: {
      //   redirectTo: `${window.location.origin}/auth/callback`,
      // },
    });

    if (error) console.error('Login error:', error.message);
  };

  return (
    <button
      onClick={handleLogin}
      className="bg-emerald-600 text-white px-6 py-3 rounded-lg font-semibold text-lg hover:bg-emerald-700 transition-colors"
    >
      Login with Google
    </button>
  );
}; 
