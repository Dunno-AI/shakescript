import { Loader2 } from 'lucide-react';

const FullScreenLoader = () => {
  return (
    <div className="fixed inset-0 flex h-screen w-full items-center justify-center bg-black">
      <Loader2 className="h-12 w-12 animate-spin text-emerald-500" />
    </div>
  );
};

export default FullScreenLoader;
