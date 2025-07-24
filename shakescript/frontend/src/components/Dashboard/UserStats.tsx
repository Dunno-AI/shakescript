/**
 * UserStats component displays user profile and stats using dummy data.
 * Replace dummyUserDashboard with real API data and types as needed.
 */

/**
 * @typedef {Object} UserDashboard
 * @property {Object} user
 * @property {number} user.id
 * @property {string} user.auth_id
 * @property {string} user.email
 * @property {string} user.name
 * @property {boolean} user.is_premium
 * @property {string} user.avatar_url
 * @property {string} user.created_at
 * @property {Object} stats
 * @property {number} stats.total_stories
 * @property {number} stats.total_episodes
 * @property {number} stats.episodes_day_count
 * @property {number} stats.episodes_month_count
 * @property {number} stats.completed_stories
 * @property {number} stats.in_progress_stories
 * @property {number} stats.account_age_days
 * @property {string} stats.last_active
 * @property {Array} recent_stories
 * @property {boolean} premium_status
 */
import React, { useState, useEffect } from 'react';
import { Pencil } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function UserStats() {
  const { user } = useAuth();
  const [editMode, setEditMode] = useState(false);
  const [name, setName] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');

  useEffect(() => {
    if (user) {
      setName(user.user_metadata?.full_name || 'User');
      setAvatarUrl(user.user_metadata?.avatar_url || `https://i.pravatar.cc/100?u=${user.id}`);
    }
    // In a real app, you would fetch UserDashboard data from your backend here
  }, [user]);

  const handleSave = () => {
    setEditMode(false);
    // Here you would call the API to update user info
    // e.g., supabase.from('users').update({ name, avatar_url }).eq('id', user.id)
  };

  if (!user) {
    return <div>Loading...</div>;
  }
  
  // Dummy data for stats - replace with real data from your backend
  const dummyStats = {
    total_stories: 12,
    total_episodes: 87,
    episodes_day_count: 3,
    episodes_month_count: 20,
    in_progress_stories: 4,
  };

  return (
    <div className="w-full h-full min-h-screen bg-[#181818] p-8 text-white border border-zinc-800">
      <div className="flex items-center gap-4 mb-6">
        <img
          src={avatarUrl}
          alt="avatar"
          className="w-20 h-20 rounded-full border-2 border-emerald-500 object-cover"
        />
        <div className="flex-1">
          {editMode ? (
            <input
              className="bg-zinc-900 text-white rounded px-2 py-1 w-full mb-2 border border-zinc-700"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          ) : (
            <h2 className="text-2xl font-bold flex items-center gap-2">
              {name}
              <button onClick={() => setEditMode(true)} className="ml-2 text-zinc-400 hover:text-emerald-400">
                <Pencil size={18} />
              </button>
            </h2>
          )}
          <div className="text-zinc-400 text-sm mt-1">
            {/* is_premium would come from your backend user table */}
            <span className="bg-emerald-700 text-white px-2 py-0.5 rounded mr-2 text-xs">Premium</span>
            Joined Since: {new Date(user.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>
      {editMode && (
        <div className="mb-4">
          <label className="block text-zinc-300 text-sm mb-1">Avatar URL</label>
          <input
            className="bg-zinc-900 text-white rounded px-2 py-1 w-full border border-zinc-700"
            value={avatarUrl}
            onChange={e => setAvatarUrl(e.target.value)}
          />
          <button
            className="mt-2 px-4 py-1 bg-emerald-600 rounded text-white hover:bg-emerald-700"
            onClick={handleSave}
          >
            Save
          </button>
        </div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-6">
        <div className="bg-zinc-900 rounded-lg p-6 flex flex-col items-center border border-zinc-800">
          <span className="text-3xl font-bold text-emerald-400">{dummyStats.total_stories}</span>
          <span className="text-zinc-400 mt-1 text-sm">Stories Generated</span>
        </div>
        <div className="bg-zinc-900 rounded-lg p-6 flex flex-col items-center border border-zinc-800">
          <span className="text-3xl font-bold text-emerald-400">{dummyStats.total_episodes}</span>
          <span className="text-zinc-400 mt-1 text-sm">Total Episodes Generated</span>
        </div>
        <div className="bg-zinc-900 rounded-lg p-6 flex flex-col items-center border border-zinc-800">
          <span className="text-3xl font-bold text-emerald-400">{dummyStats.in_progress_stories}</span>
          <span className="text-zinc-400 mt-1 text-sm">Incomplete Stories</span>
        </div>
      </div>
      {/* Usage Table - moved below stats boxes, full width, consistent font */}
      <div className="bg-zinc-900 rounded-xl p-6 mt-8 shadow border border-zinc-800 w-full">
        <div className="text-lg text-zinc-300 mb-4">Usage <span className="text-zinc-400">[ Episodes ]</span></div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-base">
            <thead>
              <tr className="text-zinc-400 text-base">
                <th className="font-medium pb-2">USER</th>
                <th className="font-medium pb-2 text-center">TODAY</th>
                <th className="font-medium pb-2 text-center">THIS MONTH</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-zinc-700 text-base">
                <td className="py-3 text-zinc-300">You</td>
                <td className="py-3 text-center">
                  {dummyStats.episodes_day_count || 0} <span className="text-zinc-400">/ 5</span>
                </td>
                <td className="py-3 text-center">
                  {dummyStats.episodes_month_count || 0} <span className="text-zinc-400">/ 30</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 