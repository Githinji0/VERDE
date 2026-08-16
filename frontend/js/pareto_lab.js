import { api } from './api.js';
import { renderScatterPlot } from './charts.js';
import { formatBps, formatMetric, renderBadge } from './utils.js';

export async function renderParetoLab(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Pareto Lab...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const paretoData = await api.getParetoData();
        const candidates = await api.getCandidates({ pareto_only: true });

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="target"></i> Multi-Objective Pareto Frontier</h3>
                        <span class="card-subtitle">Non-dominated alpha candidates maximizing Sharpe and Fitness while minimizing Turnover</span>
                    </div>
                </div>
            </div>

            <div class="pareto-container">
                <!-- Interactive Frontier Chart -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 12px;">
                        <i data-lucide="crosshair"></i> Non-Dominated Frontier (Sharpe vs. Turnover)
                    </h4>
                    <div id="chart-pareto-frontier" style="min-height: 380px;"></div>
                </div>

                <!-- Pareto Candidates Summary List -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 12px;">
                        <i data-lucide="award"></i> Pareto Optimal Candidates (${candidates.length})
                    </h4>
                    <div style="max-height: 400px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px;">
                        ${candidates.length > 0 ? candidates.map(c => `
                            <div class="card" style="margin: 0; padding: 12px; border-left: 3px solid var(--verde-primary);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <span class="badge badge-info">${c.family_code}</span>
                                    <span class="badge badge-pareto">Rank #${c.pareto_rank || 1}</span>
                                </div>
                                <div class="code-expr" style="display: block; font-size: 11px; margin-bottom: 6px;">${c.expression}</div>
                                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                                    <span><strong>Sharpe:</strong> ${formatMetric(c.sharpe)}</span>
                                    <span><strong>Turnover:</strong> ${formatMetric(c.turnover)}</span>
                                    <button class="btn btn-outline btn-sm" onclick="window.verdeUI.openCandidateModal('${c.id}')" style="padding: 2px 6px;">Inspect</button>
                                </div>
                            </div>
                        `).join('') : `
                            <div style="color: var(--text-muted); font-size: 13px; text-align: center; padding: 30px;">
                                No Pareto candidates identified yet.
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // Render Pareto Scatter
        const validPoints = paretoData.points || [];
        const paretoPoints = validPoints.filter(p => p.is_pareto).map(p => ({
            x: p.turnover || 0,
            y: p.sharpe || 0,
            expression: p.expression,
            family: p.family_code,
            fitness: p.fitness
        }));
        const nonParetoPoints = validPoints.filter(p => !p.is_pareto).map(p => ({
            x: p.turnover || 0,
            y: p.sharpe || 0,
            expression: p.expression,
            family: p.family_code,
            fitness: p.fitness
        }));

        renderScatterPlot("chart-pareto-frontier", [
            { name: "Pareto Frontier (Dominant)", data: paretoPoints },
            { name: "Subordinate Candidates", data: nonParetoPoints }
        ], "Turnover Ratio", "Sharpe Ratio");

    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
