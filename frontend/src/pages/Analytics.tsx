import React, { useState, useEffect, useRef } from 'react';
import { AnalyticsService } from '../services/api';
import type { InsightResponse, ChartData } from '../types';
import Plot from 'react-plotly.js';
import { Send, Bot, User, Code, BarChart2, Loader2, Sparkles, AlertCircle, LayoutDashboard, MessageSquare, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    code?: string;
    chart?: any; // Parsed JSON
    timestamp: Date;
    loading?: boolean;
}

const Analytics: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'dashboard' | 'chat'>('dashboard');
    const [sessionId, setSessionId] = useState<string | null>(null);

    // Dashboard State
    const [insights, setInsights] = useState<InsightResponse[]>([]);
    const [dashboardCharts, setDashboardCharts] = useState<ChartData[]>([]);
    const [loadingDashboard, setLoadingDashboard] = useState(false);

    // Column Selection State
    const [availableColumns, setAvailableColumns] = useState<string[]>([]);
    const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
    const [loadingCharts, setLoadingCharts] = useState(false);

    // Chat State
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoadingChat, setIsLoadingChat] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const sid = localStorage.getItem('current_session_id');
        setSessionId(sid);

        if (sid) {
            fetchDashboardData(sid);
        }

        // Initial Greeting
        setMessages([{
            id: 'init',
            role: 'assistant',
            text: "I'm ready to analyze your financial data. Ask me about trends, total profit, or ask for a visualization.",
            timestamp: new Date()
        }]);
    }, []);

    const fetchDashboardData = async (sid: string) => {
        setLoadingDashboard(true);
        try {
            // Fetch Automated Insights
            const insightsRes = await AnalyticsService.getInsights(sid);
            setInsights(insightsRes.data.insights || []);

            // Fetch Available Columns
            try {
                const colsRes = await AnalyticsService.getColumns(sid);
                if (colsRes.data.columns) {
                    setAvailableColumns(colsRes.data.columns);
                    // Select all columns initially
                    setSelectedColumns(colsRes.data.columns);
                }
            } catch (e) {
                console.error("Failed to fetch columns", e);
            }

            // Fetch Dashboard Charts (with all columns initially)
            await fetchCharts(sid);

        } catch (error) {
            console.error("Failed to load dashboard data", error);
        } finally {
            setLoadingDashboard(false);
        }
    };

    const fetchCharts = async (sid: string, columns?: string[]) => {
        setLoadingCharts(true);
        try {
            const chartsRes = await AnalyticsService.getVisualizations(sid, columns);
            if (chartsRes.data.charts) {
                // Normalize chart data: Plotly expects data to always be an array
                const normalizedCharts = chartsRes.data.charts.map(chart => ({
                    ...chart,
                    data: Array.isArray(chart.data) ? chart.data : [chart.data]
                }));
                setDashboardCharts(normalizedCharts);
            }
        } catch (error) {
            console.error("Failed to fetch charts", error);
        } finally {
            setLoadingCharts(false);
        }
    };

    const handleColumnToggle = (column: string) => {
        setSelectedColumns(prev =>
            prev.includes(column)
                ? prev.filter(c => c !== column)
                : [...prev, column]
        );
    };

    const handleGenerateCharts = () => {
        if (sessionId && selectedColumns.length > 0) {
            fetchCharts(sessionId, selectedColumns);
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, activeTab]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSend = async () => {
        if (!input.trim() || !sessionId) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            text: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoadingChat(true);

        try {
            const response = await AnalyticsService.askQuestion(sessionId, userMsg.text);
            const data = response.data;

            let chartData = null;
            if (data.visualization) {
                try {
                    chartData = JSON.parse(data.visualization);
                } catch (e) {
                    console.error("Failed to parse chart", e);
                }
            }

            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                text: data.answer || "I processed that, but I'm not sure how to answer.",
                code: data.code_generated,
                chart: chartData,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMsg]);

        } catch (error) {
            console.error(error);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                text: "I encountered an error while analyzing the data. Please try again.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoadingChat(false);
        }
    };

    if (!sessionId) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-4">
                <AlertCircle className="text-stone-500" size={48} />
                <h2 className="text-2xl font-bold text-white">No Data Session Active</h2>
                <p className="text-stone-400">Please upload invoices to start an analysis session.</p>
            </div>
        );
    }

    return (
        <div className="h-[88vh] flex flex-col max-w-6xl mx-auto industrial-panel overflow-hidden border-stone-800 relative">
            {/* Header / Tabs */}
            <div className="p-4 border-b border-stone-800 bg-stone-900/80 flex items-center justify-between backdrop-blur-sm z-10">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent/10 rounded-lg">
                        <Sparkles className="text-accent" size={20} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-white">Financial Intelligence</h2>
                        <p className="text-xs text-stone-500 font-mono">POWERED BY GEMINI 2.0</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* View Chart Button */}
                    <a
                        href={AnalyticsService.getChartUrl(sessionId)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 bg-stone-800 border border-stone-700 text-stone-300 hover:text-white hover:border-accent/50"
                        title="Open generated chart in new tab"
                    >
                        <ExternalLink size={14} /> View Chart
                    </a>

                    {/* Tab Switcher */}
                    <div className="flex gap-1 bg-stone-950 p-1 rounded-lg border border-stone-800">
                        <button
                            onClick={() => setActiveTab('dashboard')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'dashboard'
                                ? 'bg-stone-800 text-white shadow-sm'
                                : 'text-stone-500 hover:text-stone-300'
                                }`}
                        >
                            <LayoutDashboard size={16} /> Dashboard
                        </button>
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'chat'
                                ? 'bg-stone-800 text-white shadow-sm'
                                : 'text-stone-500 hover:text-stone-300'
                                }`}
                        >
                            <MessageSquare size={16} /> Analyst Chat
                        </button>
                    </div>
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden relative">
                <AnimatePresence mode='wait'>
                    {activeTab === 'dashboard' ? (
                        <motion.div
                            key="dashboard"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            className="h-full overflow-y-auto p-6 space-y-8 scrollbar-thin"
                        >
                            {loadingDashboard ? (
                                <div className="flex flex-col items-center justify-center h-full text-stone-500 gap-3">
                                    <Loader2 className="animate-spin" size={32} />
                                    <span>Synthesizing Insights...</span>
                                </div>
                            ) : (
                                <>
                                    {/* Insights Section */}
                                    {insights.length > 0 && (
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                            {insights.map((insight, idx) => (
                                                <div key={idx} className="p-4 rounded-xl bg-stone-900/50 border border-stone-800 hover:border-accent/30 transition-colors">
                                                    <div className="flex items-start gap-3">
                                                        <Sparkles className="text-amber-400 shrink-0 mt-1" size={16} />
                                                        <p className="text-sm text-stone-300 leading-relaxed">{insight.text}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Column Selector Section */}
                                    {availableColumns.length > 0 && (
                                        <div className="p-4 rounded-xl bg-stone-900/30 border border-stone-800">
                                            <div className="flex items-center justify-between mb-4">
                                                <h3 className="text-sm font-bold text-stone-400 uppercase tracking-wider flex items-center gap-2">
                                                    <BarChart2 size={14} /> Select Columns for Visualization
                                                </h3>
                                                <button
                                                    onClick={handleGenerateCharts}
                                                    disabled={selectedColumns.length === 0 || loadingCharts}
                                                    className="px-4 py-2 rounded-lg text-sm font-medium transition-all bg-accent hover:bg-accent/80 text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                                >
                                                    {loadingCharts ? (
                                                        <Loader2 size={14} className="animate-spin" />
                                                    ) : (
                                                        <BarChart2 size={14} />
                                                    )}
                                                    Generate Charts
                                                </button>
                                            </div>
                                            <div className="flex flex-wrap gap-2">
                                                {availableColumns.map((column) => (
                                                    <button
                                                        key={column}
                                                        onClick={() => handleColumnToggle(column)}
                                                        className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all border ${selectedColumns.includes(column)
                                                                ? 'bg-accent/20 border-accent text-accent'
                                                                : 'bg-stone-900 border-stone-700 text-stone-500 hover:border-stone-600'
                                                            }`}
                                                    >
                                                        {column}
                                                    </button>
                                                ))}
                                            </div>
                                            <p className="text-xs text-stone-600 mt-3">
                                                {selectedColumns.length} of {availableColumns.length} columns selected
                                            </p>
                                        </div>
                                    )}

                                    {/* Charts Grid */}
                                    {dashboardCharts.length > 0 ? (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            {dashboardCharts.map((chart, idx) => (
                                                <div key={idx} className="border border-stone-800 rounded-xl overflow-hidden bg-stone-950 p-4 shadow-lg flex flex-col">
                                                    <h3 className="text-stone-400 font-bold mb-4 px-2 uppercase text-xs tracking-wider border-b border-stone-900 pb-2">
                                                        {chart.chart_name}
                                                    </h3>
                                                    <div className="flex-1 min-h-[300px]">
                                                        <Plot
                                                            data={chart.data}
                                                            layout={{
                                                                ...chart.layout,
                                                                paper_bgcolor: 'rgba(0,0,0,0)',
                                                                plot_bgcolor: 'rgba(0,0,0,0)',
                                                                font: { color: '#a8a29e' },
                                                                margin: { t: 10, r: 10, l: 40, b: 40 },
                                                                autosize: true,
                                                            }}
                                                            useResizeHandler={true}
                                                            style={{ width: '100%', height: '100%' }}
                                                            config={{ responsive: true, displayModeBar: false }}
                                                        />
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-20 text-stone-500">
                                            <BarChart2 size={48} className="mx-auto mb-4 opacity-20" />
                                            <p>No visualization data available yet.</p>
                                        </div>
                                    )}
                                </>
                            )}
                        </motion.div>
                    ) : (
                        <motion.div
                            key="chat"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="h-full flex flex-col"
                        >
                            {/* Chat Messages */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
                                {messages.map((msg) => (
                                    <div
                                        key={msg.id}
                                        className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        {msg.role === 'assistant' && (
                                            <div className="w-8 h-8 rounded-full bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0">
                                                <Bot size={16} className="text-accent" />
                                            </div>
                                        )}

                                        <div className={`max-w-[80%] space-y-2`}>
                                            <div className={`p-4 rounded-2xl shadow-sm border ${msg.role === 'user'
                                                ? 'bg-accent text-white border-accent'
                                                : 'bg-stone-900 border-stone-800 text-stone-200'
                                                }`}>
                                                <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                                            </div>

                                            {msg.chart && (
                                                <div className="border border-stone-800 rounded-xl overflow-hidden bg-stone-950 p-2 shadow-lg">
                                                    <Plot
                                                        data={msg.chart.data}
                                                        layout={{
                                                            ...msg.chart.layout,
                                                            paper_bgcolor: 'rgba(0,0,0,0)',
                                                            plot_bgcolor: 'rgba(0,0,0,0)',
                                                            font: { color: '#a8a29e' },
                                                            margin: { t: 30, r: 20, l: 40, b: 40 },
                                                            autosize: true,
                                                            height: 400
                                                        }}
                                                        config={{ responsive: true, displayModeBar: false }}
                                                        style={{ width: '100%', height: '400px' }}
                                                    />
                                                </div>
                                            )}

                                            {msg.code && (
                                                <details className="group">
                                                    <summary className="cursor-pointer list-none">
                                                        <div className="inline-flex items-center gap-2 text-xs font-mono text-stone-500 hover:text-accent transition-colors">
                                                            <Code size={12} />
                                                            <span>VIEW_GENERATED_PYTHON</span>
                                                        </div>
                                                    </summary>
                                                    <div className="mt-2 bg-stone-950 rounded-lg p-3 border border-stone-800 overflow-x-auto">
                                                        <pre className="text-xs font-mono text-emerald-500/80">
                                                            {msg.code}
                                                        </pre>
                                                    </div>
                                                </details>
                                            )}
                                        </div>

                                        {msg.role === 'user' && (
                                            <div className="w-8 h-8 rounded-full bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0">
                                                <User size={16} className="text-stone-400" />
                                            </div>
                                        )}
                                    </div>
                                ))}

                                {isLoadingChat && (
                                    <div className="flex gap-4">
                                        <div className="w-8 h-8 rounded-full bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0">
                                            <Bot size={16} className="text-accent" />
                                        </div>
                                        <div className="flex items-center gap-2 p-4 rounded-xl bg-stone-900/50 border border-stone-800">
                                            <Loader2 size={18} className="animate-spin text-accent" />
                                            <span className="text-sm text-stone-400 animate-pulse">Analyzing...</span>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="p-4 bg-stone-900 border-t border-stone-800">
                                <div className="relative flex items-center gap-2">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Ask questions like 'Show me monthly sales' or 'Who is my top customer?'..."
                                        className="w-full bg-stone-950 border border-stone-800 text-white rounded-xl px-4 py-3 pr-12 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/50 transition-all font-medium placeholder-stone-600"
                                    />
                                    <button
                                        onClick={handleSend}
                                        disabled={isLoadingChat || !input.trim()}
                                        className="absolute right-2 p-2 bg-accent hover:bg-accent-hover text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <Send size={18} />
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default Analytics;
