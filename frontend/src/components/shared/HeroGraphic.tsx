import React from 'react';
import { motion } from 'framer-motion';

const HeroGraphic: React.FC = () => {
    return (
        <div className="relative w-full max-w-[600px] aspect-square mx-auto">
            {/* Dynamic Light Background instead of weird circle */}
            <div className="absolute inset-0 bg-gradient-radial from-accent/5 to-transparent opacity-40 blur-3xl pointer-events-none" />

            <svg viewBox="0 0 600 500" className="w-full h-full drop-shadow-2xl overflow-visible">
                <defs>
                    <linearGradient id="glass-gradient" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stopColor="#292524" stopOpacity="0.9" />
                        <stop offset="100%" stopColor="#1c1917" stopOpacity="0.95" />
                    </linearGradient>
                    <linearGradient id="accent-gradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#ff5722" />
                        <stop offset="100%" stopColor="#f97316" />
                    </linearGradient>
                    <linearGradient id="chart-gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#ff5722" stopOpacity="0.5" />
                        <stop offset="100%" stopColor="#ff5722" stopOpacity="0" />
                    </linearGradient>
                    <pattern id="grid-pattern" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
                        <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#292524" strokeWidth="0.5" />
                    </pattern>
                </defs>

                {/* Grid Background */}
                <rect x="0" y="0" width="600" height="500" fill="url(#grid-pattern)" opacity="0.4" />

                {/* Central Futuristic Document Interface */}
                <motion.g
                    initial={{ y: 30, opacity: 0, scale: 0.95 }}
                    animate={{ y: 0, opacity: 1, scale: 1 }}
                    transition={{ duration: 1.2, ease: "easeOut" }}
                >
                    {/* Main Panel */}
                    <rect x="150" y="50" width="300" height="400" rx="16" fill="url(#glass-gradient)" stroke="#44403c" strokeWidth="1.5" style={{ filter: 'drop-shadow(0 20px 50px rgba(0,0,0,0.5))' }} />

                    {/* Header Bar */}
                    <path d="M 150 66 C 150 57.163 157.163 50 166 50 H 434 C 442.837 50 450 57.163 450 66 V 90 H 150 V 66 Z" fill="#292524" />
                    <circle cx="170" cy="70" r="4" fill="#ef4444" opacity="0.8" />
                    <circle cx="185" cy="70" r="4" fill="#f59e0b" opacity="0.8" />
                    <circle cx="200" cy="70" r="4" fill="#10b981" opacity="0.8" />

                    {/* Content Placeholders */}
                    <rect x="190" y="130" width="100" height="10" rx="4" fill="#57534e" />
                    <rect x="190" y="160" width="220" height="6" rx="2" fill="#44403c" />
                    <rect x="190" y="180" width="200" height="6" rx="2" fill="#44403c" />
                    <rect x="190" y="200" width="180" height="6" rx="2" fill="#44403c" />

                    {/* Invoice Table Effect */}
                    <rect x="190" y="240" width="220" height="30" rx="4" fill="#292524" stroke="#44403c" strokeWidth="0.5" />
                    <rect x="190" y="280" width="220" height="1" fill="#44403c" />
                    <rect x="190" y="310" width="220" height="1" fill="#44403c" />
                    <rect x="190" y="340" width="220" height="1" fill="#44403c" />

                    {/* Animated Scanning Line */}
                    <motion.rect
                        x="150" y="100" width="300" height="2" fill="url(#accent-gradient)"
                        animate={{ y: [0, 350, 0], opacity: [0, 1, 0] }}
                        transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                        style={{ filter: "drop-shadow(0 0 8px #ff5722)" }}
                    />
                </motion.g>

                {/* Left Floating Chart Card */}
                <motion.g
                    initial={{ x: -40, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.6, duration: 0.8 }}
                >
                    <rect x="50" y="250" width="180" height="140" rx="12" fill="#1c1917" stroke="#44403c" strokeWidth="1" style={{ filter: 'drop-shadow(0 10px 30px rgba(0,0,0,0.3))' }} />
                    <text x="70" y="280" fill="#a8a29e" fontSize="10" fontWeight="bold" letterSpacing="0.5">REVENUE TREND</text>
                    {/* Area Chart */}
                    <path d="M 70 350 L 70 330 L 100 310 L 130 340 L 160 300 L 190 320 L 210 290V 350 H 70 Z" fill="url(#chart-gradient)" />
                    <path d="M 70 330 L 100 310 L 130 340 L 160 300 L 190 320 L 210 290" fill="none" stroke="#ff5722" strokeWidth="2" strokeLinecap="round" />
                    {/* Highlight Dot */}
                    <circle cx="210" cy="290" r="4" fill="#ffffff" stroke="#ff5722" strokeWidth="2" />

                    {/* Floating Badge */}
                    <rect x="170" y="240" width="50" height="20" rx="10" fill="#292524" stroke="#44403c" />
                    <text x="195" y="253" fill="#10b981" fontSize="9" fontWeight="bold" textAnchor="middle">+24%</text>
                </motion.g>

                {/* Right Floating AI Terminal */}
                <motion.g
                    initial={{ x: 40, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.8, duration: 0.8 }}
                >
                    <rect x="370" y="200" width="200" height="140" rx="12" fill="#0c0a09" stroke="#ff5722" strokeWidth="1.5" style={{ filter: 'drop-shadow(0 10px 30px rgba(255,87,34,0.1))' }} />
                    <path d="M 370 212 C 370 205.373 375.373 200 382 200 H 558 C 564.627 200 570 205.373 570 212 V 224 H 370 V 212 Z" fill="#ff5722" fillOpacity="0.1" />
                    <text x="385" y="216" fill="#ff5722" fontSize="9" fontWeight="bold" letterSpacing="1">AI_ANALYST_KERNEL</text>

                    <text x="385" y="245" fontFamily="monospace" fontSize="10" fill="#10b981">&gt; initializing model...</text>
                    <text x="385" y="265" fontFamily="monospace" fontSize="10" fill="#a8a29e">&gt; analyzing_patterns</text>
                    <text x="385" y="285" fontFamily="monospace" fontSize="10" fill="#e5e5e5">Found 3 anomalies</text>
                    <text x="385" y="305" fontFamily="monospace" fontSize="10" fill="#a8a29e">&gt; query_execution: <tspan fill="#10b981">DONE</tspan></text>

                    <motion.rect
                        x="385" y="315" width="8" height="12" fill="#ff5722"
                        animate={{ opacity: [1, 0] }}
                        transition={{ repeat: Infinity, duration: 0.8 }}
                    />
                </motion.g>

                {/* Abstract Data Flow Connectors */}
                <path d="M 210 290 C 260 290, 300 290, 370 270" fill="none" stroke="#ff5722" strokeWidth="1" strokeDasharray="3 3" opacity="0.3" />
                <circle cx="370" cy="270" r="3" fill="#ff5722" opacity="0.5" />
            </svg>
        </div>
    );
};

export default HeroGraphic;
