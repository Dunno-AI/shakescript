import { Loader2 } from "lucide-react";

interface ConfirmModalProps {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  message: string;
  isDeleting: boolean; // Add a prop to track the deleting state
}

const ConfirmModal = ({
  open,
  onConfirm,
  onCancel,
  message,
  isDeleting,
}: ConfirmModalProps) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm">
      <div className="bg-zinc-900 p-8 rounded-2xl shadow-2xl border border-zinc-800 w-full max-w-md mx-4">
        <div className="mb-6 text-zinc-100 text-xl text-center font-semibold">
          {message}
        </div>
        <div className="flex justify-center gap-4 mt-4">
          <button
            onClick={onCancel}
            disabled={isDeleting} // Disable while deleting
            className="px-6 py-3 rounded-lg bg-zinc-700 text-zinc-200 hover:bg-zinc-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isDeleting} // Disable while deleting
            className="px-6 py-3 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[120px] transition-colors"
          >
            {isDeleting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              "Delete"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
