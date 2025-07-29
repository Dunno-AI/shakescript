import { useState } from "react";
import { supabase } from "../../lib/supabaseClient";
import { InfoModal } from "../utils/InfoModal"; // Import the new modal
import { Heart } from "lucide-react";

export const LoginButton = () => {
  const [showModal, setShowModal] = useState(false);

  const handleLogin = async () => {
    if (window.innerWidth < 1024) {
      setShowModal(true); // Show the custom modal instead of an alert
      return;
    }

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) console.error("Login error:", error.message);
  };

  return (
    <>
      <button
        onClick={handleLogin}
        className="bg-emerald-600 text-white px-6 py-3 rounded-lg font-semibold text-lg hover:bg-emerald-700 transition-colors"
      >
        Login with Google
      </button>

      <InfoModal isOpen={showModal} onClose={() => setShowModal(false)}>
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center border-2 border-emerald-500/30">
            <Heart className="w-8 h-8 text-emerald-400" />
          </div>
          <h2 className="text-xl font-bold text-white">A little heads-up!</h2>
          <p className="text-zinc-400">
            For the best experience, please use a desktop or a larger screen!
            <br />
            <span className="text-2xl mt-2 block">🥹👉👈</span>
          </p>
          <button
            onClick={() => setShowModal(false)}
            className="mt-4 px-6 py-2 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
          >
            Okay, I understand
          </button>
        </div>
      </InfoModal>
    </>
  );
};
