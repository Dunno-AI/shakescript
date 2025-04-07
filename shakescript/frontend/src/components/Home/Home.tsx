import React from 'react';
import FeatureGrid from './FeatureGrid';

const Home: React.FC = () => {
  return (
    <main className="min-h-screen bg-black text-white">
      <div className="container mx-auto py-8">
        <FeatureGrid />
      </div>
    </main>
  );
};

export default Home;