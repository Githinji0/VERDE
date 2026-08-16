import { api } from './api.js';
import { formatBps, formatMetric, formatTimestamp, renderBadge, showToast } from './utils.js';

let activePollTimer = null;
let currentFilter = 'ALL';
let currentSearch = '';
let cachedSims = [];

export async function refreshSimulationsData(silent = false) {
    const tbody = document.getElementById("simulations-tbody");
    const refreshBtnIcon = document.getElementById("sim-refresh-icon");

    if (refreshBtnIcon) refreshBtnIcon.classList.add("spin");

    try {
        const sims = await api.getSimulations({ limit: 150 });
        cachedSims = sims;

        updateStatsCounters(sims);
        renderTableBody(sims);

        // Schedule next background poll only if there are running jobs and user is on simulations page
        if (activePollTimer) {
            clearTimeout(activePollTimer);
            activePollTimer = null;
        }

        const hasRunning = sims.some(s => s.status === 'RUNNING' || s.status === 'SUBMITTING');
        if (hasRunning) {
            activePollTimer = setTimeout(() => {
                const curPage = window.location.hash.replace('#', '') || 'dashboard';
                if (curPage === 'simulations') {
                    refreshSimulationsData(true);
                }
            }, 3000);
        }
    } catch (err) {
        if (!silent && tbody) {
            tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--status-danger); padding: 20px;">Failed to refresh simulations: ${err.message}</td></tr>`;
        }
    } finally {
        if (refreshBtnIcon) refreshBtnIcon.classList.remove("spin");
    }
}

function updateStatsCounters(sims) {
    const total = sims.length;
    const valid = sims.filter(s => s.has_valid_metrics || s.metrics_status === 'AVAILABLE').length;
    const running = sims.filter(s => s.status === 'RUNNING' || s.status === 'SUBMITTING').length;
    const failed = sims.filter(s => s.classification === 'TECHNICAL_FAILURE' || s.classification === 'REMOTE_FAILURE' || s.classification === 'AUTH_FAILURE' || s.classification === 'ALPHA_FAILURE' || s.classification === 'PORTFOLIO_EMPTY' || s.portfolio_status === 'EMPTY').length;

    const countAll = document.getElementById("sim-count-all");
    const countValid = document.getElementById("sim-count-valid");
    const countRunning = document.getElementById("sim-count-running");
    const countFailed = document.getElementById("sim-count-failed");

    if (countAll) countAll.textContent = total;
    if (countValid) countValid.textContent = valid;
    if (countRunning) countRunning.textContent = running;
    if (countFailed) countFailed.textContent = failed;
}

