import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '40px', background: '#0c0a09', color: 'white', height: '100vh', fontFamily: 'sans-serif' }}>
                    <h1>Something went wrong.</h1>
                    <p>The application crashed with the following error:</p>
                    <pre style={{ background: '#1c1917', padding: '20px', borderRadius: '8px', color: '#ef4444', overflow: 'auto' }}>
                        {this.state.error?.toString()}
                    </pre>
                    <button
                        onClick={() => window.location.reload()}
                        style={{ marginTop: '20px', padding: '10px 20px', background: '#6366f1', border: 'none', borderRadius: '4px', color: 'white', cursor: 'pointer' }}
                    >
                        Reload Application
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
