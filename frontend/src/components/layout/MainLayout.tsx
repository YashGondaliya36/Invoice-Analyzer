import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, PieChart, Upload, BrainCircuit, ScanLine, BarChart3 } from 'lucide-react';
import clsx from 'clsx';
import NeuralBackground from './NeuralBackground';

interface MainLayoutProps {
    children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
    const navItems = [
        { icon: LayoutDashboard, label: 'Sessions', path: '/' },
        { icon: Upload, label: 'Upload', path: '/upload' },
        { icon: FileText, label: 'Invoices', path: '/invoices' },
        { icon: BarChart3, label: 'Charts', path: '/visualizations' },
        { icon: BrainCircuit, label: 'AI Analyst', path: '/analytics' },
        { icon: PieChart, label: 'Reports', path: '/reports' },
    ];

    return (
        <div className="flex h-screen bg-stone-950 text-text-main overflow-hidden">
            {/* Professional Sidebar */}
            <aside className="w-64 bg-stone-950 border-r border-stone-800 flex flex-col relative z-20">
                <div className="p-6 border-b border-stone-800/50 flex items-center gap-3">
                    <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
                        <ScanLine className="text-white" size={18} />
                    </div>
                    <h1 className="text-xl font-bold tracking-tight text-white">
                        Invoice<span className="text-accent">IQ</span>
                    </h1>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                clsx("nav-item group", isActive && "active")
                            }
                        >
                            <item.icon size={18} className="group-hover:text-accent transition-colors" />
                            {item.label}
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-stone-800/50">
                    <div className="bg-stone-900 rounded-xl p-4 border border-stone-800">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                            <span className="text-xs font-medium text-stone-400">System Operational</span>
                        </div>
                        <p className="text-[10px] text-stone-500 font-mono">v1.2.0 • PRO</p>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 overflow-hidden relative flex flex-col">
                {/* Top Header Bar */}
                <header className="h-16 border-b border-stone-800 bg-stone-950/80 backdrop-blur-md flex items-center justify-between px-8 z-10">
                    <div className="text-sm text-stone-400 font-medium">Workspace / <span className="text-white">Financial Analysis</span></div>
                    <div className="flex items-center gap-4">
                        <div className="w-8 h-8 rounded-full bg-stone-800 border border-stone-700 flex items-center justify-center text-xs font-bold text-accent">
                            US
                        </div>
                    </div>
                </header>

                <div className="flex-1 overflow-auto p-8 relative">
                    {/* Background Grid Pattern */}
                    <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
                        style={{ backgroundImage: `radial-gradient(#a8a29e 1px, transparent 1px)`, backgroundSize: '32px 32px' }}>
                    </div>

                    {/* Living Neural Network */}
                    <NeuralBackground />

                    <div className="relative z-10 max-w-7xl mx-auto">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default MainLayout;
