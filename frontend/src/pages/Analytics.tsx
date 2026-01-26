import React, { useState, useEffect, useRef } from 'react';
import { AnalyticsService, SessionService } from '../services/api';
import type { Session } from '../types';
import PlotlyChart from '../components/charts/PlotlyChart';
import { Send, Bot, User, Code, Loader2, Sparkles, AlertCircle, MessageSquare, Plus, Clock, Trash2, ChevronRight } from 'lucide-react';


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
    const [sessions, setSessions] = useState<Session[]>([]);
    const [isLoadingSessions, setIsLoadingSessions] = useState(false);

    // Chat State
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoadingChat, setIsLoadingChat] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initial Load
    useEffect(() => {
        loadSessions();
        const sid = localStorage.getItem('current_session_id');
        if (sid) {
            setSessionId(sid);
        }
    }, []);

    // Load Chat History when SessionId changes
    useEffect(() => {
        if (sessionId) {
            localStorage.setItem('current_session_id', sessionId);
            loadChatHistory(sessionId);
        } else {
            setMessages([]);
        }
    }, [sessionId]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadSessions = async () => {
        setIsLoadingSessions(true);
        try {
            const res = await SessionService.getAllSessions();
            if (res.data.sessions) {
                // Sort by created_at desc
                const sorted = res.data.sessions.sort((a, b) =>
                    new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
                );
                setSessions(sorted);
            }
        } catch (error) {
            console.error("Failed to load sessions", error);
        } finally {
            setIsLoadingSessions(false);
        }
    };

    const loadChatHistory = async (sid: string) => {
        try {
            const res = await AnalyticsService.getChatHistory(sid);
            const history = res.data;

            if (history && history.length > 0) {
                const mappedMessages: Message[] = history.map((item: any, idx: number) => {
                    let chartData = null;
                    if (item.visualization) {
                        try {
                            // If it's a string, parse it. It might already be an object depending on axios
                            chartData = typeof item.visualization === 'string'
                                ? JSON.parse(item.visualization)
                                : item.visualization;
                        } catch (e) { console.error("Chart parse error", e); }
                    }

                    return {
                        id: `hist-${idx}`,
                        role: item.role,
                        text: item.text,
                        code: item.code,
                        chart: chartData,
                        timestamp: new Date(item.timestamp)
                    };
                });
                setMessages(mappedMessages);
            } else {
                // New/Empty session greeting
                setMessages([{
                    id: 'init',
                    role: 'assistant',
                    text: "I'm ready to analyze your financial data. Ask me about trends, total profit, or ask for a visualization.",
                    timestamp: new Date()
                }]);
            }
        } catch (error) {
            console.error("Failed to load history", error);
        }
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

    const handleDeleteSession = async (e: React.MouseEvent, sid: string) => {
        e.stopPropagation();
        if (window.confirm('Are you sure you want to delete this session?')) {
            try {
                await SessionService.deleteSession(sid);
                setSessions(prev => prev.filter(s => s.session_id !== sid));
                if (sessionId === sid) {
                    setSessionId(null);
                    setMessages([]);
                }
            } catch (err) {
                console.error("Delete failed", err);
            }
        }
    }

    if (!sessionId && sessions.length === 0 && !isLoadingSessions) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-4">
                <AlertCircle className="text-stone-500" size={48} />
                <h2 className="text-2xl font-bold text-white">No Data Sessions</h2>
                <p className="text-stone-400">Please upload invoices to start a new analysis session.</p>
            </div>
        );
    }

    return (
        <div className="h-[88vh] grid grid-cols-12 gap-6 max-w-7xl mx-auto overflow-hidden">

            {/* Sidebar - Session List */}
            <div className="col-span-3 industrial-panel flex flex-col overflow-hidden bg-stone-900/50 border-stone-800">
                <div className="p-4 border-b border-stone-800">
                    <button
                        className="w-full flex items-center gap-2 px-4 py-3 bg-accent/10 hover:bg-accent/20 text-accent rounded-lg transition-colors text-sm font-semibold"
                        onClick={() => window.location.href = '/upload'} // Or properly navigate
                    >
                        <Plus size={16} /> New Analysis
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {isLoadingSessions ? (
                        <div className="flex justify-center p-4"><Loader2 className="animate-spin text-stone-500" /></div>
                    ) : (
                        sessions.map(sess => (
                            <div
                                key={sess.session_id}
                                onClick={() => setSessionId(sess.session_id)}
                                className={`group flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all ${sessionId === sess.session_id
                                    ? 'bg-stone-800 text-white'
                                    : 'text-stone-400 hover:bg-stone-800/50 hover:text-stone-300'
                                    }`}
                            >
                                <MessageSquare size={16} className="mt-1 shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <h4 className="text-sm font-medium truncate">
                                        Session {sess.session_id.slice(0, 8)}
                                    </h4>
                                    <div className="flex items-center gap-2 mt-1">
                                        <Clock size={10} />
                                        <span className="text-xs opacity-60">
                                            {new Date(sess.created_at || '').toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => handleDeleteSession(e, sess.session_id)}
                                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="col-span-9 flex flex-col industrial-panel overflow-hidden border-stone-800 relative bg-stone-950/80 backdrop-blur-md">
                {/* Header */}
                <div className="p-4 border-b border-stone-800 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-accent/10 rounded-lg">
                            <Sparkles className="text-accent" size={20} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white">Financial Intelligence</h2>
                            <p className="text-xs text-stone-500 font-mono">
                                {sessionId ? `SESSION: ${sessionId.slice(0, 8)}...` : 'SELECT A SESSION'}
                            </p>
                        </div>
                    </div>
                </div>

                {sessionId ? (
                    <div className="flex-1 overflow-hidden relative flex flex-col">
                        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin">
                            {messages.map((msg) => (
                                <div
                                    key={msg.id}
                                    className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    {msg.role === 'assistant' && (
                                        <div className="w-8 h-8 rounded-full bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0 mt-1">
                                            <Bot size={16} className="text-accent" />
                                        </div>
                                    )}

                                    <div className={`max-w-[85%] space-y-2`}>
                                        <div className={`p-4 rounded-2xl shadow-sm border ${msg.role === 'user'
                                            ? 'bg-accent text-white border-accent'
                                            : 'bg-stone-900 border-stone-800 text-stone-200'
                                            }`}>
                                            <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                                        </div>

                                        {msg.chart && (
                                            <div className="border border-stone-800 rounded-xl overflow-hidden bg-stone-950 p-2 shadow-lg">
                                                <PlotlyChart
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
                                                    config={{
                                                        responsive: true,
                                                        displayModeBar: 'hover',
                                                        scrollZoom: true,
                                                        displaylogo: false
                                                    }}
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
                                                        <ChevronRight size={12} className="group-open:rotate-90 transition-transform" />
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
                                        <div className="w-8 h-8 rounded-full bg-stone-800 border border-stone-700 flex items-center justify-center shrink-0 mt-1">
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
                        <div className="p-4 bg-stone-900 border-t border-stone-800 z-10">
                            <div className="relative flex items-center gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Ask about trends, sales, or anomalies..."
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
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-stone-500 gap-4">
                        <MessageSquare size={48} className="opacity-20" />
                        <p>Select a session to view history</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Analytics;
