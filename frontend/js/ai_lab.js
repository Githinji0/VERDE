import { api } from './api.js';
import { renderBadge, showToast } from './utils.js';

export async function renderAILab(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading AI Lab...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const provRes = await api.getAIProviders();
        const providers = provRes.providers;
        const families = await api.getFamilies();

        let providerCards = providers.map(p => `
            <div class="card" style="margin: 0; padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong>${p.display_name}</strong>
                    ${renderBadge(p.status)}
                </div>
                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">
                    Key Hint: <code>${p.key_hint || 'Not Configured'}</code>
                </div>
                <div style="display: flex; gap: 8px;">
                    <input type="password" id="key-input-${p.name}" class="form-control" placeholder="Enter API Key" style="font-size: 12px; padding: 4px 8px;" />
                    <button class="btn btn-primary btn-sm btn-val-key" data-provider="${p.name}">
                        Validate
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="sparkles"></i> AI Research Assistant Lab (Optional)</h3>
                        <span class="card-subtitle">AI generates qualitative hypotheses and mutation ideas. All expressions remain strictly subject to deterministic preflight validation.</span>
                    </div>
                </div>
            </div>

            <!-- Provider Management -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px;">
                ${providerCards}
            </div>

            <!-- AI Hypothesis Workbench -->
            <div class="card">
                <h4 class="card-title" style="font-size: 14px; margin-bottom: 12px;"><i data-lucide="compass"></i> Hypothesis Ideation Assistant</h4>
                <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px;">
                    <div class="form-group" style="flex: 1; min-width: 200px; margin: 0;">
                        <label>AI Model Provider</label>
                        <select id="ai-provider-select" class="form-control">
                            ${providers.map(p => `<option value="${p.name}">${p.display_name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group" style="flex: 1; min-width: 200px; margin: 0;">
                        <label>Target Research Family</label>
                        <select id="ai-family-select" class="form-control">
                            ${families.map(f => `<option value="${f.code}">${f.name} (${f.code})</option>`).join('')}
                        </select>
                    </div>
                    <div style="display: flex; align-items: flex-end;">
                        <button class="btn btn-primary" id="btn-generate-ai-hypothesis">
                            <i data-lucide="sparkles"></i> Consult AI Assistant
                        </button>
                    </div>
                </div>

                <div id="ai-hypothesis-output">
                    <div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">
                        Select a provider and research family to generate structured hypotheses.
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // Key Validation Listeners
        document.querySelectorAll(".btn-val-key").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const provider = e.target.dataset.provider;
                const inputEl = document.getElementById(`key-input-${provider}`);
                const keyVal = inputEl ? inputEl.value.trim() : "";

                if (!keyVal) {
                    showToast("Please enter an API key to validate.", "warning");
                    return;
                }

                btn.disabled = true;
                btn.textContent = "Validating...";

                try {
                    const res = await api.validateAIKey(provider, keyVal);
                    if (res.status === "AI_KEY_VALID") {
                        showToast(`API Key for ${provider} validated and encrypted successfully!`, "success");
                        renderAILab(container);
                    } else {
                        showToast(`Validation failed: ${res.message}`, "error");
                        btn.disabled = false;
                        btn.textContent = "Validate";
                    }
                } catch (err) {
                    showToast(`Error: ${err.message}`, "error");
                    btn.disabled = false;
                    btn.textContent = "Validate";
                }
            });
        });

        // AI Generation Listener
        document.getElementById("btn-generate-ai-hypothesis")?.addEventListener("click", async () => {
            const provider = document.getElementById("ai-provider-select").value;
            const family = document.getElementById("ai-family-select").value;
            const outEl = document.getElementById("ai-hypothesis-output");
            const btn = document.getElementById("btn-generate-ai-hypothesis");

            btn.disabled = true;
            btn.innerHTML = `<i data-lucide="loader" class="spin"></i> Consulting AI...`;
            if (window.lucide) window.lucide.createIcons();

            try {
                const res = await api.generateAIHypothesis(provider, family);
                const hyps = res.hypotheses || [];

                outEl.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 12px;">
                        ${hyps.map(h => `
                            <div class="card" style="margin: 0; padding: 14px; background-color: var(--verde-pale); border-color: var(--verde-pale-border);">
                                <div style="font-weight: 700; color: var(--verde-dark); font-size: 14px;">${h.title}</div>
                                <p style="font-size: 13px; color: var(--text-main); margin: 6px 0;">${h.rationale}</p>
                                <div style="display: flex; gap: 16px; font-size: 12px; color: var(--text-muted);">
                                    <span><strong>Fields:</strong> ${h.suggested_fields.join(', ')}</span>
                                    <span><strong>Operators:</strong> ${h.suggested_operators.join(', ')}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } catch (err) {
                outEl.innerHTML = `<div style="color: var(--status-danger);">AI Consultation failed: ${err.message}</div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<i data-lucide="sparkles"></i> Consult AI Assistant`;
                if (window.lucide) window.lucide.createIcons();
            }
        });

    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
