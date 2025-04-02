import "./index.css"
import { BackgroundLines } from "./components/AceternityUI/background-lines"
import StoryViewer from "./StoryView"

function App() {
  return (
    <div className="flex justify-center items-center h-screen bg-gray-50">
      <StoryViewer />
    </div>
  );
}

export default App;
