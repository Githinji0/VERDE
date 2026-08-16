import { api } from './api.js';
import { renderBadge, showToast, updateUserUI, syncBrainStatus } from './utils.js';

let liveLogs = [];

function appendLog(severity, event, message) {
    const time = new Date().toLocaleTimeString();
    liveLogs.unshift({ time, severity, event, message });
    if (liveLogs.length > 20) liveLogs.pop();
    updateLiveLogContainer();
}

function updateLiveLogContainer() {
    const logEl = document.getElementById("brain-live-terminal-logs");
    if (!logEl) return;
    if (liveLogs.length === 0) {
        logEl.innerHTML = `<div style="color: #6b7280; font-style: italic; font-size: 12px;">Ready. Click 'Test Auth Ping' or 'Save & Connect' to capture live connection diagnostics.</div>`;
        return;
    }
    logEl.innerHTML = liveLogs.map(l => {
        const color = l.severity === 'SUCCESS' ? '#4ade80' : l.severity === 'ERROR' ? '#f87171' : l.severity === 'WARN' ? '#facc15' : '#93c5fd';
        return `
            <div style="font-family: 'Consolas', monospace; font-size: 11.5px; line-height: 1.6; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 4px 0;">
                <span style="color: #64748b;">[${l.time}]</span>
                <span style="color: ${color}; font-weight: 700; margin: 0 4px;">[${l.event}]</span>
                <span style="color: #e2e8f0;">${l.message}</span>
            </div>
        `;
    }).join('');
}

