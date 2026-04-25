import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  TrendingUp,
  Users,
  DollarSign,
  MousePointer,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';

const Dashboard = () => {
  const { user, isAdmin } = useAuth();
  const [stats, setStats] = useState(null);
  const [salesData, setSalesData] = useState([]);
  const [topInfluencers, setTopInfluencers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch stats
      const statsRes = await api.get('/dashboard/stats/');
      setStats(statsRes.data);

      // Fetch sales over time (mock data for last 7 days)
      const mockSalesData = [
        { date: 'Mon', sales: 1200, revenue: 3400 },
        { date: 'Tue', sales: 1900, revenue: 5200 },
        { date: 'Wed', sales: 1500, revenue: 4100 },
        { date: 'Thu', sales: 2200, revenue: 6800 },
        { date: 'Fri', sales: 2800, revenue: 8500 },
        { date: 'Sat', sales: 2400, revenue: 7200 },
        { date: 'Sun', sales: 1800, revenue: 5400 },
      ];
      setSalesData(mockSalesData);

      // Fetch top influencers if admin
      if (isAdmin()) {
        const topRes = await api.get('/analytics/top-influencers/');
        setTopInfluencers(topRes.data.slice(0, 5));
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, change, color }) => (
    <div className="bg-white rounded-xl p-6 shadow-sm card-hover">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {change && (
            <div className={`flex items-center mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ArrowDownRight className="w-4 h-4 mr-1" />}
              <span>{Math.abs(change)}% from last month</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );

  const pieData = [
    { name: 'Completed', value: 65, color: '#3b82f6' },
    { name: 'Pending', value: 25, color: '#f59e0b' },
    { name: 'Processing', value: 10, color: '#10b981' },
  ];

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
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Welcome back, {user?.email}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Sales"
          value={`$${stats?.total_sales?.toLocaleString() || '0'}`}
          icon={TrendingUp}
          change={12}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          title="Total Clicks"
          value={stats?.total_clicks?.toLocaleString() || '0'}
          icon={MousePointer}
          change={8}
          color="bg-purple-100 text-purple-600"
        />
        <StatCard
          title="Commissions Paid"
          value={`$${stats?.total_commissions?.toLocaleString() || '0'}`}
          icon={DollarSign}
          change={-5}
          color="bg-green-100 text-green-600"
        />
        <StatCard
          title="Conversion Rate"
          value={`${stats?.conversion_rate?.toFixed(1) || '0'}%`}
          icon={Users}
          change={3}
          color="bg-orange-100 text-orange-600"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sales Trend (Last 7 Days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Revenue Split Pie Chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Status Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center space-x-6 mt-4">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center">
                <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: item.color }} />
                <span className="text-sm text-gray-600">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Influencers Bar Chart */}
      {isAdmin() && topInfluencers.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Influencers by Revenue</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topInfluencers}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Pending Payments Alert */}
      {stats?.pending_payments > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-center">
          <div className="bg-yellow-100 p-2 rounded-lg mr-4">
            <DollarSign className="w-5 h-5 text-yellow-600" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-yellow-800">
              Pending Payments: ${stats.pending_payments.toLocaleString()}
            </p>
            <p className="text-sm text-yellow-600">
              There are pending commissions waiting for approval
            </p>
          </div>
          <button className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">
            Review
          </button>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
