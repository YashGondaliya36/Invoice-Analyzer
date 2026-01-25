import React, { useState, useEffect } from 'react';
import { AnalyticsService } from '../services/api';
import { FileText, Download, RefreshCw, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Reports: React.FC = () => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [report, setReport] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        const sid = localStorage.getItem('current_session_id');
        setSessionId(sid);
        if (sid) {
            checkExistingReport(sid);
        }
    }, []);

    const checkExistingReport = async (sid: string) => {
        setLoading(true);
        try {
            const res = await AnalyticsService.getReport(sid);
            if (res.data.report) {
                setReport(res.data.report);
            }
        } catch (error) {
            // No report exists yet, that's fine
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        if (!sessionId) return;
        setGenerating(true);
        try {
            const res = await AnalyticsService.generateReport(sessionId);
            setReport(res.data.report);
        } catch (error) {
            console.error("Failed to generate report", error);
        } finally {
            setGenerating(false);
        }
    };

    // Simple markdown renderer styling using Tailwind typography if available, or custom
    // Since we don't have typography plugin installed, I'll do basic mapping or just text-formatted

    if (!sessionId) {
        return (
            <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
                <AlertCircle className="text-stone-500" size={48} />
                <h2 className="text-2xl font-bold text-white">No Data Session</h2>
                <p className="text-stone-400">Please upload invoices to generate a report.</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6 animate-fade-in pb-10">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Executive Report</h1>
                    <p className="text-stone-400 mt-1">AI-Generated financial summary and strategic insights.</p>
                </div>

                <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="btn-accent"
                >
                    {generating ? <RefreshCw className="animate-spin" size={20} /> : <FileText size={20} />}
                    {report ? 'Regenerate Report' : 'Generate Intelligence'}
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-20">
                    <RefreshCw className="animate-spin text-stone-500" size={32} />
                </div>
            ) : report ? (
                <div className="industrial-panel p-8 md:p-12 min-h-[60vh] relative overflow-hidden">
                    {/* Report Content */}
                    <div className="prose prose-invert prose-stone prose-lg max-w-none prose-headings:text-white prose-a:text-accent prose-strong:text-white prose-li:text-stone-300 pointer-events-none">
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                h1: ({ node, ...props }) => <h1 className="text-3xl font-bold text-white mb-6 mt-8 pb-2 border-b border-stone-800" {...props} />,
                                h2: ({ node, ...props }) => <h2 className="text-2xl font-bold text-accent mb-4 mt-8" {...props} />,
                                h3: ({ node, ...props }) => <h3 className="text-xl font-semibold text-white mb-3 mt-6" {...props} />,
                                p: ({ node, ...props }) => <p className="text-stone-300 leading-relaxed mb-4 text-lg" {...props} />,
                                ul: ({ node, ...props }) => <ul className="list-disc list-outside ml-6 space-y-2 mb-6 text-stone-300" {...props} />,
                                li: ({ node, ...props }) => <li className="pl-2" {...props} />,
                                strong: ({ node, ...props }) => <strong className="text-white font-bold" {...props} />,
                                blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-accent pl-4 italic text-stone-400 my-4 bg-stone-900/50 p-4 rounded-r-lg" {...props} />,
                            }}
                        >
                            {report}
                        </ReactMarkdown>
                    </div>

                    <div className="absolute top-4 right-4 pointer-events-auto">
                        <button className="p-2 hover:bg-stone-800 rounded-lg text-stone-500 hover:text-white transition-colors" title="Download Markdown">
                            <Download size={20} />
                        </button>
                    </div>
                </div>
            ) : (
                <div className="industrial-panel p-12 text-center border-dashed border-2 border-stone-800 bg-transparent flex flex-col items-center justify-center min-h-[40vh]">
                    <div className="w-16 h-16 rounded-2xl bg-stone-900 border border-stone-800 flex items-center justify-center mb-6">
                        <FileText size={32} className="text-stone-600" />
                    </div>
                    <h3 className="text-xl font-medium text-white mb-2">Ready to Compile</h3>
                    <p className="text-stone-400 max-w-md">
                        The AI will analyze all {sessionId} invoices to generate a comprehensive textual report highlighting key trends and anomalies.
                    </p>
                </div>
            )}
        </div>
    );
};

export default Reports;
