import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { CreditCard, Download, CheckCircle, FileText, DollarSign, AlertCircle } from 'lucide-react';

const Payments = () => {
  const { isAdmin, isFinance, isInfluencer } = useAuth();
  const [payments, setPayments] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showBankModal, setShowBankModal] = useState(false);

  useEffect(() => {
    fetchPayments();
    if (!isInfluencer()) {
      fetchSummary();
    }
  }, []);

  const fetchPayments = async () => {
    try {
      const res = await api.get('/payments/');
      setPayments(res.data);
    } catch (error) {
      console.error('Error fetching payments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const res = await api.get('/payments/summary/');
      setSummary(res.data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const exportReport = async (format) => {
    try {
      const response = await api.get(`/payments/export/${format}/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Error exporting report');
    }
  };

  const handleBankSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
      await api.post('/payments/bank-account/', {
        account_holder: formData.get('account_holder'),
        account_number: formData.get('account_number'),
        bank_name: formData.get('bank_name'),
        ifsc_code: formData.get('ifsc_code'),
      });
      setShowBankModal(false);
      alert('Bank account saved successfully');
    } catch (error) {
      alert('Error saving bank account: ' + error.message);
    }
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
          <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
          <p className="text-gray-500">Manage commissions and payouts</p>
        </div>
        {(isAdmin() || isFinance()) && (
          <div className="flex space-x-2">
            <button
              onClick={() => exportReport('csv')}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </button>
            <button
              onClick={() => exportReport('pdf')}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              <FileText className="w-4 h-4 mr-2" />
              Export PDF
            </button>
          </div>
        )}
      </div>

      {/* Summary Cards */}
      {(isAdmin() || isFinance()) && summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-yellow-400">
            <p className="text-sm text-gray-500">Pending Payments</p>
            <p className="text-xl font-bold text-gray-900">{summary.pending_payments.count}</p>
            <p className="text-sm text-orange-600">${summary.pending_payments.amount.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-green-400">
            <p className="text-sm text-gray-500">Ready for Payout</p>
            <p className="text-xl font-bold text-gray-900">{summary.ready_for_payout.count}</p>
            <p className="text-sm text-green-600">${summary.ready_for_payout.amount.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-blue-400">
            <p className="text-sm text-gray-500">Total Paid to Date</p>
            <p className="text-xl font-bold text-gray-900">${summary.total_paid_to_date.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-purple-400">
            <p className="text-sm text-gray-500">Influencers with Pending</p>
            <p className="text-xl font-bold text-gray-900">{summary.influencers_with_pending}</p>
          </div>
        </div>
      )}

      {/* Bank Account Button for Influencers */}
      {isInfluencer() && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center">
          <CreditCard className="w-5 h-5 text-blue-600 mr-3" />
          <div className="flex-1">
            <p className="font-medium text-blue-800">Bank Account</p>
            <p className="text-sm text-blue-600">Add or update your bank details for payouts</p>
          </div>
          <button
            onClick={() => setShowBankModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Manage
          </button>
        </div>
      )}

      {/* Payments Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                {!isInfluencer() && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Influencer</th>}
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transaction ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {payments.map((payment) => (
                <tr key={payment.id} className="hover:bg-gray-50">
                  {!isInfluencer() && (
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{payment.influencer}</p>
                        <p className="text-sm text-gray-500">{payment.referral_code}</p>
                      </div>
                    </td>
                  )}
                  <td className="px-6 py-4 font-bold text-green-600">${payment.amount}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      payment.status === 'completed' ? 'bg-green-100 text-green-800' :
                      payment.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {payment.status === 'completed' && <CheckCircle className="w-3 h-3 inline mr-1" />}
                      {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm capitalize">{payment.payment_method}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(payment.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm font-mono">{payment.transaction_id || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bank Account Modal */}
      {showBankModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Bank Account Details</h2>
            <form onSubmit={handleBankSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Account Holder Name</label>
                <input name="account_holder" type="text" required className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bank Name</label>
                <input name="bank_name" type="text" required className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Account Number</label>
                <input name="account_number" type="text" required className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">IFSC Code</label>
                <input name="ifsc_code" type="text" required className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowBankModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Payments;
