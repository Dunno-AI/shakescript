const ConfirmModal = ({ open, onConfirm, onCancel, message }: { open: boolean; onConfirm: () => void; onCancel: () => void; message: string }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70">
      <div className="backdrop-blur-lg bg-zinc-950/95 p-10 rounded-2xl shadow-2xl border border-zinc-800 w-full max-w-lg mx-4">
        <div className="mb-6 text-zinc-100 text-xl text-center font-semibold">{message}</div>
        <div className="flex justify-center gap-8 mt-4">
          <button onClick={onCancel} className="px-6 py-3 rounded-lg bg-zinc-700 text-zinc-200 hover:bg-zinc-600">Cancel</button>
          <button onClick={onConfirm} className="px-6 py-3 rounded-lg bg-red-600 text-white hover:bg-red-700">Delete</button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
