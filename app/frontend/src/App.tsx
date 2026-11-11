import { AnimatePresence, motion } from "motion/react";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";
import Backdrop from "./components/Backdrop";
import { APP_NAME } from "./config";
import About from "./pages/About";
import Explore from "./pages/Explore";
import Findings from "./pages/Findings";
import Landing from "./pages/Landing";
import Upload from "./pages/Upload";

export default function App() {
  const location = useLocation();
  return (
    <>
      <Backdrop />
      <header className="site-header">
        <NavLink to="/" className="brand">{APP_NAME}</NavLink>
        <nav aria-label="Main">
          <NavLink to="/explore">Explore</NavLink>
          <NavLink to="/upload">Upload</NavLink>
          <NavLink to="/findings">Findings</NavLink>
          <NavLink to="/about">About</NavLink>
        </nav>
      </header>
      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}
        >
          <Routes location={location}>
            <Route path="/" element={<Landing />} />
            <Route path="/explore" element={<Explore />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </motion.main>
      </AnimatePresence>
      <footer className="site-footer">
        Experimental research demo. Quantum models run on a simulator. Nothing you upload is stored.
      </footer>
    </>
  );
}
