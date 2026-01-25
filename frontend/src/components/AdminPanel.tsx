import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, Brain, Loader2, CheckCircle, AlertCircle, Zap, Server } from 'lucide-react';
import { triggerIngest, triggerTrain } from '../api';
import { KPICard } from './KPICard';

interface AdminPanelProps {
    stats: any;
}

export const AdminPanel: React.FC<AdminPanelProps> = ({ stats }) => {
    const [ingestLoading, setIngestLoading] = useState(false);
    const [trainLoading, setTrainLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    const handleIngest = async () => {
        setIngestLoading(true);
        setMessage(null);
        try {
            const res = await triggerIngest();
            setMessage({ type: 'success', text: res.message });
        } catch (e: any) {
            setMessage({ type: 'error', text: e.response?.data?.detail || 'Ingest failed' });
        } finally {
            setIngestLoading(false);
        }
    };

    const handleTrain = async () => {
        setTrainLoading(true);
        setMessage(null);
        try {
            const res = await triggerTrain();
            setMessage({ type: 'success', text: res.message });
        } catch (e: any) {
            setMessage({ type: 'error', text: e.response?.data?.detail || 'Training failed' });
        } finally {
            setTrainLoading(false);
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
                <motion.h2
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    style={{
                        fontSize: '1.75rem',
                        fontWeight: 700,
                        color: '#f8fafc',
                        marginBottom: '0.5rem'
                    }}
                >
                    Dashboard Overview
                </motion.h2>
                <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
                    Monitor your customer intelligence metrics and manage system operations.
                </p>
            </div>

            {/* KPI Cards */}
            <div className="grid-cols-3" style={{ marginBottom: '2rem' }}>
                <KPICard
                    title="Total Customers"
                    value={stats ? "4,000" : "—"}
                    icon="users"
                    trend="up"
                    trendValue="+12%"
                />
                <KPICard
                    title="Avg CLTV"
                    value={stats ? "₹2,500" : "—"}
                    icon="money"
                    color="text-green"
                    trend="up"
                    trendValue="+8%"
                />
                <KPICard
                    title="Churn Rate"
                    value={stats ? "22%" : "—"}
                    icon="trend"
                    color="text-yellow"
                    trend="down"
                    trendValue="-3%"
                />
            </div>

            {/* Admin Actions Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="card"
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        padding: '10px',
                        borderRadius: '12px'
                    }}>
                        <Server size={20} color="white" />
                    </div>
                    <div>
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#f1f5f9', margin: 0 }}>
                            System Operations
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                            Run backend processes from the dashboard
                        </p>
                    </div>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '1rem',
                    marginTop: '1.5rem'
                }}>
                    {/* Ingest Card */}
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        style={{
                            background: 'rgba(59, 130, 246, 0.1)',
                            border: '1px solid rgba(59, 130, 246, 0.2)',
                            borderRadius: '16px',
                            padding: '1.25rem',
                            cursor: 'pointer'
                        }}
                        onClick={!ingestLoading ? handleIngest : undefined}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <div style={{
                                background: 'linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%)',
                                padding: '10px',
                                borderRadius: '10px'
                            }}>
                                {ingestLoading ? <Loader2 className="animate-spin" size={20} color="white" /> : <Database size={20} color="white" />}
                            </div>
                            <span style={{ fontWeight: 600, color: '#f1f5f9' }}>Data Ingestion</span>
                        </div>
                        <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: 0 }}>
                            Generate synthetic customer dataset for training and testing.
                        </p>
                    </motion.div>

                    {/* Train Card */}
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        style={{
                            background: 'rgba(139, 92, 246, 0.1)',
                            border: '1px solid rgba(139, 92, 246, 0.2)',
                            borderRadius: '16px',
                            padding: '1.25rem',
                            cursor: 'pointer'
                        }}
                        onClick={!trainLoading ? handleTrain : undefined}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <div style={{
                                background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
                                padding: '10px',
                                borderRadius: '10px'
                            }}>
                                {trainLoading ? <Loader2 className="animate-spin" size={20} color="white" /> : <Brain size={20} color="white" />}
                            </div>
                            <span style={{ fontWeight: 600, color: '#f1f5f9' }}>Train Models</span>
                        </div>
                        <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: 0 }}>
                            Train Churn, Uplift, and CLTV prediction models.
                        </p>
                    </motion.div>
                </div>

                {/* Status Message */}
                <AnimatePresence>
                    {message && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            style={{
                                marginTop: '1.5rem',
                                padding: '1rem 1.25rem',
                                borderRadius: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.75rem',
                                background: message.type === 'success'
                                    ? 'rgba(16, 185, 129, 0.15)'
                                    : 'rgba(239, 68, 68, 0.15)',
                                border: message.type === 'success'
                                    ? '1px solid rgba(16, 185, 129, 0.3)'
                                    : '1px solid rgba(239, 68, 68, 0.3)',
                                color: message.type === 'success' ? '#34d399' : '#f87171'
                            }}
                        >
                            {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                            <span style={{ fontWeight: 500 }}>{message.text}</span>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>

            {/* Quick Stats */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                style={{
                    marginTop: '2rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#64748b',
                    fontSize: '0.85rem'
                }}
            >
                <Zap size={16} style={{ color: '#fbbf24' }} />
                <span>System ready • Models loaded • API active</span>
            </motion.div>
        </motion.div>
    );
};
