"use client";

import { useState } from "react";

export default function TestConnection() {
  const [results, setResults] = useState<string[]>([]);

  const addResult = (msg: string) => {
    setResults(prev => [...prev, msg]);
  };

  const testBackendFromBrowser = async () => {
    addResult("Testing backend from browser...");
    try {
      const response = await fetch("http://localhost:8000/", {
        method: "GET",
      });
      const data = await response.json();
      addResult(`✅ SUCCESS: ${JSON.stringify(data)}`);
    } catch (error: any) {
      addResult(`❌ FAILED: ${error.message}`);
      addResult(`Error type: ${error.name}`);
    }
  };

  const testBackendFromServer = async () => {
    addResult("Testing backend from Next.js server...");
    try {
      const response = await fetch("/api/test-backend");
      const data = await response.json();
      addResult(`✅ Result: ${JSON.stringify(data, null, 2)}`);
    } catch (error: any) {
      addResult(`❌ FAILED: ${error.message}`);
    }
  };

  const testCORS = async () => {
    addResult("Testing CORS preflight...");
    try {
      const response = await fetch("http://localhost:8000/", {
        method: "OPTIONS",
        headers: {
          "Origin": "http://localhost:3000",
          "Access-Control-Request-Method": "GET",
        },
      });
      addResult(`✅ CORS preflight status: ${response.status}`);
      const corsHeader = response.headers.get("access-control-allow-origin");
      addResult(`CORS header: ${corsHeader}`);
    } catch (error: any) {
      addResult(`❌ CORS test failed: ${error.message}`);
    }
  };

  const runAllTests = async () => {
    setResults([]);
    await testBackendFromBrowser();
    await testBackendFromServer();
    await testCORS();
  };

  return (
    <div style={{ padding: "20px", fontFamily: "monospace" }}>
      <h1>Backend Connection Test</h1>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={runAllTests} style={{ padding: "10px 20px", marginRight: "10px" }}>
          Run All Tests
        </button>
        <button onClick={testBackendFromBrowser} style={{ padding: "10px 20px", marginRight: "10px" }}>
          Test Browser → Backend
        </button>
        <button onClick={testBackendFromServer} style={{ padding: "10px 20px", marginRight: "10px" }}>
          Test Server → Backend
        </button>
        <button onClick={testCORS} style={{ padding: "10px 20px" }}>
          Test CORS
        </button>
      </div>

      <div style={{
        background: "#000",
        color: "#0f0",
        padding: "20px",
        borderRadius: "5px",
        minHeight: "300px",
        fontFamily: "monospace",
        fontSize: "14px",
        whiteSpace: "pre-wrap"
      }}>
        {results.length === 0 ? "Click a button to run tests..." : results.join("\n")}
      </div>

      <div style={{ marginTop: "20px", padding: "20px", background: "#f0f0f0", borderRadius: "5px" }}>
        <h2>Configuration</h2>
        <p><strong>Backend URL:</strong> {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</p>
        <p><strong>Frontend URL:</strong> {process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}</p>
        <p><strong>Current URL:</strong> {typeof window !== 'undefined' ? window.location.href : 'N/A'}</p>
      </div>

      <div style={{ marginTop: "20px", padding: "20px", background: "#fff3cd", borderRadius: "5px" }}>
        <h2>What to Look For</h2>
        <ul>
          <li><strong>Browser → Backend:</strong> Should return {`{"message":"TaskFlow API","status":"running"}`}</li>
          <li><strong>Server → Backend:</strong> Should show success and backend response</li>
          <li><strong>CORS:</strong> Should show status 200 and allow-origin: *</li>
        </ul>
        <p><strong>If any test fails:</strong> Copy the entire output and share it</p>
      </div>
    </div>
  );
}
