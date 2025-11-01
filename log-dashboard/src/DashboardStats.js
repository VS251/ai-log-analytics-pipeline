import React, { useMemo } from 'react';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

// Colors for our pie chart
const SENTIMENT_COLORS = {
  POSITIVE: '#9eff9e', // Green
  NEGATIVE: '#ff8e8e', // Red
  UNKNOWN: '#8884d8'  // Purple
};

export default function DashboardStats({ logs }) {

  // This 'useMemo' hook will re-process the data ONLY when the logs prop changes.
  // This is much more efficient than recalculating on every render.

  // 1. Process data for the Sentiment Pie Chart
  const sentimentData = useMemo(() => {
    const counts = logs.reduce((acc, log) => {
      const sentiment = log.ai_sentiment || 'UNKNOWN';
      acc[sentiment] = (acc[sentiment] || 0) + 1;
      return acc;
    }, {});
    
    // Format for Recharts: [{ name: 'POSITIVE', value: 12 }, { name: 'NEGATIVE', value: 3 }]
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [logs]);

  // 2. Process data for the Service Bar Chart
  const serviceData = useMemo(() => {
    const counts = logs.reduce((acc, log) => {
      const service = log.service || 'UNKNOWN';
      acc[service] = (acc[service] || 0) + 1;
      return acc;
    }, {});

    // Format for Recharts: [{ name: 'login-service', count: 10 }, { name: 'payment-api', count: 5 }]
    return Object.entries(counts).map(([name, count]) => ({ name, count }))
           .sort((a, b) => b.count - a.count); // Sort descending
  }, [logs]);


  return (
    <div className="stats-container">
      
      {/* --- Pie Chart (Sentiment) --- */}
      <div className="chart-wrapper">
        <h3>Log Sentiment</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={sentimentData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              label={(entry) => `${entry.name} (${entry.value})`}
            >
              {sentimentData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[entry.name]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* --- Bar Chart (Services) --- */}
      <div className="chart-wrapper">
        <h3>Logs by Service</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={serviceData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#555" />
            <XAxis type="number" stroke="#ccc" />
            <YAxis dataKey="name" type="category" stroke="#ccc" width={120} />
            <Tooltip 
              cursor={{fill: '#4a4f5a'}}
              contentStyle={{backgroundColor: '#282c34', border: '1px solid #555'}}
            />
            <Bar dataKey="count" fill="#8ebfff" />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}