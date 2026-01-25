import { motion } from 'framer-motion';
import { Github, Heart, Cpu, Zap, ExternalLink } from 'lucide-react';

export function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <motion.footer
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            style={{
                background: 'linear-gradient(to top, rgba(15, 23, 42, 0.95), transparent)',
                borderTop: '1px solid rgba(139, 92, 246, 0.1)',
                padding: '3rem 2rem 2rem',
                marginTop: '4rem',
            }}
        >
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                {/* Main Footer Content */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                    gap: '2rem',
                    marginBottom: '2rem',
                }}>
                    {/* About Section */}
                    <div>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            marginBottom: '1rem',
                        }}>
                            <div style={{
                                background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                                padding: '0.5rem',
                                borderRadius: '0.75rem',
                            }}>
                                <Cpu size={20} color="white" />
                            </div>
                            <span style={{
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                background: 'linear-gradient(135deg, #8b5cf6, #06b6d4)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                            }}>
                                DIE-Ops
                            </span>
                        </div>
                        <p style={{
                            color: 'rgba(148, 163, 184, 0.9)',
                            fontSize: '0.875rem',
                            lineHeight: 1.7,
                            marginBottom: '1rem',
                        }}>
                            <strong style={{ color: '#8b5cf6' }}>Decision Intelligence Engine</strong> for Enterprise Operations.
                            Transform customer analytics into actionable, ROI-driven decisions with advanced ML models
                            including Churn Prediction, Customer Lifetime Value, and Uplift Modeling.
                        </p>
                    </div>

                    {/* Features Section */}
                    <div>
                        <h4 style={{
                            color: '#e2e8f0',
                            fontSize: '0.875rem',
                            fontWeight: 600,
                            marginBottom: '1rem',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                        }}>
                            Key Features
                        </h4>
                        <ul style={{
                            listStyle: 'none',
                            padding: 0,
                            margin: 0,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.5rem',
                        }}>
                            {[
                                'ROI-Based Decision Optimization',
                                'Multi-Model ML Intelligence',
                                'SHAP Explainability',
                                'Budget-Constrained Targeting',
                                'Real-time Campaign Simulation',
                            ].map((feature, i) => (
                                <li key={i} style={{
                                    color: 'rgba(148, 163, 184, 0.8)',
                                    fontSize: '0.8125rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                }}>
                                    <Zap size={12} color="#8b5cf6" />
                                    {feature}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Links Section */}
                    <div>
                        <h4 style={{
                            color: '#e2e8f0',
                            fontSize: '0.875rem',
                            fontWeight: 600,
                            marginBottom: '1rem',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                        }}>
                            Resources
                        </h4>
                        <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.75rem',
                        }}>
                            <motion.a
                                href="https://github.com/VibuAchari/DIE-Ops"
                                target="_blank"
                                rel="noopener noreferrer"
                                whileHover={{ x: 4 }}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    color: '#e2e8f0',
                                    textDecoration: 'none',
                                    fontSize: '0.875rem',
                                    padding: '0.5rem 0.75rem',
                                    borderRadius: '0.5rem',
                                    background: 'rgba(139, 92, 246, 0.1)',
                                    border: '1px solid rgba(139, 92, 246, 0.2)',
                                    transition: 'all 0.2s ease',
                                }}
                            >
                                <Github size={16} />
                                View on GitHub
                                <ExternalLink size={12} style={{ marginLeft: 'auto', opacity: 0.5 }} />
                            </motion.a>
                            <a
                                href="https://github.com/VibuAchari/DIE-Ops/blob/main/README.md"
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    color: 'rgba(148, 163, 184, 0.8)',
                                    textDecoration: 'none',
                                    fontSize: '0.8125rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                }}
                            >
                                <ExternalLink size={12} />
                                Documentation
                            </a>
                            <a
                                href="https://github.com/VibuAchari/DIE-Ops/issues"
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    color: 'rgba(148, 163, 184, 0.8)',
                                    textDecoration: 'none',
                                    fontSize: '0.8125rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                }}
                            >
                                <ExternalLink size={12} />
                                Report Issues
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div style={{
                    borderTop: '1px solid rgba(139, 92, 246, 0.1)',
                    paddingTop: '1.5rem',
                    display: 'flex',
                    flexWrap: 'wrap',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '1rem',
                }}>
                    <div style={{
                        color: 'rgba(148, 163, 184, 0.6)',
                        fontSize: '0.8125rem',
                    }}>
                        © {currentYear} DIE-Ops. Built with{' '}
                        <Heart size={12} color="#ef4444" style={{ display: 'inline', verticalAlign: 'middle' }} />{' '}
                        using FastAPI + React
                    </div>

                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                    }}>
                        <span style={{
                            fontSize: '0.75rem',
                            color: 'rgba(148, 163, 184, 0.5)',
                            padding: '0.25rem 0.5rem',
                            background: 'rgba(139, 92, 246, 0.1)',
                            borderRadius: '0.25rem',
                        }}>
                            v2.0
                        </span>
                        <motion.a
                            href="https://github.com/VibuAchari/DIE-Ops"
                            target="_blank"
                            rel="noopener noreferrer"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: '2rem',
                                height: '2rem',
                                borderRadius: '0.5rem',
                                background: 'rgba(139, 92, 246, 0.1)',
                                border: '1px solid rgba(139, 92, 246, 0.2)',
                                color: '#e2e8f0',
                                transition: 'all 0.2s ease',
                            }}
                        >
                            <Github size={16} />
                        </motion.a>
                    </div>
                </div>
            </div>
        </motion.footer>
    );
}
