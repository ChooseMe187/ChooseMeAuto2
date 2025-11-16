import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import VehiclesPage from "./pages/VehiclesPage";
import VehicleDetailPage from "./pages/VehicleDetailPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/vehicles" replace />} />
          <Route path="/vehicles" element={<VehiclesPage />} />
          <Route path="/vehicle/:stock_id" element={<VehicleDetailPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
