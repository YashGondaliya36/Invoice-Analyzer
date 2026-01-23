import React, { useEffect, useState } from 'react';
import { InvoiceService } from '../services/api';
import type { InvoiceItem } from '../types';
import { motion } from 'framer-motion';
import { RefreshCcw, Search, Filter, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

const Invoices: React.FC = () => {
    const [invoices, setInvoices] = useState<InvoiceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [sessionId, setSessionId] = useState<string | null>(null);

    useEffect(() => {
        const sid = localStorage.getItem('current_session_id');
        setSessionId(sid);
        if (sid) {
            fetchInvoices(sid);
        } else {
            setLoading(false);
        }
    }, []);

    const fetchInvoices = async (sid: string) => {
        setLoading(true);
        try {
            const res = await InvoiceService.getInvoices(sid);
            setInvoices(res.data.data);
        } catch (error) {
            console.error("Failed to fetch invoices", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[50vh] text-stone-500 gap-3">
                <RefreshCcw className="animate-spin" />
                <span>Syncing Ledger...</span>
            </div>
        );
    }

    if (!sessionId || invoices.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-[50vh] space-y-4 animate-fade-in">
                <div className="w-16 h-16 rounded-2xl bg-stone-900 border border-stone-800 flex items-center justify-center text-stone-600">
                    <Filter size={32} />
                </div>
                <h3 className="text-xl font-bold text-white">No Invoices Found</h3>
                <p className="text-stone-400">Upload documents to start analyzing.</p>
                <Link to="/upload" className="btn-accent">
                    Go to Upload
                </Link>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Extracted Data</h1>
                    <p className="text-stone-400 text-sm mt-1">Session ID: <span className="font-mono text-stone-500">{sessionId}</span></p>
                </div>
                <div className="flex gap-2">
                    <button className="btn-ghost text-sm px-4 h-10">
                        <Filter size={16} /> Filter
                    </button>
                    <button className="btn-ghost text-sm px-4 h-10">
                        <Search size={16} /> Search
                    </button>
                    <Link to="/visualizations" className="btn-accent text-sm px-4 h-10">
                        <BarChart3 size={16} /> Generate Charts
                    </Link>
                </div>
            </div>

            {/* Industrial Data Grid */}
            <div className="border border-stone-800 rounded-xl overflow-hidden bg-stone-900/50 shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-stone-950/80 text-stone-500 text-xs uppercase tracking-wider font-semibold border-b border-stone-800">
                                <th className="p-4 rounded-tl-xl">Invoice No</th>
                                <th className="p-4">Date</th>
                                <th className="p-4">Customer</th>
                                <th className="p-4">Product</th>
                                <th className="p-4">Category</th>
                                <th className="p-4 text-right">Unit Price</th>
                                <th className="p-4 text-center">Qty</th>
                                <th className="p-4 text-right rounded-tr-xl">Total</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-stone-800/50">
                            {invoices.map((inv, idx) => (
                                <motion.tr
                                    key={idx}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.05 }}
                                    className="hover:bg-stone-800/30 transition-colors group cursor-default"
                                >
                                    <td className="p-4 font-mono text-stone-300 group-hover:text-accent transition-colors">#{inv.invoice_no || 'N/A'}</td>
                                    <td className="p-4 text-stone-400 text-sm">{inv.date || 'N/A'}</td>
                                    <td className="p-4 font-medium text-white">{inv.customer_name || 'Unknown'}</td>
                                    <td className="p-4 text-stone-300 text-sm max-w-[200px] truncate">{inv.product_name}</td>
                                    <td className="p-4">
                                        <span className="inline-flex items-center px-2 py-1 rounded text-[10px] font-medium bg-stone-800 text-stone-400 border border-stone-700/50 border-dashed">
                                            {inv.category || 'General'}
                                        </span>
                                    </td>
                                    <td className="p-4 text-right font-mono text-stone-400">
                                        {inv.unit_price ? `$${Number(inv.unit_price).toFixed(2)}` : '-'}
                                    </td>
                                    <td className="p-4 text-center font-mono text-stone-500">{inv.quantity}</td>
                                    <td className="p-4 text-right font-mono font-medium text-emerald-500">
                                        {inv.total_price ? `$${Number(inv.total_price).toFixed(2)}` : '-'}
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Invoices;
