import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Navbar
import NavBar from "./components/NavBar";

// Existing pages
import VehiclesPage from "./pages/VehiclesPage";
import VehicleDetailPage from "./pages/VehicleDetailPage";

// Pages
import HomePage from "./pages/HomePage";
import PreApprovalPage from "./pages/PreApprovalPage";
import ContactPage from "./pages/ContactPage";
import TestDrivePage from "./pages/TestDrivePage";
import ThankYouPage from "./pages/ThankYouPage";

// Admin pages
import AdminLayout from "./pages/admin/AdminLayout";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Admin routes - no navbar */}
        <Route path="/admin/*" element={<AdminLayout />} />
        
        {/* Public routes with navbar */}
        <Route
          path="*"
          element={
            <>
              <NavBar />
              <main style={{ maxWidth: 1200, margin: "0 auto", padding: "1rem" }}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  
                  {/* Inventory */}
                  <Route path="/vehicles" element={<VehiclesPage />} />
                  <Route path="/vehicle/:stock_id" element={<VehicleDetailPage />} />

                  {/* Used vehicles */}
                  <Route 
                    path="/used" 
                    element={<VehiclesPage initialFilters={{ condition: "Used" }} />} 
                  />
                  
                  {/* New vehicles */}
                  <Route 
                    path="/new" 
                    element={<VehiclesPage initialFilters={{ condition: "New" }} />} 
                  />
                  
                  {/* Forms */}
                  <Route path="/preapproved" element={<PreApprovalPage />} />
                  <Route path="/contact" element={<ContactPage />} />
                  <Route path="/test-drive" element={<TestDrivePage />} />
                  
                  {/* Thank you pages */}
                  <Route path="/thank-you" element={<ThankYouPage />} />
                  <Route path="/preapproved/thanks" element={<ThankYouPage />} />

                  {/* Fallback */}
                  <Route path="*" element={<HomePage />} />
                </Routes>
              </main>
            </>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
