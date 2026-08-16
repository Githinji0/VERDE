import { api } from './api.js';
import { renderBarChart, renderScatterPlot } from './charts.js';

export async function renderAnalytics(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Analytics...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const paretoData = await api.getParetoData();
        const familyData = await api.getFamilyStats();

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="bar-chart-2"></i> Quantitative Alpha Analytics</h3>
                        <span class="card-subtitle">Statistical dispersion, Pareto frontier, and family performance breakdown</span>
                    </div>
                </div>
            </div>

            <div class="charts-grid">
                <!-- Scatter Plot: Sharpe vs Turnover -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 12px;">
                        <i data-lucide="crosshair"></i> Sharpe vs. Turnover Dispersion
                    </h4>
                    <div id="chart-sharpe-turnover" style="min-height: 350px;"></div>
                </div>

                <!-- Bar Chart: Average Sharpe by Family -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 12px;">
                        <i data-lucide="layers"></i> Performance by Research Family
                    </h4>
                    <div id="chart-family-performance" style="min-height: 350px;"></div>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // Render Sharpe vs Turnover Scatter
        const validPoints = paretoData.points || [];
        const paretoPoints = validPoints.filter(p => p.is_pareto).map(p => ({
            x: p.turnover || 0,
            y: p.sharpe || 0,
            expression: p.expression,
            family: p.family_code,
            fitness: p.fitness
        }));
        const regularPoints = validPoints.filter(p => !p.is_pareto).map(p => ({
            x: p.turnover || 0,
            y: p.sharpe || 0,
            expression: p.expression,
            family: p.family_code,
            fitness: p.fitness
        }));

        renderScatterPlot("chart-sharpe-turnover", [
            { name: "Pareto Optimal", data: paretoPoints },
            { name: "Standard Candidates", data: regularPoints }
        ], "Turnover Ratio", "Sharpe Ratio");

        // Render Family Bar Chart
        const categories = familyData.map(f => f.family_code);
        const sharpeSeries = familyData.map(f => f.avg_sharpe || 0);
        const fitnessSeries = familyData.map(f => f.avg_fitness || 0);

        renderBarChart("chart-family-performance", categories, [
            { name: "Avg Sharpe", data: sharpeSeries },
            { name: "Avg Fitness", data: fitnessSeries }
        ], "Alpha Metric");

    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
