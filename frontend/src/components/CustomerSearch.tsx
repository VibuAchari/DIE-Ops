import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { scoreCustomer } from '../api';
import { Search, Loader2, User, TrendingDown, TrendingUp, DollarSign, Zap } from 'lucide-react';

export const CustomerSearch: React.FC = () => {
    const [cid, setCid] = useState('');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSearch = async () => {
        if (!cid) return;
        setLoading(true);
        setError('');
        setData(null);
        try {
            const res = await scoreCustomer(parseInt(cid));
            setData(res);
        } catch (err) {
            setError('Customer not found');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleSearch();
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
        >
            {/* Header */}
            <div style={{ marginBottom: '2rem' }}>
                <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
                    Customer Explorer
                </h2>
                <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
                    Search and analyze individual customer profiles with AI-powered insights.
                </p>
            </div>

            {/* Search Card */}
            <motion.div
                className="card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                    <div style={{ flex: 1 }}>
                        <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.5rem', fontWeight: 500 }}>
                            Customer ID
                        </label>
                        <div style={{ position: 'relative' }}>
                            <User size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                            <input
                                placeholder="Enter ID (e.g., 42)"
                                value={cid}
                                onChange={e => setCid(e.target.value)}
                                onKeyPress={handleKeyPress}
                                type="number"
                                style={{ paddingLeft: '2.75rem' }}
                            />
                        </div>
                    </div>
                    <button
                        onClick={handleSearch}
                        disabled={loading || !cid}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            minWidth: '140px',
                            justifyContent: 'center'
                        }}
                    >
                        {loading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
                        {loading ? 'Searching...' : 'Analyze'}
                    </button>
                </div>

                {error && (
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        style={{ color: '#f87171', marginTop: '1rem', fontSize: '0.9rem' }}
                    >
                        {error}
                    </motion.p>
                )}
            </motion.div>

            {/* Results */}
            <AnimatePresence>
                {data && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.98 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.4 }}
                        className="card"
                        style={{ marginTop: '1.5rem' }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div style={{
                                width: '60px',
                                height: '60px',
                                borderRadius: '16px',
                                background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.5rem',
                                fontWeight: 700,
                                color: 'white'
                            }}>
                                #{data.customer_id}
                            </div>
                            <div>
                                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f1f5f9', margin: 0 }}>
                                    Customer Profile
                                </h3>
                                <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                                    AI-generated risk and value assessment
                                </p>
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                            {/* Churn */}
                            <div style={{
                                background: data.churn_prob > 0.5 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                                border: `1px solid ${data.churn_prob > 0.5 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)'}`,
                                borderRadius: '14px',
                                padding: '1.25rem'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                                    <TrendingDown size={18} style={{ color: data.churn_prob > 0.5 ? '#f87171' : '#34d399' }} />
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 500 }}>Churn Risk</span>
                                </div>
                                <div style={{
                                    fontSize: '1.75rem',
                                    fontWeight: 700,
                                    color: data.churn_prob > 0.5 ? '#f87171' : '#34d399'
                                }}>
                                    {(data.churn_prob * 100).toFixed(1)}%
                                </div>
                            </div>

                            {/* Uplift */}
                            <div style={{
                                background: 'rgba(59, 130, 246, 0.1)',
                                border: '1px solid rgba(59, 130, 246, 0.2)',
                                borderRadius: '14px',
                                padding: '1.25rem'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                                    <TrendingUp size={18} style={{ color: '#60a5fa' }} />
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 500 }}>Uplift Score</span>
                                </div>
                                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#60a5fa' }}>
                                    {(data.uplift * 100).toFixed(2)}%
                                </div>
                            </div>

                            {/* CLTV */}
                            <div style={{
                                background: 'rgba(251, 191, 36, 0.1)',
                                border: '1px solid rgba(251, 191, 36, 0.2)',
                                borderRadius: '14px',
                                padding: '1.25rem'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                                    <DollarSign size={18} style={{ color: '#fbbf24' }} />
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 500 }}>Predicted CLTV</span>
                                </div>
                                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fbbf24' }}>
                                    ₹{data.cltv.toFixed(2)}
                                </div>
                            </div>
                        </div>

                        {/* Recommendation */}
                        <div style={{
                            marginTop: '1.5rem',
                            padding: '1rem 1.25rem',
                            background: 'rgba(139, 92, 246, 0.1)',
                            border: '1px solid rgba(139, 92, 246, 0.2)',
                            borderRadius: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem'
                        }}>
                            <Zap size={20} style={{ color: '#a78bfa' }} />
                            <span style={{ color: '#e2e8f0', fontSize: '0.9rem' }}>
                                <strong style={{ color: '#a78bfa' }}>AI Recommendation:</strong> {' '}
                                {data.churn_prob > 0.5
                                    ? 'High churn risk - Consider retention campaign'
                                    : 'Low churn risk - Focus on upselling opportunities'}
                            </span>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};
