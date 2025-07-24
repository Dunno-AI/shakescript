import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { AuthProvider } from "./contexts/AuthContext";
import { StoryProvider } from "./contexts/StoryListContext";
import { BrowserRouter as Router } from "react-router-dom";

createRoot(document.getElementById("root")!).render(
  <Router>
    <AuthProvider>
      <StoryProvider>
        <App />
      </StoryProvider>
    </AuthProvider>
  </Router>
);
