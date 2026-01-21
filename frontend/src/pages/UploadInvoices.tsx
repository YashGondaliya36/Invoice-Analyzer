import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, FileText, CheckCircle } from 'lucide-react';
import { InvoiceService } from '../services/api'; // Correct Import
import { useNavigate } from 'react-router-dom';

const UploadInvoices: React.FC = () => {
    const navigate = useNavigate();
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
        const validFiles = newFiles.filter(file =>
            file.type === 'application/pdf' || file.type.startsWith('image/')
        );
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

        // Simulating start progress
        setProgress(10);

        try {
            // 1. Upload
            const uploadRes = await InvoiceService.uploadInvoices(files);
            const sessionId = uploadRes.data.session_id;
            setProgress(50);

            // 2. Process
            await InvoiceService.processInvoices(sessionId);
            setProgress(100);

            // Store session
            localStorage.setItem('current_session_id', sessionId);

            // Navigate
            setTimeout(() => {
                navigate('/invoices');
            }, 800);

        } catch (error) {
            console.error(error);
            setUploading(false);
            alert("Upload failed. Please check the logs.");
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in relative z-10">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Invoice Ingestion</h1>
                    <p className="text-stone-400 mt-2">Upload PDFs or Images for automated extraction.</p>
                </div>
                <div className="px-4 py-2 rounded-full bg-stone-900 border border-stone-800 text-xs font-mono text-emerald-500 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    SCANNER READY
                </div>
            </div>

            {/* Holographic Drop Zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`relative h-80 rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer overflow-hidden group
                    ${isDragging
                        ? 'border-accent bg-accent/5 shadow-[0_0_40px_rgba(255,87,34,0.15)]'
                        : 'border-stone-800 bg-stone-900/50 hover:border-stone-700 hover:bg-stone-900'
                    }`}
            >
                <input
                    type="file"
                    multiple
                    className="hidden"
                    ref={fileInputRef}
                    onChange={handleFileInput}
                    accept=".pdf,image/*"
                />

                {/* Scanner Light Effect */}
                <div className={`absolute inset-0 bg-gradient-to-b from-transparent via-accent/5 to-transparent h-[200%] w-full transition-transform duration-[2000ms] ease-in-out
                    ${uploading ? 'animate-scan' : 'translate-y-[-100%] group-hover:translate-y-[100%]'}`}
                />

                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <div className={`w-20 h-20 rounded-2xl border flex items-center justify-center mb-6 transition-all duration-300
                        ${isDragging ? 'border-accent bg-accent/10 scale-110' : 'border-stone-700 bg-stone-800'}`}>
                        <Upload className={`transition-colors ${isDragging ? 'text-accent' : 'text-stone-400'}`} size={32} />
                    </div>
                    <p className="text-lg font-medium text-white">
                        {isDragging ? 'Drop to Initialize Scan' : 'Drop invoices here'}
                    </p>
                    <p className="text-sm text-stone-500 mt-2">
                        Support for PDF, JPG, PNG
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
                            <span>WAITING QUEUE ({files.length})</span>
                            <button onClick={() => setFiles([])} className="text-red-400 hover:text-red-300 transition-colors">
                                Clear Queue
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
                                        Start Extraction Sequence
                                        <CheckCircle size={18} className="ml-2" />
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
