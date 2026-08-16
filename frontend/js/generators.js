import { api } from './api.js';
import { showToast } from './utils.js';

export async function renderGenerators(container) {
    const families = await api.getFamilies();

    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <div>
                    <h3 class="card-title"><i data-lucide="cpu"></i> High-Throughput Research Generator</h3>
                    <span class="card-subtitle">Batch candidate synthesis with controlled stream allocations (70% Proven / 20% Explored / 10% Novel)</span>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 16px;">
                <div class="form-group">
                    <label>Target Research Family</label>
                    <select id="gen-family-select" class="form-control">
                        <option value="ALL">All Families (Round-Robin)</option>
                        ${families.map(f => `<option value="${f.code}">${f.name} (${f.code})</option>`).join('')}
                    </select>
                </div>

                <div class="form-group">
                    <label>Candidates per Family</label>
                    <input type="number" id="gen-batch-size" class="form-control" value="10" min="1" max="50" />
                </div>
            </div>

            <div class="card" style="background-color: var(--bg-main); margin-top: 16px;">
                <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 12px; text-transform: uppercase;">Stream Allocation Rules</h4>
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 180px;">
                        <span style="font-size: 13px; font-weight: 600; color: var(--verde-primary);">PROVEN (70%)</span>
                        <p style="font-size: 12px; color: var(--text-muted);">Historically high-survival alpha structures & proven standard templates.</p>
                    </div>
                    <div style="flex: 1; min-width: 180px;">
                        <span style="font-size: 13px; font-weight: 600; color: var(--status-warning);">EXPLORED (20%)</span>
                        <p style="font-size: 12px; color: var(--text-muted);">Lookback mutations, smoothing filters, and volatility normalizers.</p>
                    </div>
                    <div style="flex: 1; min-width: 180px;">
                        <span style="font-size: 13px; font-weight: 600; color: var(--status-info);">NOVEL (10%)</span>
                        <p style="font-size: 12px; color: var(--text-muted);">Cross-family factor pairings and exploratory structural combinations.</p>
                    </div>
                </div>
            </div>

            <button class="btn btn-primary" id="btn-start-batch-gen" style="margin-top: 16px;">
                <i data-lucide="play"></i> Execute Batch Synthesis
            </button>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    document.getElementById("btn-start-batch-gen").addEventListener("click", async () => {
        const family = document.getElementById("gen-family-select").value;
        const count = parseInt(document.getElementById("gen-batch-size").value) || 10;
        const btn = document.getElementById("btn-start-batch-gen");

        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader" class="spin"></i> Generating Candidates...`;
        if (window.lucide) window.lucide.createIcons();

        try {
            const targets = family === "ALL" ? families.map(f => f.code) : [family];
            let totalGen = 0;

            for (const f of targets) {
                const res = await api.generateCandidates({ family_code: f, count: Math.ceil(count / targets.length) });
                totalGen += res.generated_count;
            }

            showToast(`Batch synthesis complete: ${totalGen} candidates created across ${targets.length} families.`, "success");
            window.verdeUI.navigateTo("candidates");
        } catch (err) {
            showToast(`Batch synthesis error: ${err.message}`, "error");
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<i data-lucide="play"></i> Execute Batch Synthesis`;
            if (window.lucide) window.lucide.createIcons();
        }
    });
}
