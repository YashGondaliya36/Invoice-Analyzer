import React from 'react';
import { Upload, BrainCircuit, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import HeroGraphic from '../components/shared/HeroGraphic';

const Home: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="grid lg:grid-cols-2 gap-16 items-center min-h-[80vh]">
            {/* Left Content */}
            <div className="space-y-8 animate-slide-up">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20 text-accent text-xs font-semibold tracking-wide uppercase">
                    <Activity size={14} /> AI-Powered Financial Intelligence
                </div>

                <h1 className="text-6xl font-bold tracking-tight text-white leading-[1.1]">
                    Transform <br />
                    <span className="text-stone-500">Invoices into</span> <br />
                    <span className="text-accent">Insights.</span>
                </h1>

                <p className="text-lg text-stone-400 max-w-lg leading-relaxed">
                    The enterprise-grade solution for automated invoice processing.
                    Upload documents, extract structured data, and query your financial history using natural language.
                </p>

                <div className="flex flex-wrap gap-4 pt-4">
                    <button
                        onClick={() => navigate('/upload')}
                        className="btn-accent"
                    >
                        <Upload size={20} />
                        Process Invoices
                    </button>

                    <button
                        onClick={() => navigate('/analytics')}
                        className="btn-ghost"
                    >
                        <BrainCircuit size={20} />
                        Analyst Dashboard
                    </button>
                </div>

                <div className="pt-8 border-t border-stone-800 flex gap-8">
                    <div>
                        <div className="text-2xl font-bold text-white">99.9%</div>
                        <div className="text-xs text-stone-500 font-medium uppercase tracking-wider">Extraction Accuracy</div>
                    </div>
                    <div>
                        <div className="text-2xl font-bold text-white">2x</div>
                        <div className="text-xs text-stone-500 font-medium uppercase tracking-wider">Faster Processing</div>
                    </div>
                </div>
            </div>

            {/* Right Graphic */}
            <div className="relative animate-fade-in lg:block hidden">
                <div className="absolute -inset-4 bg-stone-900/50 rounded-full blur-3xl opacity-20" />
                <HeroGraphic />

                {/* Floating "Live Status" Card */}
                <div className="absolute -bottom-8 -left-8 industrial-panel p-4 flex items-center gap-4 animate-float">
                    <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                        <Activity className="text-emerald-500" size={20} />
                    </div>
                    <div>
                        <div className="text-sm font-bold text-white">System Ready</div>
                        <div className="text-xs text-stone-500">Waiting for data stream...</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
