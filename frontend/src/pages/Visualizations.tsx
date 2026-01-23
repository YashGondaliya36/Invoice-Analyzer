import React, { useState, useEffect } from 'react';
import { VisualizationService } from '../services/api';
import type { ChartData } from '../types';
import PlotlyChart from '../components/charts/PlotlyChart';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    BarChart3,
    Loader2,
    AlertCircle,
    CheckSquare,
    Square,
    ArrowRight,
    Sparkles,
    RefreshCw
} from 'lucide-react';



const Visualizations: React.FC = () => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [availableColumns, setAvailableColumns] = useState<string[]>([]);
    const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
    const [charts, setCharts] = useState<ChartData[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [showCharts, setShowCharts] = useState(false);

    useEffect(() => {
        const sid = localStorage.getItem('current_session_id');
        setSessionId(sid);
        if (sid) {
            fetchColumns(sid);
        } else {
            setLoading(false);
        }
    }, []);

    const fetchColumns = async (sid: string) => {
        setLoading(true);
        try {
            const res = await VisualizationService.getAvailableColumns(sid);
            setAvailableColumns(res.data.columns);
            // Pre-select all columns by default
            setSelectedColumns(res.data.columns);
        } catch (error) {
            console.error("Failed to fetch columns", error);
        } finally {
            setLoading(false);
        }
    };

    const toggleColumn = (col: string) => {
        setSelectedColumns(prev =>
            prev.includes(col)
                ? prev.filter(c => c !== col)
                : [...prev, col]
        );
    };

    const selectAll = () => setSelectedColumns([...availableColumns]);
    const deselectAll = () => setSelectedColumns([]);

    const generateCharts = async () => {
        if (!sessionId || selectedColumns.length === 0) return;

        setGenerating(true);
        setShowCharts(false);

        try {
            const res = await VisualizationService.getVisualizationsForColumns(sessionId, selectedColumns);
            // Normalize chart data: Plotly expects data to always be an array
            const normalizedCharts = res.data.charts.map(chart => ({
                ...chart,
                data: Array.isArray(chart.data) ? chart.data : [chart.data]
            }));
            setCharts(normalizedCharts);
            setShowCharts(true);
        } catch (error) {
            console.error("Failed to generate charts", error);
        } finally {
            setGenerating(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[50vh] text-stone-500 gap-3">
                <Loader2 className="animate-spin" />
                <span>Loading column data...</span>
            </div>
        );
    }

    if (!sessionId || availableColumns.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-[50vh] space-y-4 animate-fade-in">
                <div className="w-16 h-16 rounded-2xl bg-stone-900 border border-stone-800 flex items-center justify-center text-stone-600">
                    <BarChart3 size={32} />
                </div>
                <h3 className="text-xl font-bold text-white">No Data Available</h3>
                <p className="text-stone-400">Upload and process invoices to visualize data.</p>
                <Link to="/upload" className="btn-accent">
                    Go to Upload
                </Link>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-fade-in pb-10">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Data Visualizations</h1>
                    <p className="text-stone-400 mt-1">Select columns to generate charts (No AI required)</p>
                </div>
                <div className="px-4 py-2 rounded-full bg-stone-900 border border-stone-800 text-xs font-mono text-emerald-500 flex items-center gap-2">
                    <Sparkles size={14} />
                    INSTANT CHARTS
                </div>
            </div>

            {/* Column Selection */}
            <div className="industrial-panel p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <BarChart3 size={20} className="text-accent" />
                        Select Columns to Visualize
                    </h2>
                    <div className="flex gap-2">
                        <button
                            onClick={selectAll}
                            className="text-xs text-stone-400 hover:text-white transition-colors px-2 py-1"
                        >
                            Select All
                        </button>
                        <span className="text-stone-600">|</span>
                        <button
                            onClick={deselectAll}
                            className="text-xs text-stone-400 hover:text-white transition-colors px-2 py-1"
                        >
                            Clear
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-6">
                    {availableColumns.map((col) => (
                        <button
                            key={col}
                            onClick={() => toggleColumn(col)}
                            className={`p-3 rounded-xl border text-left transition-all flex items-center gap-3 group ${selectedColumns.includes(col)
                                ? 'bg-accent/10 border-accent/50 text-white'
                                : 'bg-stone-900/50 border-stone-800 text-stone-400 hover:border-stone-700'
                                }`}
                        >
                            {selectedColumns.includes(col) ? (
                                <CheckSquare size={18} className="text-accent shrink-0" />
                            ) : (
                                <Square size={18} className="text-stone-600 group-hover:text-stone-500 shrink-0" />
                            )}
                            <span className="text-sm font-medium truncate">{col}</span>
                        </button>
                    ))}
                </div>

                <div className="flex items-center justify-between border-t border-stone-800 pt-4">
                    <p className="text-sm text-stone-500">
                        {selectedColumns.length} of {availableColumns.length} columns selected
                    </p>
                    <button
                        onClick={generateCharts}
                        disabled={generating || selectedColumns.length === 0}
                        className="btn-accent"
                    >
                        {generating ? (
                            <>
                                <RefreshCw className="animate-spin" size={18} />
                                Generating...
                            </>
                        ) : (
                            <>
                                Generate Charts
                                <ArrowRight size={18} />
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Charts Display */}
            <AnimatePresence>
                {showCharts && charts.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        className="space-y-6"
                    >
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-bold text-white">
                                Generated Charts ({charts.length})
                            </h2>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {charts.map((chart, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className="border border-stone-800 rounded-xl overflow-hidden bg-stone-950 p-4 shadow-lg flex flex-col"
                                >
                                    <h3 className="text-stone-400 font-bold mb-4 px-2 uppercase text-xs tracking-wider border-b border-stone-900 pb-2">
                                        {chart.chart_name}
                                    </h3>
                                    <div className="flex-1 min-h-[350px]">
                                        <PlotlyChart
                                            data={chart.data}
                                            layout={{
                                                ...chart.layout,
                                                paper_bgcolor: 'rgba(0,0,0,0)',
                                                plot_bgcolor: 'rgba(0,0,0,0)',
                                                font: { color: '#a8a29e' },
                                                margin: { t: 10, r: 10, l: 50, b: 50 },
                                                autosize: true,
                                            }}
                                            config={{ responsive: true, displayModeBar: true, displaylogo: false }}
                                            style={{ width: '100%', height: '100%' }}
                                        />
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Empty State for Charts */}
            {showCharts && charts.length === 0 && (
                <div className="text-center py-16 text-stone-500">
                    <AlertCircle size={48} className="mx-auto mb-4 opacity-30" />
                    <p>No charts could be generated for the selected columns.</p>
                    <p className="text-sm mt-2">Try selecting different column combinations.</p>
                </div>
            )}
        </div>
    );
};

export default Visualizations;
