import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Navbar
import NavBar from "./components/NavBar";

// Existing pages
import VehiclesPage from "./pages/VehiclesPage";
import VehicleDetailPage from "./pages/VehicleDetailPage";

// New pages
import HomePage from "./pages/HomePage";
import UsedVehiclesPage from "./pages/UsedVehiclesPage";
import NewVehiclesPage from "./pages/NewVehiclesPage";
import PreApprovalPage from "./pages/PreApprovalPage";
import ContactPage from "./pages/ContactPage";
import TestDrivePage from "./pages/TestDrivePage";

function App() {
  return (
    <BrowserRouter>
      <NavBar />

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "1rem" }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          
          {/* Inventory */}
          <Route path="/vehicles" element={<VehiclesPage />} />
          <Route path="/vehicle/:stock_id" element={<VehicleDetailPage />} />

          {/* Top nav tabs - using VehiclesPage with initialFilters */}
          <Route 
            path="/used" 
            element={<VehiclesPage initialFilters={{ condition: "Used" }} />} 
          />
          <Route path="/new" element={<NewVehiclesPage />} />
          <Route path="/preapproved" element={<PreApprovalPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/test-drive" element={<TestDrivePage />} />

          {/* Fallback */}
          <Route path="*" element={<HomePage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
