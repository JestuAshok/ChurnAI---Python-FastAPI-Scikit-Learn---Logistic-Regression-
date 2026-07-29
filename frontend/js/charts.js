/**
 * charts.js
 * Drawing scripts for responsive dark-themed Plotly charts.
 */

// Shared Dark Theme Layout Configurations
const themeLayout = {
    paper_bgcolor: 'rgba(0, 0, 0, 0)',
    plot_bgcolor: 'rgba(0, 0, 0, 0)',
    font: {
        family: 'Inter, sans-serif',
        color: '#A1A1AA' // var(--text-secondary)
    },
    title: {
        font: {
            family: 'Outfit, sans-serif',
            color: '#FFFFFF',
            size: 16
        },
        x: 0.05
    },
    margin: { l: 50, r: 20, t: 60, b: 50 },
    xaxis: {
        gridcolor: 'rgba(255, 255, 255, 0.05)',
        linecolor: 'rgba(255, 255, 255, 0.1)',
        tickcolor: 'rgba(255, 255, 255, 0.1)',
        zerolinecolor: 'rgba(255, 255, 255, 0.05)'
    },
    yaxis: {
        gridcolor: 'rgba(255, 255, 255, 0.05)',
        linecolor: 'rgba(255, 255, 255, 0.1)',
        tickcolor: 'rgba(255, 255, 255, 0.1)',
        zerolinecolor: 'rgba(255, 255, 255, 0.05)'
    },
    showlegend: true,
    legend: {
        font: { size: 11 },
        bgcolor: 'rgba(24, 24, 27, 0.8)',
        bordercolor: 'rgba(255, 255, 255, 0.05)',
        borderwidth: 1
    }
};

const plotlyConfig = {
    responsive: true,
    displayModeBar: false
};

// 1. Customer Churn Distribution (Donut Chart)
function drawChurnDistribution(data) {
    const trace = {
        labels: data.labels,
        values: data.values,
        type: 'pie',
        hole: 0.5,
        marker: {
            colors: ['#14B8A6', '#EC4899'] // Teal (No Churn), Pink (Churn)
        },
        textinfo: 'percent+label',
        hoverinfo: 'label+value+percent',
        automargin: true
    };

    const layout = JSON.parse(JSON.stringify(themeLayout));
    layout.title.text = 'Overall Customer Churn Ratio';
    layout.showlegend = true;
    layout.legend.x = 0.8;
    layout.legend.y = 0.9;

    Plotly.newPlot('chart-churn-dist', [trace], layout, plotlyConfig);
}

// 2. Contract Type vs Churn (Grouped Bar Chart)
function drawContractVsChurn(data) {
    const traceNoChurn = {
        x: data.categories,
        y: data.no_churn,
        name: 'Retained',
        type: 'bar',
        marker: { color: '#14B8A6' }
    };

    const traceChurn = {
        x: data.categories,
        y: data.churn,
        name: 'Churned',
        type: 'bar',
        marker: { color: '#EC4899' }
    };

    const layout = JSON.parse(JSON.stringify(themeLayout));
    layout.title.text = 'Churn Rate by Contract Type';
    layout.barmode = 'group';
    layout.xaxis.title = 'Contract Type';
    layout.yaxis.title = 'Customer Count';

    Plotly.newPlot('chart-contract-churn', [traceNoChurn, traceChurn], layout, plotlyConfig);
}

// 3. Monthly Charges vs Churn (Box/Violin Plot)
function drawMonthlyChargesVsChurn(data) {
    const traceNoChurn = {
        y: data.no_churn,
        name: 'Retained',
        type: 'box',
        boxpoints: 'suspectedoutliers',
        marker: { color: '#14B8A6' },
        line: { width: 1.5 }
    };

    const traceChurn = {
        y: data.churn,
        name: 'Churned',
        type: 'box',
        boxpoints: 'suspectedoutliers',
        marker: { color: '#EC4899' },
        line: { width: 1.5 }
    };

    const layout = JSON.parse(JSON.stringify(themeLayout));
    layout.title.text = 'Monthly Charges Distribution';
    layout.yaxis.title = 'Monthly Charges ($)';
    layout.xaxis.title = 'Status';
    layout.showlegend = false;

    Plotly.newPlot('chart-charges-churn', [traceNoChurn, traceChurn], layout, plotlyConfig);
}

// 4. Tenure vs Churn (Violin/Box Plot)
function drawTenureVsChurn(data) {
    const traceNoChurn = {
        y: data.no_churn,
        name: 'Retained',
        type: 'violin',
        meanline: { visible: true },
        marker: { color: '#14B8A6' },
        points: false
    };

    const traceChurn = {
        y: data.churn,
        name: 'Churned',
        type: 'violin',
        meanline: { visible: true },
        marker: { color: '#EC4899' },
        points: false
    };

    const layout = JSON.parse(JSON.stringify(themeLayout));
    layout.title.text = 'Customer Tenure (Months) vs Churn';
    layout.yaxis.title = 'Tenure (Months)';
    layout.showlegend = false;

    Plotly.newPlot('chart-tenure-churn', [traceNoChurn, traceChurn], layout, plotlyConfig);
}

