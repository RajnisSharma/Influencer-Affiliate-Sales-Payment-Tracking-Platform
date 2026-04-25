import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ShoppingCart, Filter, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sales = () => {
  const { isAdmin, isInfluencer } = useAuth();
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchSales();
  }, [statusFilter]);

  const fetchSales = async () => {
    try {
      const params = statusFilter ? `?status=${statusFilter}` : '';
      const res = await api.get(`/sales/${params}`);
      setSales(res.data);
    } catch (error) {
      console.error('Error fetching sales:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (id, newStatus) => {
    try {
      await api.patch(`/sales/${id}/`, { status: newStatus });
      fetchSales();
    } catch (error) {
      alert('Error updating status: ' + error.message);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'paid': return <CheckCircle className="w-4 h-4 text-blue-600" />;
      case 'approved': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'rejected': return <XCircle className="w-4 h-4 text-red-600" />;
      default: return <Clock className="w-4 h-4 text-yellow-600" />;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'paid': return 'status-paid';
      case 'approved': return 'status-approved';
      case 'rejected': return 'status-rejected';
      default: return 'status-pending';
    }
  };

  const stats = {
    total: sales.length,
    revenue: sales.reduce((a, b) => a + parseFloat(b.amount || 0), 0),
    commissions: sales.reduce((a, b) => a + parseFloat(b.commission || 0), 0),
    pending: sales.filter(s => s.status === 'pending').length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sales</h1>
          <p className="text-gray-500">Track all influencer-driven sales</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <p className="text-sm text-gray-500">Total Sales</p>
          <p className="text-xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <p className="text-sm text-gray-500">Revenue</p>
          <p className="text-xl font-bold text-green-600">${stats.revenue.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <p className="text-sm text-gray-500">Commissions</p>
          <p className="text-xl font-bold text-blue-600">${stats.commissions.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <p className="text-sm text-gray-500">Pending</p>
          <p className="text-xl font-bold text-orange-600">{stats.pending}</p>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center space-x-4">
        <Filter className="w-5 h-5 text-gray-400" />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="paid">Paid</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {/* Sales Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                {!isInfluencer() && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Influencer</th>}
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Commission</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                {isAdmin() && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sales.map((sale) => (
                <tr key={sale.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <ShoppingCart className="w-4 h-4 text-gray-400 mr-2" />
                      <span className="font-mono text-sm">{sale.order_id}</span>
                    </div>
                  </td>
                  {!isInfluencer() && (
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{sale.influencer_name}</p>
                        <p className="text-xs text-gray-500">{sale.referral_code}</p>
                      </div>
                    </td>
                  )}
                  <td className="px-6 py-4 font-medium">${sale.amount}</td>
                  <td className="px-6 py-4 text-green-600 font-medium">${sale.commission}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClass(sale.status)}`}>
                      {getStatusIcon(sale.status)}
                      <span className="ml-1 capitalize">{sale.status}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(sale.created_at).toLocaleDateString()}
                  </td>
                  {isAdmin() && (
                    <td className="px-6 py-4">
                      {sale.status === 'pending' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => updateStatus(sale.id, 'approved')}
                            className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-xs"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => updateStatus(sale.id, 'rejected')}
                            className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-xs"
                          >
                            Reject
                          </button>
                        </div>
                      )}
                      {sale.status === 'approved' && (
                        <button
                          onClick={() => updateStatus(sale.id, 'paid')}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-xs"
                        >
                          Mark Paid
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Sales;
