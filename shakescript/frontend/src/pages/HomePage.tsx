import { HeroSection } from "../components/Home/Hero";
import Home from "../components/Home/Home";
import { StartBuildingSection } from "../components/Home/StartBuilding";

const HomePage = () => {
  return (
    <>
      <HeroSection />
      <StartBuildingSection />
      <Home />
    </>
  );
};

export default HomePage;
