import React from 'react';

export const StoryQuality: React.FC = () => {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Story Quality Analysis</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-zinc-900 p-6 rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Quality Metrics</h2>
            <p className="text-zinc-400">
              Analyze the quality of your stories using various metrics and parameters.
            </p>
          </div>
          <div className="bg-zinc-900 p-6 rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Performance Insights</h2>
            <p className="text-zinc-400">
              Get detailed insights into how your stories are performing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}; 