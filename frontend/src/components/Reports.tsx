import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';
import { FileText, Download, Loader2, FolderOpen, ExternalLink } from 'lucide-react';

export const Reports: React.FC = () => {
    const [reports, setReports] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        setLoading(true);
        try {
            const res = await api.get('/reports');
            setReports(res.data);
        } catch (e) {
            console.error("Failed to fetch reports");
        } finally {
            setLoading(false);
        }
    };

    const openReport = (filename: string) => {
        window.open(`http://localhost:8000/reports/${filename}`, '_blank');
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
                    Generated Reports
                </h2>
                <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
                    View and download campaign strategy reports and analytics.
                </p>
            </div>

            {/* Reports Card */}
            <motion.div
                className="card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
                        padding: '10px',
                        borderRadius: '12px'
                    }}>
                        <FolderOpen size={20} color="white" />
                    </div>
                    <div>
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#f1f5f9', margin: 0 }}>
                            Report Library
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                            {reports.length} reports available
                        </p>
                    </div>
                </div>

                {loading && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#94a3b8', padding: '2rem 0' }}>
                        <Loader2 className="animate-spin" size={20} />
                        Loading reports...
                    </div>
                )}

                {!loading && reports.length === 0 && (
                    <div style={{
                        textAlign: 'center',
                        padding: '3rem 2rem',
                        background: 'rgba(148, 163, 184, 0.05)',
                        borderRadius: '12px',
                        border: '1px dashed rgba(148, 163, 184, 0.2)'
                    }}>
                        <FileText size={48} style={{ color: '#475569', marginBottom: '1rem' }} />
                        <p style={{ color: '#94a3b8', fontSize: '0.95rem', margin: 0 }}>
                            No reports generated yet.
                        </p>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                            Run a campaign optimization to generate your first report.
                        </p>
                    </div>
                )}

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {reports.map((file, index) => (
                        <motion.div
                            key={file}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={{ scale: 1.01 }}
                            style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                background: 'rgba(148, 163, 184, 0.05)',
                                border: '1px solid rgba(148, 163, 184, 0.1)',
                                padding: '1rem 1.25rem',
                                borderRadius: '12px',
                                cursor: 'pointer'
                            }}
                            onClick={() => openReport(file)}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <div style={{
                                    background: 'rgba(139, 92, 246, 0.2)',
                                    padding: '8px',
                                    borderRadius: '8px'
                                }}>
                                    <FileText size={18} style={{ color: '#a78bfa' }} />
                                </div>
                                <div>
                                    <span style={{ fontWeight: 500, color: '#e2e8f0' }}>{file}</span>
                                    <span style={{ display: 'block', fontSize: '0.75rem', color: '#64748b' }}>HTML Report</span>
                                </div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#60a5fa' }}>
                                <span style={{ fontSize: '0.85rem' }}>Open</span>
                                <ExternalLink size={16} />
                            </div>
                        </motion.div>
                    ))}
                </div>
            </motion.div>
        </motion.div>
    );
};
