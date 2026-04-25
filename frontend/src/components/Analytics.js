import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  TrendingUp, Brain, AlertTriangle, Users,
  Sparkles, ChevronDown, ChevronUp
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar
} from 'recharts';

const Analytics = () => {
  const { isInfluencer } = useAuth();
  const [predictions, setPredictions] = useState(null);
  const [insights, setInsights] = useState(null);
  const [fraudAlerts, setFraudAlerts] = useState(null);
  const [topInfluencers, setTopInfluencers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedSection, setExpandedSection] = useState('predictions');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      // Fetch predictions
      const predRes = await api.get('/analytics/predictions/');
      setPredictions(predRes.data);

      // Fetch insights
      const insightRes = await api.get('/analytics/insights/');
      setInsights(insightRes.data);

      // Fetch fraud detection (admin only)
      if (!isInfluencer()) {
        const fraudRes = await api.get('/analytics/fraud-detection/');
        setFraudAlerts(fraudRes.data);

        const topRes = await api.get('/analytics/top-influencers/');
        setTopInfluencers(topRes.data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const Section = ({ title, icon: Icon, id, children }) => (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <button
        onClick={() => setExpandedSection(expandedSection === id ? null : id)}
        className="w-full px-6 py-4 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50"
      >
        <div className="flex items-center">
          <div className="bg-blue-100 p-2 rounded-lg mr-3">
            <Icon className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        {expandedSection === id ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>
      {expandedSection === id && (
        <div className="p-6">
          {children}
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI-Powered Analytics</h1>
        <p className="text-gray-500">Advanced insights and predictions</p>
      </div>

      {/* AI Badge */}
      <div className="flex items-center bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4">
        <Sparkles className="w-6 h-6 text-purple-600 mr-3" />
        <div>
          <p className="font-medium text-purple-900">AI Features Active</p>
          <p className="text-sm text-purple-700">
            Sales predictions and influencer insights powered by machine learning
          </p>
        </div>
      </div>

      {/* Sales Predictions */}
      <Section title="Sales Predictions (Next 30 Days)" icon={TrendingUp} id="predictions">
        {predictions && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-600">Predicted Revenue</p>
                <p className="text-2xl font-bold text-blue-900">
                  ${predictions.total_predicted_revenue?.toLocaleString()}
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-green-600">Predicted Sales</p>
                <p className="text-2xl font-bold text-green-900">
                  {predictions.total_predicted_sales}
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-sm text-purple-600">Confidence</p>
                <p className="text-2xl font-bold text-purple-900">
                  {predictions.confidence}%
                </p>
              </div>
            </div>

            {predictions.ai_insight && (
              <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200 rounded-lg p-4">
                <div className="flex items-start">
                  <Brain className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                  <div>
                    <p className="font-medium text-indigo-900">AI Insight</p>
                    <p className="text-sm text-indigo-700">{predictions.ai_insight}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Prediction Chart */}
            {predictions.predictions?.length > 0 && (
              <div className="h-64 mt-6">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={predictions.predictions}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="date" tickFormatter={(d) => new Date(d).getDate()} stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip labelFormatter={(l) => `Date: ${l}`} />
                    <Line type="monotone" dataKey="predicted_revenue" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </Section>

      {/* Influencer Insights */}
      <Section title="Influencer Performance Insights" icon={Brain} id="insights">
        {insights && (
          <div className="space-y-4">
            {isInfluencer() ? (
              // Single influencer view
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Performance Score</p>
                  <p className="text-2xl font-bold text-gray-900">{insights.insights?.performance_score}/100</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Conversion Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{insights.insights?.conversion_rate}%</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Best Day</p>
                  <p className="text-2xl font-bold text-gray-900">{insights.insights?.best_performing_day || 'N/A'}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Avg Order Value</p>
                  <p className="text-2xl font-bold text-gray-900">${insights.insights?.avg_order_value}</p>
                </div>
              </div>
            ) : (
              // Admin view - list of influencers
              <div className="space-y-3">
                {insights.insights?.map((insight, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{insight.influencer}</p>
                        <p className="text-sm text-gray-500">{insight.referral_code}</p>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Score</p>
                          <p className="font-bold text-blue-600">{insight.performance_score}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Conv. Rate</p>
                          <p className="font-bold text-green-600">{insight.conversion_rate}%</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Recommendations */}
            {insights.insights?.recommendations?.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
                <p className="font-medium text-yellow-900 mb-2">Recommendations</p>
                <ul className="space-y-2">
                  {insights.insights.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-yellow-800 flex items-start">
                      <span className="mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Section>

      {/* Fraud Detection - Admin Only */}
      {!isInfluencer() && (
        <Section title="Fraud Detection" icon={AlertTriangle} id="fraud">
          {fraudAlerts && (
            <div>
              {fraudAlerts.suspicious_count > 0 ? (
                <div className="space-y-3">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                      <p className="font-medium text-red-900">
                        {fraudAlerts.suspicious_count} suspicious activities detected
                      </p>
                    </div>
                  </div>
                  {fraudAlerts.activities.map((activity, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            activity.risk_level === 'high' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                          }`}>
                            {activity.risk_level.toUpperCase()} RISK
                          </span>
                          <p className="mt-2 text-sm text-gray-700">{activity.message}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Sparkles className="w-5 h-5 text-green-600 mr-2" />
                    <p className="font-medium text-green-900">No suspicious activity detected</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </Section>
      )}

      {/* Top Influencers Chart - Admin Only */}
      {!isInfluencer() && topInfluencers.length > 0 && (
        <Section title="Top Performers Leaderboard" icon={Users} id="leaderboard">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topInfluencers} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" stroke="#6b7280" />
                <YAxis dataKey="name" type="category" width={120} stroke="#6b7280" />
                <Tooltip />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Section>
      )}
    </div>
  );
};

export default Analytics;
