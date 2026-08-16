import { api } from './api.js';
import { showToast } from './utils.js';

export async function renderSettings(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Settings...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const s = await api.getSettings();
        const targets = s.validation_targets;
        const alloc = s.priority_allocation;

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="settings"></i> Validation Targets & Research Configuration</h3>
                        <span class="card-subtitle">Configure thresholds for candidate readiness, near-miss routing, and stream allocation ratios</span>
                    </div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <!-- Validation Targets -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 16px;"><i data-lucide="target"></i> Candidate Readiness Criteria</h4>
                    
                    <div class="form-group">
                        <label>Minimum Sharpe Ratio</label>
                        <input type="number" step="0.05" id="set-min-sharpe" class="form-control" value="${targets.min_sharpe}" />
                    </div>

                    <div class="form-group">
                        <label>Minimum Fitness</label>
                        <input type="number" step="0.05" id="set-min-fitness" class="form-control" value="${targets.min_fitness}" />
                    </div>

                    <div class="form-group">
                        <label>Maximum Turnover</label>
                        <input type="number" step="0.05" id="set-max-turnover" class="form-control" value="${targets.max_turnover}" />
                    </div>

                    <div class="form-group">
                        <label>Minimum Margin (bps)</label>
                        <input type="number" step="0.5" id="set-min-margin" class="form-control" value="${targets.min_margin_bps}" />
                    </div>
                </div>

                <!-- Priority Allocation -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 16px;"><i data-lucide="pie-chart"></i> Priority Allocation Stream Ratios</h4>
                    
                    <div class="form-group">
                        <label>Proven Stream Ratio (Standard: 0.70)</label>
                        <input type="number" step="0.05" id="set-proven-ratio" class="form-control" value="${alloc.PROVEN}" />
                    </div>

                    <div class="form-group">
                        <label>Explored Stream Ratio (Standard: 0.20)</label>
                        <input type="number" step="0.05" id="set-explored-ratio" class="form-control" value="${alloc.EXPLORED}" />
                    </div>

                    <div class="form-group">
                        <label>Novel Stream Ratio (Standard: 0.10)</label>
                        <input type="number" step="0.05" id="set-novel-ratio" class="form-control" value="${alloc.NOVEL}" />
                    </div>

                    <div class="form-group" style="margin-top: 20px;">
                        <button class="btn btn-primary" id="btn-save-settings" style="width: 100%;">
                            <i data-lucide="save"></i> Save Configuration
                        </button>
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        document.getElementById("btn-save-settings")?.addEventListener("click", async () => {
            const body = {
                min_sharpe: parseFloat(document.getElementById("set-min-sharpe").value),
                min_fitness: parseFloat(document.getElementById("set-min-fitness").value),
                max_turnover: parseFloat(document.getElementById("set-max-turnover").value),
                min_margin_bps: parseFloat(document.getElementById("set-min-margin").value),
                proven_ratio: parseFloat(document.getElementById("set-proven-ratio").value),
                explored_ratio: parseFloat(document.getElementById("set-explored-ratio").value),
                novel_ratio: parseFloat(document.getElementById("set-novel-ratio").value),
                ai_enabled: s.flags.ai_enabled,
                brain_debug: s.flags.brain_debug
            };

            try {
                await api.updateSettings(body);
                showToast("System validation settings updated successfully!", "success");
            } catch (err) {
                showToast(`Failed to update settings: ${err.message}`, "error");
            }
        });

    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
