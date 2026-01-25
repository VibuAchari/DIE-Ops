import React from 'react';
import { motion } from 'framer-motion';
import { Users, Target, FileText, LayoutDashboard, Sparkles } from 'lucide-react';

interface NavItem {
    name: string;
    icon: React.ReactNode;
    id: string;
}

interface Props {
    active: string;
    onNavigate: (id: string) => void;
}

const navItems: NavItem[] = [
    { name: 'Overview', icon: <LayoutDashboard size={18} />, id: 'overview' },
    { name: 'Customers', icon: <Users size={18} />, id: 'customers' },
    { name: 'Campaigns', icon: <Target size={18} />, id: 'campaign' },
    { name: 'Reports', icon: <FileText size={18} />, id: 'reports' },
];

export const Navbar: React.FC<Props> = ({ active, onNavigate }) => {
    return (
        <motion.nav
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{
                background: 'rgba(15, 23, 42, 0.8)',
                backdropFilter: 'blur(20px)',
                padding: '1rem 2rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
                marginBottom: '2rem',
                position: 'sticky',
                top: 0,
                zIndex: 100
            }}
        >
            {/* Logo */}
            <motion.div
                style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}
                whileHover={{ scale: 1.02 }}
                onClick={() => onNavigate('overview')}
            >
                <div style={{
                    padding: '10px',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                    borderRadius: '14px',
                    boxShadow: '0 4px 20px rgba(59, 130, 246, 0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <Sparkles color="white" size={22} />
                </div>
                <div>
                    <span style={{
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent'
                    }}>
                        DIE-Ops
                    </span>
                    <span style={{
                        display: 'block',
                        fontSize: '0.65rem',
                        color: '#64748b',
                        marginTop: '-2px',
                        letterSpacing: '0.05em'
                    }}>
                        Intelligence Engine
                    </span>
                </div>
            </motion.div>

            {/* Navigation */}
            <div style={{ display: 'flex', gap: '0.5rem' }}>
                {navItems.map(item => (
                    <motion.button
                        key={item.id}
                        onClick={() => onNavigate(item.id)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.98 }}
                        style={{
                            background: active === item.id
                                ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)'
                                : 'transparent',
                            border: active === item.id
                                ? '1px solid rgba(59, 130, 246, 0.3)'
                                : '1px solid transparent',
                            color: active === item.id ? '#60a5fa' : '#94a3b8',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.6rem 1.25rem',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            fontSize: '0.9rem',
                            fontWeight: 500,
                            transition: 'all 0.2s ease',
                            boxShadow: active === item.id ? '0 4px 15px rgba(59, 130, 246, 0.2)' : 'none'
                        }}
                    >
                        {item.icon}
                        {item.name}
                    </motion.button>
                ))}
            </div>
        </motion.nav>
    );
};
