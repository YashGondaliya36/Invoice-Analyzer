import React from 'react';
import { motion } from 'framer-motion';

const HeroGraphic: React.FC = () => {
    return (
        <div className="relative w-full max-w-[500px] aspect-square mx-auto">
            {/* Background Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-accent/10 blur-[100px] rounded-full" />

            <svg viewBox="0 0 400 400" className="w-full h-full drop-shadow-2xl">
                {/* Abstract Base Grid */}
                <defs>
                    <pattern id="grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#292524" strokeWidth="1" />
                    </pattern>
                </defs>
                <rect width="400" height="400" fill="url(#grid)" opacity="0.5" />

                {/* Central Document Scanner */}
                <motion.g
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 1 }}
                >
                    {/* The "Paper" */}
                    <rect x="100" y="80" width="200" height="260" rx="12" fill="#1c1917" stroke="#44403c" strokeWidth="2" />
                    <rect x="120" y="110" width="80" height="8" rx="4" fill="#57534e" />
                    <rect x="220" y="110" width="60" height="8" rx="4" fill="#a8a29e" />

                    {/* Data Lines */}
                    {[140, 160, 180, 200, 220, 240, 260].map((y, i) => (
                        <rect key={i} x="120" y={y} width={160} height="4" rx="2" fill="#292524" />
                    ))}
                </motion.g>

                {/* Floating Analysis Cards */}
                <motion.g
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.5, duration: 0.8 }}
                >
                    {/* Left Card: Chart */}
                    <rect x="40" y="180" width="120" height="100" rx="8" fill="#292524" stroke="#44403c" strokeWidth="1" />
                    <path d="M 50 250 L 70 230 L 90 240 L 110 210 L 140 200" fill="none" stroke="#ff5722" strokeWidth="3" strokeLinecap="round" />
                    <circle cx="140" cy="200" r="4" fill="#ff5722" />
                </motion.g>

                <motion.g
                    initial={{ x: 20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.8, duration: 0.8 }}
                >
                    {/* Right Card: Code/Data */}
                    <rect x="250" y="240" width="130" height="90" rx="8" fill="#0c0a09" stroke="#ff5722" strokeWidth="2" />
                    <text x="265" y="270" fontFamily="monospace" fontSize="10" fill="#a8a29e">&gt; analyzing...</text>
                    <text x="265" y="290" fontFamily="monospace" fontSize="10" fill="#10b981">✓ 99.8% match</text>
                    <text x="265" y="310" fontFamily="monospace" fontSize="10" fill="#a8a29e" opacity="0.5">query_db()</text>
                </motion.g>

                {/* Scanning Laser Effect */}
                <motion.rect
                    x="90" y="80" width="220" height="2" fill="#ff5722"
                    initial={{ y: 80, opacity: 0 }}
                    animate={{ y: [80, 340, 80], opacity: [0, 1, 0] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    className="blur-[2px]"
                />
            </svg>
        </div>
    );
};

export default HeroGraphic;
