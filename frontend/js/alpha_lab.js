import { api } from './api.js';
import { formatMetric, renderBadge, showToast } from './utils.js';

export async function renderAlphaLab(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Alpha Lab...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const families = await api.getFamilies();

        container.innerHTML = `
            <div class="alpha-lab-grid">
                <!-- Control Panel -->
                <div class="control-panel">
                    <h3 class="card-title" style="margin-bottom: 16px;"><i data-lucide="sliders"></i> Generator Setup</h3>
                    
                    <div class="form-group">
                        <label>Research Family (17 Available)</label>
                        <select id="lab-family-select" class="form-control">
                            ${families.map(f => `<option value="${f.code}">${f.name} (${f.code})</option>`).join('')}
                        </select>
                    </div>

                    <div class="card" style="padding: 12px; background-color: var(--bg-main); margin-bottom: 16px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Core Hypothesis:</div>
                        <div id="family-hypothesis-display" style="font-size: 13px; color: var(--text-main); margin-top: 4px; line-height: 1.4;">
                            ${families[0]?.core_hypothesis || ''}
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Generation Batch Count</label>
                        <input type="number" id="lab-batch-count" class="form-control" value="5" min="1" max="25" />
                    </div>

                    <div class="form-group">
                        <label>Allocation Stream</label>
                        <div style="display: flex; gap: 8px; font-size: 12px; font-weight: 600;">
                            <span class="badge badge-success">70% Proven</span>
                            <span class="badge badge-warning">20% Explored</span>
                            <span class="badge badge-info">10% Novel</span>
                        </div>
                    </div>

                    <button class="btn btn-primary" id="btn-run-generation" style="width: 100%; margin-top: 8px;">
                        <i data-lucide="sparkles"></i> Synthesize & Preflight
                    </button>
                </div>

                <!-- Generation Stream & Preflight Results -->
                <div>
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <h3 class="card-title"><i data-lucide="cpu"></i> Active Generation Stream</h3>
                                <span class="card-subtitle">Candidates validated by deterministic preflight engine</span>
                            </div>
                        </div>

                        <div id="lab-results-container">
                            <div style="text-align: center; padding: 40px; color: var(--text-muted);">
                                <i data-lucide="flask-conical" style="width: 32px; height: 32px; margin-bottom: 8px;"></i>
                                <p>Select a research family and click <strong>Synthesize & Preflight</strong> to generate hypothesis-driven expressions.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // Bind family select change
        const selectEl = document.getElementById("lab-family-select");
        const hypDisplay = document.getElementById("family-hypothesis-display");
        selectEl.addEventListener("change", () => {
            const selected = families.find(f => f.code === selectEl.value);
            if (selected) {
                hypDisplay.textContent = selected.core_hypothesis;
            }
        });

        // Bind generation button
        const genBtn = document.getElementById("btn-run-generation");
        genBtn.addEventListener("click", async () => {
            const familyCode = selectEl.value;
            const count = parseInt(document.getElementById("lab-batch-count").value) || 5;

            genBtn.disabled = true;
            genBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Synthesizing...`;
            if (window.lucide) window.lucide.createIcons();

            try {
                const res = await api.generateCandidates({
                    family_code: familyCode,
                    count: count
                });

                renderGeneratedCandidates(res.candidates);
                showToast(`Synthesized ${res.generated_count} candidates for ${familyCode}.`, "success");
            } catch (err) {
                showToast(`Generation failed: ${err.message}`, "error");
            } finally {
                genBtn.disabled = false;
                genBtn.innerHTML = `<i data-lucide="sparkles"></i> Synthesize & Preflight`;
                if (window.lucide) window.lucide.createIcons();
            }
        });

    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}

function renderGeneratedCandidates(candidates) {
    const container = document.getElementById("lab-results-container");
    if (!container) return;

    if (!candidates || candidates.length === 0) {
        container.innerHTML = `<div style="text-align: center; padding: 20px;">No candidates generated.</div>`;
        return;
    }

    let rowsHtml = candidates.map(c => {
        const pf = c.preflight;
        return `
            <tr>
                <td><div class="code-expr">${c.expression}</div></td>
                <td><span class="badge badge-info">${c.priority_bucket}</span></td>
                <td>${renderBadge(pf.decision)}</td>
                <td>${(pf.compatibility_score * 100).toFixed(0)}%</td>
                <td>${(pf.constant_signal_risk * 100).toFixed(0)}%</td>
                <td>${pf.complexity_score}</td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-primary btn-sm" onclick="window.verdeUI.simulateCandidate('${c.id}')" ${pf.decision === 'REJECT' ? 'disabled title="Preflight rejected"' : ''}>
                            <i data-lucide="play"></i> Simulate
                        </button>
                        <button class="btn btn-outline btn-sm" onclick="window.verdeUI.openCandidateModal('${c.id}')">
                            <i data-lucide="eye"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    container.innerHTML = `
        <div class="table-container">
            <table class="verde-table">
                <thead>
                    <tr>
                        <th>Alpha Expression</th>
                        <th>Stream</th>
                        <th>Preflight</th>
                        <th>Temporal Compat</th>
                        <th>Constant Risk</th>
                        <th>Complexity</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();
}
