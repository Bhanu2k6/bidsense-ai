import React, { useState } from "react";
import "./App.css";

import Header from "./components/Header";
import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";
import ResultsTable from "./components/ResultsTable";
import WinnerBox from "./components/WinnerBox";

function App() {

  const [tender, setTender] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [matches, setMatches] = useState([]);
  const [winner, setWinner] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =====================================================
  // Analyze Bid Documents
  // =====================================================
  const analyzeBids = async () => {

    // Validation
    if (!tender || vendors.length === 0) {
      alert("Please select tender and vendor PDFs");
      return;
    }

    setLoading(true);
    setError("");

    try {

      const formData = new FormData();

      formData.append("tender", tender);

      vendors.forEach((v) => {
        formData.append("vendors", v);
      });

      const res = await fetch(
        "https://bidsense-ai-backend-9jfg.onrender.com/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!res.ok) {
        throw new Error("Backend Error");
      }

      const data = await res.json();

      setMatches(data.matches || []);
      setWinner(data.winner || null);

    } catch (err) {

      setError("Failed to fetch results from backend");

    }

    setLoading(false);
  };

  return (

    <div className="app">

      {/* Header */}
      <Header />

      {/* Hero */}
      <Hero />

      {/* Dashboard */}
      <section className="dashboard">

        <h3>Tender Evaluation Dashboard</h3>

        {/* Upload Section */}
        <UploadSection
          setTender={setTender}
          setVendors={setVendors}
          analyzeBids={analyzeBids}
          loading={loading}
        />

        {/* Error Message */}
        {error && (
          <p className="error">
            {error}
          </p>
        )}

        {/* Summary Cards */}
        {matches.length > 0 && (

          <div className="summary-grid">

            <div className="summary-card">
              <h4>📄 Total Vendors</h4>
              <p>{matches.length}</p>
            </div>

            <div className="summary-card">
              <h4>🏆 Top Score</h4>
              <p>{winner?.total_score}</p>
            </div>

            <div className="summary-card">
              <h4>🤖 Winner</h4>
              <p>{winner?.vendor_name}</p>
            </div>

          </div>

        )}

        {/* Results Table */}
        {matches.length > 0 && (

          <>

            <ResultsTable
              matches={matches}
              winner={winner}
            />

            {/* Winner Box */}
            {winner && (
              <WinnerBox winner={winner} />
            )}

          </>

        )}

      </section>

    </div>
  );
}

export default App;