// 5. Internet Service vs Churn (Grouped Bar Chart)
function drawInternetServiceVsChurn(data) {
    const traceNoChurn = {
        x: data.categories,
        y: data.no_churn,
        name: 'Retained',
        type: 'bar',
        marker: { color: '#14B8A6' }
    };

    const traceChurn = {
        x: data.categories,
        y: data.churn,
        name: 'Churned',
        type: 'bar',
        marker: { color: '#EC4899' }
    };

    const layout = JSON.parse(JSON.stringify(themeLayout));
    layout.title.text = 'Internet Service Type vs Churn';
    layout.barmode = 'group';
    layout.xaxis.title = 'Internet Service Option';
    layout.yaxis.title = 'Customer Count';

    Plotly.newPlot('chart-internet-churn', [traceNoChurn, traceChurn], layout, plotlyConfig);
}

// 6. Feature Importance (Horizontal Bar Chart)
function drawFeatureImportance(data) {
    // Sort data in ascending order for drawing horizontal bar chart from top to bottom
    const sorted = [...data].sort((a, b) => a.abs_importance - b.abs_importance);
    
    const xValues = sorted.map(item => item.importance);
    const yValues = sorted.map(item => item.feature);
    
    // Create color array: positive values green/teal, negative purple/pink
    const colors = xValues.map(val => val >= 0 ? '#EC4899' : '#14B8A6');

    const trace = {
        x: xValues,
        y: yValues,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: colors,
            line: { width: 1, color: 'rgba(255, 255, 255, 0.1)' }
        },
        hoverinfo: 'x+y'
    };

    const layout = JSON.parse(JSON.stringify(themeLayout));
    layout.title.text = 'Feature Coefficients Impact (Horizontal Coefficients)';
    layout.xaxis.title = 'Coefficient Weight (Positive increases Churn risk)';
    layout.yaxis.title = 'Features';
    layout.showlegend = false;
    layout.margin.l = 220; // Extra left margin for long feature names

    Plotly.newPlot('chart-feature-importance', [trace], layout, plotlyConfig);
}

// 7. Prediction Probability Distribution (Histogram)
function drawProbabilityDistribution(data) {
    const trace = {
        x: data,
        type: 'histogram',
        nbinsx: 30,
        marker: {
            color: '#8B5CF6',
            line: { color: 'rgba(255, 255, 255, 0.1)', width: 1 }
        },
        opacity: 0.75,
        hoverinfo: 'x+y'
    };

    const layout = JSON.parse(JSON.stringify(themeLayout));
    layout.title.text = 'Distribution of Predicted Churn Probability';
    layout.xaxis.title = 'Predicted Churn Probability';
    layout.yaxis.title = 'Frequency';
    layout.showlegend = false;

    // Draw a vertical threshold line at 0.38
    layout.shapes = [{
        type: 'line',
        x0: 0.38,
        y0: 0,
        x1: 0.38,
        y1: 1,
        yref: 'paper',
        line: {
            color: '#EF4444',
            width: 2.5,
            dash: 'dashdot'
        }
    }];
    
    // Add annotation for the threshold
    layout.annotations = [{
        x: 0.38,
        y: 0.95,
        yref: 'paper',
        text: 'Threshold (0.38)',
        showarrow: true,
        arrowhead: 2,
        ax: 60,
        ay: 0,
        font: { color: '#EF4444', size: 11 }
    }];

    Plotly.newPlot('chart-prob-dist', [trace], layout, plotlyConfig);
}

// Global drawing trigger
function initAnalyticsCharts() {
    const container = document.getElementById('analytics-loader');
    if (container) container.style.display = 'block';

    fetch('/api/analytics')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load analytics aggregates.');
            return response.json();
        })
        .then(data => {
            if (container) container.style.display = 'none';
            
            // Render all Plotly plots
            drawChurnDistribution(data.churn_distribution);
            drawContractVsChurn(data.contract_vs_churn);
            drawMonthlyChargesVsChurn(data.monthly_charges_vs_churn);
            drawTenureVsChurn(data.tenure_vs_churn);
            drawInternetServiceVsChurn(data.internet_service_vs_churn);
            drawFeatureImportance(data.feature_importance);
            drawProbabilityDistribution(data.probability_distribution);
        })
        .catch(err => {
            if (container) {
                container.innerHTML = `<span style="color: #EF4444; font-weight: 500;">Error: ${err.message}</span>`;
            }
            console.error('Analytics Loading Error:', err);
        });
}
