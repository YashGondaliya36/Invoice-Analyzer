import axios from 'axios';
import type { Session, AnalyticsResponse, InsightResponse, ProcessingResponse, InvoiceDataResponse, VisualizationResponse } from '../types';

const API_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const InvoiceService = {
    createSession: async () => {
        // In this app, uploading invoices creates a session, or we can just list them.
        // For now, let's assume we manage sessions via the list.
        return api.get<Session[]>('/sessions/');
    },

    uploadInvoices: async (files: File[]) => {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        return api.post<{ session_id: string, message: string }>('/invoices/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    processInvoices: async (sessionId: string) => {
        return api.post<ProcessingResponse>(`/invoices/process/${sessionId}`);
    },

    getInvoices: async (sessionId: string) => {
        return api.get<InvoiceDataResponse>(`/invoices/${sessionId}`);
    }
};

export const AnalyticsService = {
    generateReport: async (sessionId: string) => {
        return api.post<{ report: string }>(`/reports/generate/${sessionId}`);
    },

    getReport: async (sessionId: string) => {
        return api.get<{ report: string }>(`/reports/${sessionId}`);
    },

    uploadCsv: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post<{ session_id: string, message: string }>('/analytics/upload-csv', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    askQuestion: async (sessionId: string, question: string) => {
        return api.post<AnalyticsResponse>(`/analytics/ask/${sessionId}`, { question });
    },

    getInsights: async (sessionId: string) => {
        return api.get<{ insights: InsightResponse[], summary: any }>(`/analytics/insights/${sessionId}`);
    },

    getVisualizations: async (sessionId: string) => {
        return api.get<VisualizationResponse>(`/visualizations/${sessionId}`);
    },

    getChartUrl: (sessionId: string) => `${API_URL}/analytics/chart/${sessionId}`,

    getChatHistory: async (sessionId: string) => {
        return api.get<any[]>(`/analytics/history/${sessionId}`);
    }
};

export const SessionService = {
    getAllSessions: async () => {
        return api.get<{ sessions: Session[] }>('/sessions/');
    },

    deleteSession: async (sessionId: string) => {
        return api.delete<{ message: string }>(`/sessions/${sessionId}`);
    }
};

// Visualization Service for Column Selection Flow (No LLM)
export const VisualizationService = {
    getAvailableColumns: async (sessionId: string) => {
        return api.get<{ success: boolean, session_id: string, columns: string[] }>(`/visualizations/columns/${sessionId}`);
    },

    getVisualizationsForColumns: async (sessionId: string, columns: string[]) => {
        // Build query string for columns
        const params = new URLSearchParams();
        columns.forEach(col => params.append('columns', col));
        return api.get<VisualizationResponse>(`/visualizations/${sessionId}?${params.toString()}`);
    }
};
