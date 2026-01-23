import React, { useEffect, useRef } from 'react';
// @ts-ignore - plotly.js-dist-min doesn't have TypeScript definitions
import Plotly from 'plotly.js-dist-min';

interface PlotlyChartProps {
    data: any[];
    layout?: any;
    config?: any;
    style?: React.CSSProperties;
}

/**
 * Custom Plotly component that uses plotly.js directly via DOM refs
 * This bypasses react-plotly.js compatibility issues
 */
const PlotlyChart: React.FC<PlotlyChartProps> = ({ data, layout = {}, config = {}, style = {} }) => {
    const plotRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (plotRef.current && data && data.length > 0) {
            // Create or update the plot
            Plotly.newPlot(
                plotRef.current,
                data,
                layout,
                {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    ...config
                }
            );
        }

        // Cleanup on unmount
        return () => {
            if (plotRef.current) {
                Plotly.purge(plotRef.current);
            }
        };
    }, [data, layout, config]);

    return <div ref={plotRef} style={{ width: '100%', height: '100%', ...style }} />;
};

export default PlotlyChart;
