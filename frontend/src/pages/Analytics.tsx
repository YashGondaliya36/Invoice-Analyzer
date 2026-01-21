import React, { useState, useEffect, useRef } from 'react';
import { AnalyticsService } from '../services/api';
import type { AnalyticsResponse } from '../types';
import Plot from 'react-plotly.js';
import { Send, Bot, User, Code, BarChart2, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

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
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const sid = localStorage.getItem('current_session_id');
        setSessionId(sid);

        // Initial Greeting
        setMessages([{
            id: 'init',
            role: 'assistant',
            text: "I'm ready to analyze your financial data. Ask me about trends, total profit, or ask for a visualization.",
            timestamp: new Date()
        }]);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

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
        setIsLoading(true);

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
            setIsLoading(false);
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
        <div className="h-[85vh] flex flex-col max-w-5xl mx-auto industrial-panel overflow-hidden border-stone-800">
            {/* Header */}
            <div className="p-4 border-b border-stone-800 bg-stone-900/50 flex items-center gap-3">
                <div className="p-2 bg-accent/10 rounded-lg">
                    <Sparkles className="text-accent" size={20} />
                </div>
                <div>
                    <h2 className="text-lg font-bold text-white">Financial Analyst Agent</h2>
                    <p className="text-xs text-stone-500 font-mono">POWERED BY GEMINI 2.0</p>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
                {messages.map((msg) => (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={msg.id}
                        className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        {msg.role === 'assistant' && (
                            <div className="w-8 h-8 rounded-full bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0">
                                <Bot size={16} className="text-accent" />
                            </div>
                        )}

                        <div className={`max-w-[80%] space-y-2`}>
                            {/* Message Bubble */}
                            <div className={`p-4 rounded-2xl shadow-sm border ${msg.role === 'user'
                                ? 'bg-accent text-white border-accent'
                                : 'bg-stone-900 border-stone-800 text-stone-200'
                                }`}>
                                <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                            </div>

                            {/* Chart Attachment */}
                            {msg.chart && (
                                <div className="border border-stone-800 rounded-xl overflow-hidden bg-stone-950 p-2 shadow-lg">
                                    <div className="flex items-center gap-2 px-3 py-2 text-xs font-mono text-stone-500 border-b border-stone-900 mb-2">
                                        <BarChart2 size={12} /> GENERATED_PLOT
                                    </div>
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

                            {/* Code Attachment */}
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
                    </motion.div>
                ))}

                {isLoading && (
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
                        disabled={isLoading || !input.trim()}
                        className="absolute right-2 p-2 bg-accent hover:bg-accent-hover text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Analytics;