function renderTableBody(sims) {
    const tbody = document.getElementById("simulations-tbody");
    const emptyState = document.getElementById("simulations-empty-state");
    const tableContainer = document.getElementById("simulations-table-container");
    if (!tbody) return;

    let filtered = sims;

    if (currentFilter === 'VALID') {
        filtered = filtered.filter(s => s.has_valid_metrics || s.metrics_status === 'AVAILABLE');
    } else if (currentFilter === 'RUNNING') {
        filtered = filtered.filter(s => s.status === 'RUNNING' || s.status === 'SUBMITTING');
    } else if (currentFilter === 'FAILED') {
        filtered = filtered.filter(s => s.classification !== 'VALID_METRICS' && s.status !== 'RUNNING' && s.status !== 'SUBMITTING');
    }

    if (currentSearch.trim()) {
        const q = currentSearch.toLowerCase().trim();
        filtered = filtered.filter(s => 
            (s.expression && s.expression.toLowerCase().includes(q)) ||
            (s.id && s.id.toLowerCase().includes(q)) ||
            (s.brain_sim_id && s.brain_sim_id.toLowerCase().includes(q)) ||
            (s.family_code && s.family_code.toLowerCase().includes(q))
        );
    }

    if (filtered.length === 0) {
        if (tableContainer) tableContainer.style.display = "none";
        if (emptyState) {
            emptyState.style.display = "block";
            emptyState.innerHTML = `
                <div style="text-align: center; padding: 48px; color: var(--text-muted);">
                    <i data-lucide="inbox" style="width: 36px; height: 36px; margin-bottom: 10px; opacity: 0.6;"></i>
                    <h4 style="font-size: 15px; font-weight: 700; color: var(--text-main); margin-bottom: 6px;">
                        ${sims.length === 0 ? 'No Simulations Submitted Yet' : 'No Matching Simulations Found'}
                    </h4>
                    <p style="font-size: 13px; max-width: 420px; margin: 0 auto 16px auto;">
                        ${sims.length === 0 ? 'Generate candidates in Alpha Lab or synthesize hypothesis mutations to begin backtesting.' : 'Try adjusting your search query or filter criteria.'}
                    </p>
                    ${sims.length === 0 ? `
                        <button class="btn btn-primary btn-sm" onclick="window.verdeUI.navigateTo('alpha-lab')">
                            <i data-lucide="sparkles"></i> Open Alpha Lab
                        </button>
                    ` : ''}
                </div>
            `;
            if (window.lucide) window.lucide.createIcons();
        }
        return;
    }

    if (tableContainer) tableContainer.style.display = "block";
    if (emptyState) emptyState.style.display = "none";

    tbody.innerHTML = filtered.map(s => {
        const showDiag = s.classification !== "VALID_METRICS" && s.status !== "RUNNING" && s.status !== "SUBMITTING";
        const isRunning = s.status === "RUNNING" || s.status === "SUBMITTING";

        return `
            <tr>
                <td>
                    <span style="font-family: monospace; font-size: 12px; font-weight: 700; color: var(--text-muted); background: #f8fafc; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-light);">
                        ${s.id.substring(0, 8)}
                    </span>
                </td>
                <td style="max-width: 280px;">
                    <div class="code-expr" style="font-size: 11.5px; padding: 6px 10px; max-height: 48px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${s.expression || ''}">
                        ${s.expression || 'N/A'}
                    </div>
                </td>
                <td>
                    <span class="badge badge-info" style="font-size: 11px;">${s.family_code || 'MOMENTUM'}</span>
                </td>
                <td>
                    ${isRunning ? `
                        <span class="badge badge-warning" style="display: inline-flex; align-items: center; gap: 5px;">
                            <i data-lucide="loader" class="spin" style="width: 12px; height: 12px;"></i> RUNNING
                        </span>
                    ` : renderBadge(s.status)}
                </td>
                <td>${renderBadge(s.portfolio_status)}</td>
                <td>${renderBadge(s.metrics_status)}</td>
                <td>
                    <strong style="color: ${s.sharpe >= 1.25 ? '#16a34a' : 'inherit'}; font-size: 13px;">
                        ${formatMetric(s.sharpe)}
                    </strong>
                </td>
                <td>
                    <strong style="color: ${s.fitness >= 1.00 ? '#16a34a' : 'inherit'}; font-size: 13px;">
                        ${formatMetric(s.fitness)}
                    </strong>
                </td>
                <td style="font-size: 13px;">${formatMetric(s.turnover)}</td>
                <td style="font-size: 13px;">${formatBps(s.margin_bps)}</td>
                <td style="white-space: nowrap;">
                    <div class="table-action-group">
                        ${showDiag ? `
                            <button class="btn-action-diag" onclick="window.verdeUI.openDiagnosticModal('${s.id}')" title="Inspect Diagnostic Reason">
                                <i data-lucide="alert-triangle"></i>
                                <span>Diagnostics</span>
                            </button>
                        ` : ''}
                        <button class="btn-action-icon" onclick="window.verdeUI.openCandidateModal('${s.candidate_id}')" title="Inspect Candidate Detail">
                            <i data-lucide="eye"></i>
                        </button>
                        <button class="btn-action-icon" id="btn-poll-${s.id}" onclick="window.verdeUI.pollSimulationInline('${s.id}')" title="Poll Remote Status from BRAIN">
                            <i data-lucide="refresh-cw"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
}

export async function renderSimulations(container) {
    if (activePollTimer) {
        clearTimeout(activePollTimer);
        activePollTimer = null;
    }

    container.innerHTML = `
        <!-- Top Stats Row -->
        <div class="kpi-row-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 20px;">
            <div class="card" style="margin: 0; padding: 16px; border-left: 4px solid var(--verde-primary);">
                <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Total Runs</div>
                <div style="font-size: 24px; font-weight: 800; color: var(--text-main); margin-top: 4px;" id="sim-count-all">-</div>
            </div>
            <div class="card" style="margin: 0; padding: 16px; border-left: 4px solid #16a34a;">
                <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Valid Alphas</div>
                <div style="font-size: 24px; font-weight: 800; color: #16a34a; margin-top: 4px;" id="sim-count-valid">-</div>
            </div>
            <div class="card" style="margin: 0; padding: 16px; border-left: 4px solid #eab308;">
                <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">In Progress</div>
                <div style="font-size: 24px; font-weight: 800; color: #ca8a04; margin-top: 4px;" id="sim-count-running">-</div>
            </div>
            <div class="card" style="margin: 0; padding: 16px; border-left: 4px solid #ef4444;">
                <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Technical Failures</div>
                <div style="font-size: 24px; font-weight: 800; color: #ef4444; margin-top: 4px;" id="sim-count-failed">-</div>
            </div>
        </div>

        <!-- Main Card Container -->
        <div class="card">
            <!-- Header with Controls -->
            <div class="card-header" style="flex-wrap: wrap; gap: 14px; margin-bottom: 20px;">
                <div>
                    <h3 class="card-title">
                        <i data-lucide="play-circle" style="color: var(--verde-primary);"></i> WorldQuant BRAIN Simulation Monitor
                    </h3>
                    <span class="card-subtitle">
                        Real-time quantitative backtest telemetry isolating technical anomalies from alpha metrics
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button class="btn btn-outline btn-sm" id="btn-manual-refresh" title="Refresh Telemetry">
                        <i data-lucide="refresh-cw" id="sim-refresh-icon"></i> Refresh
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="window.verdeUI.navigateTo('alpha-lab')">
                        <i data-lucide="plus"></i> New Alpha Lab Run
                    </button>
                </div>
            </div>

            <!-- Filters & Search Toolbar -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; padding: 12px 16px; background: #f8fafc; border-radius: var(--radius-md); border: 1px solid var(--border-light);">
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <button class="btn btn-sm ${currentFilter === 'ALL' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-all" style="font-size: 12px;">
                        All Runs
                    </button>
                    <button class="btn btn-sm ${currentFilter === 'VALID' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-valid" style="font-size: 12px;">
                        <i data-lucide="check-circle" style="width: 12px; height: 12px;"></i> Valid Metrics
                    </button>
                    <button class="btn btn-sm ${currentFilter === 'RUNNING' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-running" style="font-size: 12px;">
                        <i data-lucide="activity" style="width: 12px; height: 12px;"></i> In Progress
                    </button>
                    <button class="btn btn-sm ${currentFilter === 'FAILED' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-failed" style="font-size: 12px;">
                        <i data-lucide="alert-triangle" style="width: 12px; height: 12px;"></i> Failures / Empty
                    </button>
                </div>
                <div style="min-width: 220px; flex: 1; max-width: 320px;">
                    <input type="text" id="sim-search-input" class="form-control" placeholder="Search formula, ID, family..." value="${currentSearch}" style="padding: 6px 12px; font-size: 12.5px;" />
                </div>
            </div>

            <!-- Table Container -->
            <div id="simulations-table-container" class="table-container">
                <table class="verde-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Alpha Expression</th>
                            <th>Family</th>
                            <th>Sim Status</th>
                            <th>Portfolio</th>
                            <th>Metrics</th>
                            <th>Sharpe</th>
                            <th>Fitness</th>
                            <th>Turnover</th>
                            <th>Margin</th>
                            <th>Diagnostics & Actions</th>
                        </tr>
                    </thead>
                    <tbody id="simulations-tbody">
                        <tr>
                            <td colspan="11" style="text-align: center; padding: 40px; color: var(--text-muted);">
                                <i data-lucide="loader" class="spin" style="width: 24px; height: 24px; margin-bottom: 8px; color: var(--verde-primary);"></i>
                                <div>Loading simulation telemetry...</div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Empty State Fallback -->
            <div id="simulations-empty-state" style="display: none;"></div>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Bind Filter Buttons
    const bindFilterBtn = (id, filterVal) => {
        document.getElementById(id)?.addEventListener("click", () => {
            currentFilter = filterVal;
            ['all', 'valid', 'running', 'failed'].forEach(f => {
                const btn = document.getElementById(`filter-btn-${f}`);
                if (btn) {
                    btn.className = `btn btn-sm ${f.toUpperCase() === filterVal ? 'btn-primary' : 'btn-outline'}`;
                }
            });
            renderTableBody(cachedSims);
        });
    };

    bindFilterBtn('filter-btn-all', 'ALL');
    bindFilterBtn('filter-btn-valid', 'VALID');
    bindFilterBtn('filter-btn-running', 'RUNNING');
    bindFilterBtn('filter-btn-failed', 'FAILED');

    // Bind Search Input
    document.getElementById("sim-search-input")?.addEventListener("input", (e) => {
        currentSearch = e.target.value;
        renderTableBody(cachedSims);
    });

    // Manual Refresh Button
    document.getElementById("btn-manual-refresh")?.addEventListener("click", () => {
        refreshSimulationsData(false);
    });

    // Initial Data Fetch
    await refreshSimulationsData(false);
}
