import { api } from './api.js';
import { renderBadge, showToast } from './utils.js';

export async function renderBrainConnection(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading BRAIN Connection...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const health = await api.getBrainHealth();

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="plug"></i> WorldQuant BRAIN Connection & Authentication</h3>
                        <span class="card-subtitle">Connect your researcher account. Credentials are encrypted via AES-256 and never logged or exposed.</span>
                    </div>
                    <div>${renderBadge(health.connected ? "CONNECTED" : "DISCONNECTED")}</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <!-- Connection Form -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 16px;"><i data-lucide="key"></i> Account Credentials</h4>
                    
                    <div class="form-group">
                        <label>BRAIN Email / Username</label>
                        <input type="email" id="brain-email-input" class="form-control" placeholder="researcher@worldquantbrain.com" />
                    </div>

                    <div class="form-group">
                        <label>BRAIN Password</label>
                        <input type="password" id="brain-pass-input" class="form-control" placeholder="••••••••••••" />
                    </div>

                    <div class="form-group">
                        <label>Environment</label>
                        <select id="brain-env-select" class="form-control">
                            <option value="PROD">Production (api.worldquantbrain.com)</option>
                            <option value="SIMULATION">Simulation Sandbox</option>
                        </select>
                    </div>

                    <div style="display: flex; gap: 10px; margin-top: 20px;">
                        <button class="btn btn-outline" id="btn-test-brain-auth">
                            <i data-lucide="activity"></i> Test Auth Ping
                        </button>
                        <button class="btn btn-primary" id="btn-connect-brain">
                            <i data-lucide="check-circle"></i> Save & Connect
                        </button>
                    </div>
                </div>

                <!-- Status & Security Diagnostics -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 14px; margin-bottom: 16px;"><i data-lucide="shield-check"></i> Security & Diagnostics</h4>
                    
                    <div style="display: flex; flex-direction: column; gap: 12px; font-size: 13px;">
                        <div>
                            <strong>API Endpoint:</strong> <code>${health.brain_api_url}</code>
                        </div>
                        <div>
                            <strong>Connection Status:</strong> ${renderBadge(health.status)}
                        </div>
                        <div>
                            <strong>Last Tested:</strong> ${health.last_tested || 'Never'}
                        </div>
                        <div style="padding: 12px; background-color: var(--verde-pale); border-radius: var(--radius-sm); border: 1px solid var(--verde-pale-border);">
                            <span style="font-weight: 700; color: var(--verde-dark);">Client-Side Isolation:</span>
                            <p style="margin-top: 4px; color: var(--text-muted);">
                                Your browser never directly calls WorldQuant API. All requests and sessions are managed securely by the VERDE backend server.
                            </p>
                        </div>
                    </div>

                    ${health.connected ? `
                        <button class="btn btn-danger btn-sm" id="btn-disconnect-brain" style="margin-top: 20px;">
                            <i data-lucide="log-out"></i> Disconnect Account
                        </button>
                    ` : ''}
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // Test Auth
        document.getElementById("btn-test-brain-auth")?.addEventListener("click", async () => {
            const email = document.getElementById("brain-email-input").value.trim();
            const password = document.getElementById("brain-pass-input").value;

            if (!email || !password) {
                showToast("Please enter both email and password.", "warning");
                return;
            }

            try {
                const res = await api.testBrainAuth({ email, password });
                if (res.status === "BRAIN_AUTH_SUCCESS") {
                    showToast(`Authentication Test Passed (${res.latency_ms}ms)!`, "success");
                } else {
                    showToast(`Auth Failed: ${res.message}`, "error");
                }
            } catch (err) {
                showToast(`Test error: ${err.message}`, "error");
            }
        });

        // Save & Connect
        document.getElementById("btn-connect-brain")?.addEventListener("click", async () => {
            const email = document.getElementById("brain-email-input").value.trim();
            const password = document.getElementById("brain-pass-input").value;
            const env = document.getElementById("brain-env-select").value;

            if (!email || !password) {
                showToast("Please enter both email and password.", "warning");
                return;
            }

            try {
                const res = await api.connectBrain({ email, password, environment: env });
                if (res.success) {
                    showToast("BRAIN account connected successfully!", "success");
                    renderBrainConnection(container);
                } else {
                    showToast(`Connection failed: ${res.message}`, "error");
                }
            } catch (err) {
                showToast(`Error: ${err.message}`, "error");
            }
        });

        // Disconnect
        document.getElementById("btn-disconnect-brain")?.addEventListener("click", async () => {
            try {
                await api.disconnectBrain();
                showToast("BRAIN account disconnected.", "info");
                renderBrainConnection(container);
            } catch (err) {
                showToast(`Error: ${err.message}`, "error");
            }
        });

    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
