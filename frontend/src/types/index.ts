export interface InvoiceItem {
    invoice_no: string;
    date: string;
    customer_name: string;
    product_name: string;
    category: string;
    quantity: number;
    unit_price: number;
    total_price: number;
    [key: string]: string | number | undefined;
}


export interface InvoiceDataResponse {
    success: boolean;
    session_id: string;
    total_items: number;
    data: InvoiceItem[];
}

export interface ProcessingResponse {
    success: boolean;
    session_id: string;
    status: string;
    total_items: number;
    data: any[]; // Or InvoiceItem[] if strict
    processed_at: string;
}

export interface Session {
    session_id: string;
    created_at: string;
    invoice_count: number;
    has_report: boolean;
    has_csv: boolean;
}

export interface ChartData {
    chart_type: string;
    chart_name: string;
    data: any[];
    layout: any;
}

export interface AnalyticsResponse {
    success: boolean;
    answer?: string;
    code_generated?: string;
    visualization?: string;
    data?: string;
    error?: string;
}

export interface InsightResponse {
    text: string;
    category: 'info' | 'warning' | 'success';
    priority: 'high' | 'medium' | 'low';
}
