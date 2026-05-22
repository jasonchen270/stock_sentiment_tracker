import { BrowserRouter, Routes, Route } from "react-router-dom";
import React from "react";
import Home from "./components/Home";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          className: "custom-toast",
          duration: 2000,
          style: {
            width: "400px",
            padding: "16px",
            fontSize: "18px",
          },
        }}
        containerStyle={{
          marginRight: "2rem",
          marginTop: "1rem",
        }}
      />
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