export async function renderBrainConnection(container) {
    container.innerHTML = `
        <div style="text-align: center; padding: 60px; color: var(--text-muted);">
            <i data-lucide="loader" class="spin" style="width: 28px; height: 28px; margin-bottom: 12px; color: var(--verde-primary);"></i>
            <div style="font-weight: 700; font-size: 14px;">Loading BRAIN Connection...</div>
        </div>
    `;
    if (window.lucide) window.lucide.createIcons();

    try {
        const health = await api.getBrainHealth();

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="plug"></i> WorldQuant BRAIN Connection & Diagnostics</h3>
                        <span class="card-subtitle">Connect your researcher credentials. Password and tokens are encrypted via AES-256 at rest.</span>
                    </div>
                    <div>${renderBadge(health.connected ? "CONNECTED" : "DISCONNECTED")}</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <!-- Credentials Form Card -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 15px; margin-bottom: 18px;"><i data-lucide="key"></i> Account Credentials</h4>
                    
                    <div class="form-group">
                        <label>BRAIN Email / Username</label>
                        <input type="email" id="brain-email-input" class="form-control" placeholder="researcher@worldquantbrain.com" autocomplete="username" />
                    </div>

                    <div class="form-group">
                        <label>BRAIN Password</label>
                        <input type="password" id="brain-pass-input" class="form-control" placeholder="••••••••••••" autocomplete="current-password" />
                    </div>

                    <div class="form-group">
                        <label>Environment</label>
                        <select id="brain-env-select" class="form-control">
                            <option value="PROD">Production (api.worldquantbrain.com)</option>
                            <option value="SIMULATION">Simulation Sandbox</option>
                        </select>
                    </div>

                    <div style="display: flex; gap: 12px; margin-top: 24px; flex-wrap: wrap;">
                        <button class="btn btn-outline" id="btn-test-brain-auth">
                            <i data-lucide="activity"></i> Test Auth Ping
                        </button>
                        <button class="btn btn-primary" id="btn-connect-brain">
                            <i data-lucide="check-circle"></i> Save & Connect
                        </button>
                    </div>
                </div>

                <!-- Live Diagnostic Details Card -->
                <div class="card">
                    <h4 class="card-title" style="font-size: 15px; margin-bottom: 18px;"><i data-lucide="shield-check"></i> Connection Status & Security</h4>
                    
                    <div style="display: flex; flex-direction: column; gap: 12px; font-size: 13px;">
                        <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid var(--border-light);">
                            <strong>API Endpoint:</strong> <code>${health.brain_api_url}</code>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid var(--border-light);">
                            <strong>Connection State:</strong> ${renderBadge(health.status)}
                        </div>
                        <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid var(--border-light);">
                            <strong>Last Tested:</strong> <span>${health.last_tested || 'Never'}</span>
                        </div>
                        <div style="padding: 12px; background-color: var(--verde-pale); border-radius: var(--radius-md); border: 1px solid var(--verde-pale-border);">
                            <span style="font-weight: 700; color: var(--verde-dark);">Client-Side Isolation:</span>
                            <p style="margin-top: 4px; color: var(--text-muted); font-size: 12px; line-height: 1.4;">
                                Your browser never directly exposes credentials to external networks. All requests and encrypted sessions are managed by the VERDE backend.
                            </p>
                        </div>
                    </div>

                    ${health.connected ? `
                        <button class="btn btn-outline" id="btn-disconnect-brain" style="margin-top: 20px; color: var(--status-danger); border-color: var(--status-danger);">
                            <i data-lucide="log-out"></i> Disconnect Account
                        </button>
                    ` : ''}
                </div>
            </div>

            <!-- Live Diagnostic Terminal Logs in UI -->
            <div class="card card-dark" style="margin-top: 20px;">
                <div class="card-header" style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 12px;">
                    <div>
                        <h4 class="card-title" style="color: #ffffff; font-size: 14px;">
                            <i data-lucide="terminal" style="color: var(--verde-accent);"></i> Live Connection & Auth Diagnostics
                        </h4>
                        <span class="card-subtitle" style="color: #94a3b8;">Real-time network handshake and error stream</span>
                    </div>
                    <button class="btn-action-icon" style="background: rgba(255,255,255,0.1); color: #fff; border-color: rgba(255,255,255,0.2);" onclick="document.getElementById('brain-live-terminal-logs').innerHTML = ''; liveLogs = [];" title="Clear Console">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
                <div id="brain-live-terminal-logs" style="max-height: 180px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 12px; border-radius: var(--radius-sm);">
                    <!-- Logs populated here -->
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();
        updateLiveLogContainer();

        // Test Auth Handler
        document.getElementById("btn-test-brain-auth")?.addEventListener("click", async () => {
            const email = document.getElementById("brain-email-input").value.trim();
            const password = document.getElementById("brain-pass-input").value;

            if (!email || !password) {
                showToast("Please enter both email and password.", "warning");
                appendLog("WARN", "VALIDATION", "Email and password fields are required.");
                return;
            }

            appendLog("INFO", "AUTH_START", `Initiating authentication ping to https://api.worldquantbrain.com/authentication for user: ${email.substring(0,3)}***`);

            try {
                const res = await api.testBrainAuth({ email, password });
                if (res.status === "BRAIN_AUTH_SUCCESS") {
                    appendLog("SUCCESS", "AUTH_200", `Authentication verified successfully. Latency: ${res.latency_ms}ms.`);
                    showToast(`Authentication Test Passed (${res.latency_ms}ms)!`, "success");
                } else {
                    appendLog("ERROR", `STATUS_${res.status_code || 401}`, `${res.message} (Latency: ${res.latency_ms || 0}ms)`);
                    showToast(`Auth Failed: ${res.message}`, "error");
                }
            } catch (err) {
                appendLog("ERROR", "NETWORK_ERROR", err.message);
                showToast(`Test error: ${err.message}`, "error");
            }
        });

        // Save & Connect Handler
        document.getElementById("btn-connect-brain")?.addEventListener("click", async () => {
            const email = document.getElementById("brain-email-input").value.trim();
            const password = document.getElementById("brain-pass-input").value;
            const env = document.getElementById("brain-env-select").value;

            if (!email || !password) {
                showToast("Please enter both email and password.", "warning");
                appendLog("WARN", "VALIDATION", "Email and password are required to connect.");
                return;
            }

            appendLog("INFO", "CONNECT_START", `Connecting account: ${email.substring(0,3)}*** (Environment: ${env})`);

            try {
                const res = await api.connectBrain({ email, password, environment: env });
                if (res.success) {
                    appendLog("SUCCESS", "CONNECT_SUCCESS", `BRAIN account connected! Session encrypted in AES-256 vault.`);
                    showToast("BRAIN account connected successfully!", "success");
                    updateUserUI(email);
                    await syncBrainStatus();
                    renderBrainConnection(container);
                } else {
                    appendLog("ERROR", `CONNECT_FAILURE`, res.message);
                    showToast(`Connection failed: ${res.message}`, "error");
                }
            } catch (err) {
                appendLog("ERROR", "CONNECT_ERROR", err.message);
                showToast(`Error: ${err.message}`, "error");
            }
        });

        // Disconnect Handler
        document.getElementById("btn-disconnect-brain")?.addEventListener("click", async () => {
            try {
                await api.disconnectBrain();
                appendLog("INFO", "DISCONNECTED", "BRAIN session cleared and disconnected.");
                showToast("BRAIN account disconnected.", "info");
                updateUserUI("Lead Quant");
                await syncBrainStatus();
                renderBrainConnection(container);
            } catch (err) {
                appendLog("ERROR", "DISCONNECT_ERROR", err.message);
                showToast(`Error: ${err.message}`, "error");
            }
        });

    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error loading BRAIN connection view: ${err.message}</div>`;
    }
}
