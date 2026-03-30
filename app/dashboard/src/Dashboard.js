import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { API_BASE_URL } from '../config';

function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [agents, setAgents] = useState([]);

  // Fetch system status on mount
  useEffect(() => {
    fetchSystemStatus();
    fetchAgents();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setSystemStatus(data);
    } catch (err) {
      console.error('Error fetching system status:', err.message);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (err) {
      console.error('Error fetching agents:', err.message);
    }
  };

  const runFullPipeline = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/run-full`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          leads: [
            {
              name: "Test Lead 1",
              company: "Acme Corp",
              industry: "Technology",
              budget: 50000,
              location: "Dubai"
            },
            {
              name: "Test Lead 2", 
              company: "Global Inc",
              industry: "Finance",
              budget: 100000,
              location: "London"
            }
          ]
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>AI Engine Dashboard</h1>
        <p>Connect backend AI system with live execution</p>
      </header>

      <div className="controls">
        <button 
          className="execute-btn"
          onClick={runFullPipeline}
          disabled={loading}
        >
          {loading ? 'RUNNING...' : 'EXECUTE NOW'}
        </button>
      </div>

      {/* System Status Panel */}
      {systemStatus && (
        <div className="panel">
          <h3>Backend Connection</h3>
          <p>Status: {systemStatus.status === 'healthy' ? '✅ Connected' : '❌ Disconnected'}</p>
          <p>API URL: {API_BASE_URL}</p>
        </div>
      )}

      {/* Agents Panel */}
      {agents.length > 0 && (
        <div className="panel">
          <h3>Available Agents ({agents.length})</h3>
          <ul>
            {agents.map((agent, idx) => (
              <li key={idx}>{agent.name || agent}</li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div className="error-panel">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="results">
          <div className="panel">
            <h3>System Status</h3>
            <p>Session ID: {result.session_id?.substring(0, 8)}...</p>
            <p>Mode: {result.mode}</p>
            <p>Steps Completed: {result.steps_completed?.join(', ')}</p>
          </div>

          {result.summary && (
            <div className="panel">
              <h3>Lead Summary</h3>
              <p>Total Leads: {result.summary.total_leads}</p>
              <p>RED: {result.summary.red} | ORANGE: {result.summary.orange} | YELLOW: {result.summary.yellow} | BLACK: {result.summary.black}</p>
              <p>Average Score: {result.summary.average_score}</p>
              <p>Predictions Generated: {result.summary.predictions_generated}</p>
            </div>
          )}

          {result.predictions && result.predictions.length > 0 && (
            <div className="panel">
              <h3>Predictions</h3>
              {result.predictions.map((pred, idx) => (
                <div key={idx} className="prediction-item">
                  <p>Lead {idx + 1}:</p>
                  <p>Growth: {pred.growth_prediction}</p>
                  <p>Revenue: {pred.revenue_range}</p>
                  <p>Confidence: {pred.confidence_score}/100</p>
                </div>
              ))}
            </div>
          )}

          {result.positioning && result.positioning.length > 0 && (
            <div className="panel">
              <h3>Positioning Strategies</h3>
              {result.positioning.map((pos, idx) => (
                <div key={idx} className="position-item">
                  <p>Angle {idx + 1}: {pos.angle}</p>
                  <p>Urgency: {pos.urgency}</p>
                </div>
              ))}
            </div>
          )}

          {result.errors && (
            <div className="error-panel">
              <h3>Errors</h3>
              <pre>{JSON.stringify(result.errors, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
