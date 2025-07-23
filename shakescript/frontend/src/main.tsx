import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { StoryProvider } from "./contexts/StoryListContext";

createRoot(document.getElementById("root")!).render(
  <>
    <StoryProvider>
      <App />
    </StoryProvider>
  </>,
);
