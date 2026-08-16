import { api } from './api.js';
import { formatBps, formatMetric, renderBadge } from './utils.js';

export async function renderResearchMemory(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Research Memory...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const mem = await api.getResearchMemory();

        let fieldRows = (mem.fields || []).slice(0, 15).map(f => `
            <tr>
                <td><strong>${f.field_name}</strong></td>
                <td>${f.total_candidates}</td>
                <td>${f.valid_simulations}</td>
                <td><span style="color: ${f.empty_portfolio_rate > 0.3 ? 'var(--status-danger)' : 'var(--text-main)'}; font-weight: 600;">${(f.empty_portfolio_rate * 100).toFixed(1)}%</span></td>
                <td><strong>${formatMetric(f.avg_sharpe)}</strong></td>
                <td><strong>${formatMetric(f.avg_fitness)}</strong></td>
                <td>${(f.success_rate * 100).toFixed(1)}%</td>
            </tr>
        `).join('');

        let opRows = (mem.operators || []).slice(0, 15).map(o => `
            <tr>
                <td><strong>${o.operator_name}</strong></td>
                <td>${o.total_candidates}</td>
                <td>${o.valid_simulations}</td>
                <td><span style="color: ${o.empty_portfolio_rate > 0.3 ? 'var(--status-danger)' : 'var(--text-main)'}; font-weight: 600;">${(o.empty_portfolio_rate * 100).toFixed(1)}%</span></td>
                <td><strong>${formatMetric(o.avg_sharpe)}</strong></td>
                <td><strong>${formatMetric(o.avg_fitness)}</strong></td>
                <td>${(o.success_rate * 100).toFixed(1)}%</td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="brain"></i> Persistent Research Memory</h3>
                        <span class="card-subtitle">Empirical performance tracking by Field and Operator to adaptively guide candidate generation</span>
                    </div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <!-- Field Performance Table -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 12px;"><i data-lucide="database"></i> Field Empirical Survival Matrix</h4>
                    <div class="table-container">
                        <table class="verde-table">
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Total</th>
                                    <th>Valid</th>
                                    <th>Empty %</th>
                                    <th>Avg Sharpe</th>
                                    <th>Avg Fitness</th>
                                    <th>Success</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${fieldRows || '<tr><td colspan="7" style="text-align: center;">No field memory records yet.</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Operator Performance Table -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 12px;"><i data-lucide="code"></i> Operator Empirical Survival Matrix</h4>
                    <div class="table-container">
                        <table class="verde-table">
                            <thead>
                                <tr>
                                    <th>Operator</th>
                                    <th>Total</th>
                                    <th>Valid</th>
                                    <th>Empty %</th>
                                    <th>Avg Sharpe</th>
                                    <th>Avg Fitness</th>
                                    <th>Success</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${opRows || '<tr><td colspan="7" style="text-align: center;">No operator memory records yet.</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();
    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
