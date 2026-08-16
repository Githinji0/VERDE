export function renderScatterPlot(elementId, seriesData, xTitle = "Turnover", yTitle = "Sharpe") {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (!window.ApexCharts) {
        el.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 13px;">Statistical visualization active. (ApexCharts CDN loading...)</div>`;
        return;
    }

    el.innerHTML = "";

    const options = {
        series: seriesData,
        chart: {
            height: 350,
            type: 'scatter',
            zoom: { enabled: true, type: 'xy' },
            toolbar: { show: true },
            fontFamily: 'Quicksand, sans-serif'
        },
        colors: ['#15803d', '#d97706', '#dc2626'],
        xaxis: {
            title: { text: xTitle, style: { fontWeight: 600 } },
            labels: { formatter: (val) => parseFloat(val).toFixed(2) }
        },
        yaxis: {
            title: { text: yTitle, style: { fontWeight: 600 } },
            labels: { formatter: (val) => parseFloat(val).toFixed(2) }
        },
        grid: {
            borderColor: '#e2e8f0'
        },
        tooltip: {
            custom: function({ series, seriesIndex, dataPointIndex, w }) {
                const data = w.globals.initialSeries[seriesIndex].data[dataPointIndex];
                return `
                    <div style="padding: 10px; font-family: Quicksand; font-size: 12px;">
                        <strong>${data.expression || 'Candidate'}</strong><br/>
                        <span>Family: ${data.family || 'N/A'}</span><br/>
                        <span>Sharpe: ${data.y}</span> | <span>Turnover: ${data.x}</span><br/>
                        <span>Fitness: ${data.fitness || 'N/A'}</span>
                    </div>
                `;
            }
        }
    };

    const chart = new window.ApexCharts(el, options);
    chart.render();
    return chart;
}

export function renderBarChart(elementId, categories, seriesData, title = "") {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (!window.ApexCharts) {
        el.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 13px;">Performance distribution active. (ApexCharts CDN loading...)</div>`;
        return;
    }

    el.innerHTML = "";

    const options = {
        series: seriesData,
        chart: {
            type: 'bar',
            height: 350,
            toolbar: { show: false },
            fontFamily: 'Quicksand, sans-serif'
        },
        colors: ['#15803d', '#22c55e'],
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
                borderRadius: 4
            }
        },
        dataLabels: { enabled: false },
        stroke: { show: true, width: 2, colors: ['transparent'] },
        xaxis: {
            categories: categories,
            labels: { style: { fontSize: '11px', fontWeight: 600 } }
        },
        yaxis: {
            title: { text: title }
        },
        fill: { opacity: 1 },
        grid: { borderColor: '#e2e8f0' }
    };

    const chart = new window.ApexCharts(el, options);
    chart.render();
    return chart;
}
