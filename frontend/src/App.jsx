import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Upload, Play, TrendingUp, AlertCircle, FileText } from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [strategy, setStrategy] = useState(null);
  const [backtestData, setBacktestData] = useState(null);
  const [error, setError] = useState("");

  // 1. Handle File Upload (Phase 1)
  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_URL}/analyze-paper/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStrategy(res.data);
    } catch (err) {
      setError("Failed to analyze paper. Is the Backend running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 2. Handle Backtest (Phase 2)
  const runBacktest = async () => {
    if (!strategy) return;
    setLoading(true);
    
    try {
      // We assume the user wants to test on BTC-USD for now
      const res = await axios.get(`${API_URL}/run-backtest/`, {
        params: { 
          strategy_name: strategy.strategy_name,
          ticker: "BTC-USD"
        }
      });
      setBacktestData(res.data);
    } catch (err) {
      setError("Backtest failed. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-6xl mx-auto">
      {/* Header */}
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-blue-400 mb-2">Alpha-Mechanism</h1>
        <p className="text-slate-400">AI-Powered Quantitative Research Engine</p>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Panel: Upload & Strategy Info */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText size={20} /> Research Paper
          </h2>
          
          <div className="flex gap-4 mb-6">
            <input 
              type="file" 
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])}
              className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
            />
            <button 
              onClick={handleUpload}
              disabled={loading || !file}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition disabled:opacity-50"
            >
              {loading ? "Processing..." : "Analyze"}
            </button>
          </div>

          {error && (
            <div className="p-4 bg-red-900/30 text-red-300 rounded-lg mb-4 flex items-center gap-2">
              <AlertCircle size={18} /> {error}
            </div>
          )}

          {strategy && (
            <div className="space-y-4 animate-fade-in">
              <div className="p-4 bg-slate-900 rounded-lg border border-slate-700">
                <h3 className="text-lg font-bold text-green-400">{strategy.strategy_name}</h3>
                <p className="text-slate-400 text-sm mt-2">{strategy.description}</p>
                <div className="mt-3 text-xs text-slate-500 font-mono">
                  File generated at: {strategy.file_saved_at}
                </div>
              </div>
              
              <button 
                onClick={runBacktest}
                disabled={loading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold flex items-center justify-center gap-2 transition"
              >
                <Play size={20} /> Run Backtest (BTC-USD)
              </button>
            </div>
          )}
        </div>

        {/* Right Panel: Charts */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg min-h-[400px]">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <TrendingUp size={20} /> Performance
          </h2>

          {!backtestData ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500">
              <p>Run a backtest to see results.</p>
            </div>
          ) : (
            <div>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 bg-slate-900 rounded-lg">
                  <p className="text-sm text-slate-400">Total Return</p>
                  <p className="text-2xl font-bold text-green-400">{backtestData.total_return}</p>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg">
                  <p className="text-sm text-slate-400">Asset</p>
                  <p className="text-2xl font-bold text-blue-400">{backtestData.ticker}</p>
                </div>
              </div>

              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={backtestData.chart_data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tick={false} />
                    <YAxis stroke="#94a3b8" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', border: 'none' }}
                      itemStyle={{ color: '#e2e8f0' }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="strategy" stroke="#4ade80" strokeWidth={2} dot={false} name="AI Strategy" />
                    <Line type="monotone" dataKey="market" stroke="#60a5fa" strokeWidth={2} dot={false} name="Buy & Hold" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;