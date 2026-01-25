import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { runCampaign } from '../api';
import { Target, Loader2, DollarSign, Users, TrendingUp, Sparkles, ChevronRight } from 'lucide-react';

export const CampaignBuilder: React.FC = () => {
    const [budget, setBudget] = useState(5000);
    const [cpa, setCpa] = useState(20);
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const run = async () => {
        setLoading(true);
        try {
            const res = await runCampaign(budget, cpa);
            setResult(res);
        } catch (e) {
            alert('Failed to run optimizer');
        } finally {
            setLoading(false);
        }
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
                    Campaign Optimizer
                </h2>
                <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
                    AI-powered customer targeting for maximum ROI on your marketing spend.
                </p>
            </div>

            {/* Config Card */}
            <motion.div
                className="card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
                        padding: '10px',
                        borderRadius: '12px'
                    }}>
                        <Target size={20} color="white" />
                    </div>
                    <div>
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#f1f5f9', margin: 0 }}>
                            Campaign Parameters
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                            Configure budget and cost settings
                        </p>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', alignItems: 'flex-end' }}>
                    <div>
                        <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.5rem', fontWeight: 500 }}>
                            Total Budget (₹)
                        </label>
                        <div style={{ position: 'relative' }}>
                            <DollarSign size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                            <input
                                type="number"
                                value={budget}
                                onChange={e => setBudget(Number(e.target.value))}
                                style={{ paddingLeft: '2.75rem' }}
                            />
                        </div>
                    </div>
                    <div>
                        <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.5rem', fontWeight: 500 }}>
                            Cost Per Action (₹)
                        </label>
                        <input
                            type="number"
                            value={cpa}
                            onChange={e => setCpa(Number(e.target.value))}
                        />
                    </div>
                    <button
                        onClick={run}
                        disabled={loading}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem',
                            background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)'
                        }}
                    >
                        {loading ? <Loader2 className="animate-spin" size={18} /> : <Sparkles size={18} />}
                        {loading ? 'Optimizing...' : 'Run Algorithm'}
                    </button>
                </div>
            </motion.div>

            {/* Results */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                        className="card"
                        style={{ marginTop: '1.5rem' }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                            <div style={{
                                background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                                padding: '10px',
                                borderRadius: '12px'
                            }}>
                                <TrendingUp size={20} color="white" />
                            </div>
                            <div>
                                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#f1f5f9', margin: 0 }}>
                                    Optimization Results
                                </h3>
                                <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                                    AI-selected targets for maximum impact
                                </p>
                            </div>
                        </div>

                        {/* Summary Stats */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div style={{
                                background: 'rgba(59, 130, 246, 0.1)',
                                border: '1px solid rgba(59, 130, 246, 0.2)',
                                borderRadius: '14px',
                                padding: '1.25rem',
                                textAlign: 'center'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                    <Users size={18} style={{ color: '#60a5fa' }} />
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Selected</span>
                                </div>
                                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#60a5fa' }}>
                                    {result.summary.selected_count}
                                </div>
                            </div>
                            <div style={{
                                background: 'rgba(251, 191, 36, 0.1)',
                                border: '1px solid rgba(251, 191, 36, 0.2)',
                                borderRadius: '14px',
                                padding: '1.25rem',
                                textAlign: 'center'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                    <DollarSign size={18} style={{ color: '#fbbf24' }} />
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Spend</span>
                                </div>
                                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fbbf24' }}>
                                    ₹{result.summary.spent.toFixed(0)}
                                </div>
                            </div>
                            <div style={{
                                background: 'rgba(16, 185, 129, 0.1)',
                                border: '1px solid rgba(16, 185, 129, 0.2)',
                                borderRadius: '14px',
                                padding: '1.25rem',
                                textAlign: 'center'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                    <TrendingUp size={18} style={{ color: '#34d399' }} />
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Avg ROI</span>
                                </div>
                                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#34d399' }}>
                                    {result.summary.avg_roi.toFixed(1)}x
                                </div>
                            </div>
                        </div>

                        {/* Table */}
                        <h4 style={{ color: '#e2e8f0', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <ChevronRight size={18} /> Top Targets Preview
                        </h4>
                        <div style={{ overflowX: 'auto', borderRadius: '12px', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                            <table>
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Uplift</th>
                                        <th>CLTV</th>
                                        <th>Expected Gain</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {result.selected_customers.slice(0, 8).map((c: any) => (
                                        <tr key={c.customer_id}>
                                            <td style={{ fontWeight: 600 }}>#{c.customer_id}</td>
                                            <td style={{ color: '#60a5fa' }}>{(c.uplift * 100).toFixed(2)}%</td>
                                            <td>{c.cltv.toFixed(2)}</td>
                                            <td style={{ color: '#34d399', fontWeight: 500 }}>+{c.expected_gain.toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};
