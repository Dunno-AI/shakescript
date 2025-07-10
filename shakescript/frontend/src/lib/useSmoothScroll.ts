import { useCallback } from "react";

/**
 * Returns a function to smoothly scroll to an element by id, or to the top if no id is provided.
 * Optionally updates the URL hash.
 */
export function useSmoothScroll() {
  return useCallback((id?: string) => {
    if (id) {
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
        window.history.replaceState(null, "", `/#${id}`);
        return;
      }
    }
    // Scroll to top if no id or element not found
    window.scrollTo({ top: 0, behavior: "smooth" });
    window.history.replaceState(null, "", "/");
  }, []);
} 