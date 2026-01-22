import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, FileText, Image, Table, ArrowRight } from 'lucide-react';
import { InvoiceService, AnalyticsService } from '../services/api';
import { useNavigate } from 'react-router-dom';

type UploadMode = 'invoices' | 'csv';

const UploadInvoices: React.FC = () => {
    const navigate = useNavigate();
    const [mode, setMode] = useState<UploadMode>('invoices');
    const [files, setFiles] = useState<File[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => setIsDragging(false);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files) {
            handleFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleFiles = (newFiles: File[]) => {
        let validFiles: File[] = [];

        if (mode === 'invoices') {
            validFiles = newFiles.filter(file =>
                file.type === 'application/pdf' || file.type.startsWith('image/')
            );
        } else {
            // CSV mode: only accept one CSV
            validFiles = newFiles.filter(file => file.name.endsWith('.csv'));
            if (validFiles.length > 0) {
                setFiles([validFiles[0]]); // Only allow one CSV
                return;
            }
        }
        setFiles(prev => [...prev, ...validFiles]);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            handleFiles(Array.from(e.target.files));
        }
    };

    const removeFile = (index: number) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        if (files.length === 0) return;
        setUploading(true);
        setProgress(10);

        try {
            if (mode === 'invoices') {
                // Flow 1: Invoice Images -> AI Extraction
                const uploadRes = await InvoiceService.uploadInvoices(files);
                const sessionId = uploadRes.data.session_id;
                setProgress(50);

                await InvoiceService.processInvoices(sessionId);
                setProgress(100);

                localStorage.setItem('current_session_id', sessionId);
                setTimeout(() => navigate('/invoices'), 800);
            } else {
                // Flow 2: CSV -> Direct Analytics
                const uploadRes = await AnalyticsService.uploadCsv(files[0]);
                const sessionId = uploadRes.data.session_id;
                setProgress(100);

                localStorage.setItem('current_session_id', sessionId);
                setTimeout(() => navigate('/analytics'), 800);
            }

        } catch (error) {
            console.error(error);
            setUploading(false);
            alert("Upload failed. Please check the logs.");
        }
    };

    const switchMode = (newMode: UploadMode) => {
        setMode(newMode);
        setFiles([]);
    };

    const acceptTypes = mode === 'invoices' ? '.pdf,image/*' : '.csv';

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in relative z-10">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Data Ingestion</h1>
                    <p className="text-stone-400 mt-2">Choose your data source for analysis.</p>
                </div>
                <div className="px-4 py-2 rounded-full bg-stone-900 border border-stone-800 text-xs font-mono text-emerald-500 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    SCANNER READY
                </div>
            </div>

            {/* Mode Toggle */}
            <div className="flex gap-4">
                <button
                    onClick={() => switchMode('invoices')}
                    className={`flex-1 p-6 rounded-2xl border-2 transition-all duration-300 group ${mode === 'invoices'
                        ? 'border-accent bg-accent/5 shadow-[0_0_30px_rgba(255,87,34,0.1)]'
                        : 'border-stone-800 bg-stone-900/30 hover:border-stone-700'
                        }`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center transition-colors ${mode === 'invoices' ? 'bg-accent/20' : 'bg-stone-800'
                            }`}>
                            <Image className={`${mode === 'invoices' ? 'text-accent' : 'text-stone-500'}`} size={28} />
                        </div>
                        <div className="text-left">
                            <h3 className={`font-bold text-lg ${mode === 'invoices' ? 'text-white' : 'text-stone-400'}`}>
                                Invoice Images
                            </h3>
                            <p className="text-sm text-stone-500">Upload PDFs, JPGs, PNGs for AI extraction</p>
                        </div>
                    </div>
                </button>

                <button
                    onClick={() => switchMode('csv')}
                    className={`flex-1 p-6 rounded-2xl border-2 transition-all duration-300 group ${mode === 'csv'
                        ? 'border-accent bg-accent/5 shadow-[0_0_30px_rgba(255,87,34,0.1)]'
                        : 'border-stone-800 bg-stone-900/30 hover:border-stone-700'
                        }`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center transition-colors ${mode === 'csv' ? 'bg-accent/20' : 'bg-stone-800'
                            }`}>
                            <Table className={`${mode === 'csv' ? 'text-accent' : 'text-stone-500'}`} size={28} />
                        </div>
                        <div className="text-left">
                            <h3 className={`font-bold text-lg ${mode === 'csv' ? 'text-white' : 'text-stone-400'}`}>
                                CSV Data
                            </h3>
                            <p className="text-sm text-stone-500">Already have structured data? Skip extraction.</p>
                        </div>
                    </div>
                </button>
            </div>

            {/* Drop Zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`relative h-72 rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer overflow-hidden group
                    ${isDragging
                        ? 'border-accent bg-accent/5 shadow-[0_0_40px_rgba(255,87,34,0.15)]'
                        : 'border-stone-800 bg-stone-900/50 hover:border-stone-700 hover:bg-stone-900'
                    }`}
            >
                <input
                    type="file"
                    multiple={mode === 'invoices'}
                    className="hidden"
                    ref={fileInputRef}
                    onChange={handleFileInput}
                    accept={acceptTypes}
                />

                {/* Scanner Light Effect */}
                <div className={`absolute inset-0 bg-gradient-to-b from-transparent via-accent/5 to-transparent h-[200%] w-full transition-transform duration-[2000ms] ease-in-out
                    ${uploading ? 'animate-scan' : 'translate-y-[-100%] group-hover:translate-y-[100%]'}`}
                />

                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <div className={`w-16 h-16 rounded-2xl border flex items-center justify-center mb-4 transition-all duration-300
                        ${isDragging ? 'border-accent bg-accent/10 scale-110' : 'border-stone-700 bg-stone-800'}`}>
                        <Upload className={`transition-colors ${isDragging ? 'text-accent' : 'text-stone-400'}`} size={28} />
                    </div>
                    <p className="text-lg font-medium text-white">
                        {isDragging ? 'Drop to Initialize' : mode === 'invoices' ? 'Drop invoice files here' : 'Drop CSV file here'}
                    </p>
                    <p className="text-sm text-stone-500 mt-1">
                        {mode === 'invoices' ? 'Supports PDF, JPG, PNG' : 'Single .csv file'}
                    </p>
                </div>
            </div>

            {/* File Queue & Actions */}
            <AnimatePresence>
                {files.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        className="space-y-4"
                    >
                        <div className="flex items-center justify-between text-sm text-stone-400 border-b border-stone-800 pb-2">
                            <span>QUEUE ({files.length})</span>
                            <button onClick={() => setFiles([])} className="text-red-400 hover:text-red-300 transition-colors">
                                Clear
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {files.map((file, i) => (
                                <motion.div
                                    key={`${file.name}-${i}`}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className="industrial-panel p-3 flex items-center justify-between group px-4"
                                >
                                    <div className="flex items-center gap-3 overflow-hidden">
                                        <FileText size={18} className="text-stone-500 shrink-0" />
                                        <span className="text-sm text-stone-200 truncate">{file.name}</span>
                                        <span className="text-xs text-stone-600 font-mono">
                                            {(file.size / 1024).toFixed(1)} KB
                                        </span>
                                    </div>
                                    <button
                                        onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                                        className="p-1 hover:bg-stone-800 rounded-md text-stone-500 hover:text-red-400 transition-colors"
                                    >
                                        <X size={16} />
                                    </button>
                                </motion.div>
                            ))}
                        </div>

                        <div className="flex justify-end pt-4">
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className={`btn-accent relative overflow-hidden ${uploading ? 'cursor-not-allowed opacity-80' : ''}`}
                            >
                                {uploading ? (
                                    <>
                                        <span className="animate-pulse">Processing... {progress}%</span>
                                        <div
                                            className="absolute bottom-0 left-0 h-1 bg-white/20 transition-all duration-300"
                                            style={{ width: `${progress}%` }}
                                        />
                                    </>
                                ) : (
                                    <>
                                        {mode === 'invoices' ? 'Start AI Extraction' : 'Launch Analytics'}
                                        <ArrowRight size={18} className="ml-2" />
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <style>{`
                @keyframes scan {
                    0% { transform: translateY(-100%); }
                    100% { transform: translateY(100%); }
                }
                .animate-scan {
                    animation: scan 2s linear infinite;
                }
            `}</style>
        </div>
    );
};

export default UploadInvoices;
