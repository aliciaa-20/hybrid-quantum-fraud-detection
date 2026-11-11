import { NavLink, Route, Routes } from "react-router-dom";
import { APP_NAME } from "./config";
import About from "./pages/About";
import Explore from "./pages/Explore";
import Findings from "./pages/Findings";
import Landing from "./pages/Landing";
import Upload from "./pages/Upload";

export default function App() {
  return (
    <>
      <header className="site-header">
        <NavLink to="/" className="brand">{APP_NAME}</NavLink>
        <nav aria-label="Main">
          <NavLink to="/explore">Explore</NavLink>
          <NavLink to="/upload">Upload</NavLink>
          <NavLink to="/findings">Findings</NavLink>
          <NavLink to="/about">About</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/findings" element={<Findings />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
      <footer className="site-footer">
        Experimental research demo. Quantum models run on a simulator. Nothing you upload is stored.
      </footer>
    </>
  );
}
