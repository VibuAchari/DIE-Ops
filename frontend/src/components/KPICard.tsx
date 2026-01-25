import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, DollarSign, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface Props {
    title: string;
    value: string | number;
    icon: 'users' | 'money' | 'trend';
    color?: string;
    trend?: 'up' | 'down' | null;
    trendValue?: string;
}

export const KPICard: React.FC<Props> = ({ title, value, icon, color = 'text-blue', trend, trendValue }) => {
    const Icon = icon === 'users' ? Users : icon === 'money' ? DollarSign : TrendingUp;

    const gradientMap: Record<string, string> = {
        'text-blue': 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
        'text-green': 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
        'text-yellow': 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
        'text-purple': 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            whileHover={{ scale: 1.02, y: -5 }}
            className="card"
            style={{ position: 'relative', overflow: 'hidden' }}
        >
            {/* Background Glow */}
            <div style={{
                position: 'absolute',
                top: '-50%',
                right: '-50%',
                width: '150px',
                height: '150px',
                background: gradientMap[color] || gradientMap['text-blue'],
                borderRadius: '50%',
                opacity: 0.1,
                filter: 'blur(40px)'
            }} />

            <div className="flex justify-between items-center mb-4">
                <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 500 }}>{title}</span>
                <div style={{
                    background: gradientMap[color] || gradientMap['text-blue'],
                    padding: '10px',
                    borderRadius: '12px',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
                }}>
                    <Icon size={20} color="white" />
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem' }}>
                <span style={{ fontSize: '2rem', fontWeight: 700, color: '#f8fafc' }}>{value}</span>
                {trend && trendValue && (
                    <span style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '2px',
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        color: trend === 'up' ? '#34d399' : '#f87171'
                    }}>
                        {trend === 'up' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                        {trendValue}
                    </span>
                )}
            </div>
        </motion.div>
    );
};
