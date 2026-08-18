import { api } from './api.js';
import { renderDashboard } from './dashboard.js';
import { renderAlphaLab } from './alpha_lab.js';
import { renderGenerators } from './generators.js';
import { renderSimulations } from './simulations.js';
import { renderCandidates, populateCandidateModal } from './candidates.js';
import { renderAnalytics } from './analytics.js';
import { renderParetoLab } from './pareto_lab.js';
import { renderResearchMemory } from './memory.js';
import { renderAILab } from './ai_lab.js';
import { renderBrainConnection } from './brain_connection.js';
import { renderLogs, populateDiagnosticModal } from './logs.js';
import { renderSettings } from './settings.js';
import { renderQualityDashboard } from './quality_dashboard.js';
import { onboardingEngine } from './tutorial.js';
import { showToast, loadSavedUserUI, updateUserUI, syncBrainStatus, renderTabSkeleton } from './utils.js';

// Route Definitions
const routes = {
    'dashboard': { title: 'Dashboard', render: renderDashboard },
    'alpha-lab': { title: 'Alpha Lab', render: renderAlphaLab },
    'generators': { title: 'Generators', render: renderGenerators },
    'families': { title: 'Research Families', render: renderAlphaLab },
    'simulations': { title: 'Simulations', render: renderSimulations },
    'candidates': { title: 'Candidates', render: renderCandidates },
    'quality-dashboard': { title: 'Quality Control V2', render: renderQualityDashboard },
    'analytics': { title: 'Analytics', render: renderAnalytics },
    'pareto': { title: 'Pareto Lab', render: renderParetoLab },
    'memory': { title: 'Research Memory', render: renderResearchMemory },
    'ai-lab': { title: 'AI Assistant', render: renderAILab },
    'brain-connection': { title: 'BRAIN Connection', render: renderBrainConnection },
    'logs': { title: 'Audit Logs', render: renderLogs },
    'settings': { title: 'Settings', render: renderSettings }
};

let currentPage = 'dashboard';

async function navigateTo(page) {
    if (!routes[page]) page = 'dashboard';
    currentPage = page;

    // Update active class in sidebar
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.page === page) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Update title
    const titleEl = document.getElementById('current-page-title');
    if (titleEl) {
        titleEl.textContent = routes[page].title;
    }

    // Render page
    const container = document.getElementById('content-view');
    if (container) {
        // Render tab loading skeleton before fetching route content
        renderTabSkeleton(container);

        try {
            await routes[page].render(container);
        } catch (err) {
            console.error(`Render error on page ${page}:`, err);
            container.innerHTML = `
                <div class="card" style="border-left: 4px solid var(--status-danger);">
                    <h3 class="card-title" style="color: var(--status-danger);">Failed to render ${routes[page].title}</h3>
                    <p style="margin-top: 8px; color: var(--text-muted); font-size: 13px;">${err.message}</p>
                    <button class="btn btn-outline btn-sm" style="margin-top: 12px;" onclick="window.verdeUI.navigateTo('${page}')">Retry</button>
                </div>
            `;
        }
        if (window.lucide && typeof window.lucide.createIcons === "function") {
            try { window.lucide.createIcons(); } catch (e) { console.warn(e); }
        }
    }
}

// Global UI Object
window.verdeUI = {
    navigateTo,
    startTutorialTour: () => onboardingEngine.startTour(),
    nextTutorialStep: () => onboardingEngine.nextStep(),
    prevTutorialStep: () => onboardingEngine.prevStep(),
    endTutorialTour: () => onboardingEngine.endTour(),
    openCandidateModal: (id) => {
        const modal = document.getElementById("candidate-modal");
        if (modal) {
            modal.classList.add("active");
            populateCandidateModal(id);
        }
    },
    closeCandidateModal: () => {
        const modal = document.getElementById("candidate-modal");
        if (modal) modal.classList.remove("active");
    },
    openDiagnosticModal: (id) => {
        const modal = document.getElementById("diagnostic-modal");
        if (modal) {
            modal.classList.add("active");
            populateDiagnosticModal(id);
        }
    },
    closeDiagnosticModal: () => {
        const modal = document.getElementById("diagnostic-modal");
        if (modal) modal.classList.remove("active");
    },
    openNewExperimentModal: () => {
        const modal = document.getElementById("new-experiment-modal");
        if (modal) {
            modal.classList.add("active");
            if (window.lucide) window.lucide.createIcons();
            const titleInput = document.getElementById("exp-title-input");
            if (titleInput) {
                titleInput.focus();
                titleInput.select();
            }
        }
    },
    closeNewExperimentModal: () => {
        const modal = document.getElementById("new-experiment-modal");
        if (modal) modal.classList.remove("active");
    },
    openExperimentInspectorModal: (id) => {
        const modal = document.getElementById("experiment-inspector-modal");
        if (modal) {
            modal.classList.add("active");
            populateExperimentInspectorModal(id);
        }
    },
    closeExperimentInspectorModal: () => {
        const modal = document.getElementById("experiment-inspector-modal");
        if (modal) modal.classList.remove("active");
    },
    submitNewExperiment: async () => {
        const title = document.getElementById("exp-title-input")?.value?.trim();
        const hypothesis = document.getElementById("exp-hypothesis-input")?.value?.trim();
        const research_question = document.getElementById("exp-question-input")?.value?.trim();
        const mechanism = document.getElementById("exp-mechanism-input")?.value?.trim();
        const expected_behavior = document.getElementById("exp-behavior-input")?.value?.trim();
        const family_code = document.getElementById("exp-family-select")?.value || "MOMENTUM";
        const neutralization = document.getElementById("exp-neutralization-select")?.value || "SUBINDUSTRY";
        const target_budget = parseInt(document.getElementById("exp-budget-input")?.value || "20", 10);

        if (!title) {
            showToast("Please enter an experiment title.", "warning");
            return;
        }

        const submitBtn = document.getElementById("btn-submit-exp");
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Running Evaluation Pipeline...`;
        }

        try {
            await api.post("/api/research/experiments", {
                title: title,
                hypothesis: hypothesis || "Hypothesis-driven quantitative alpha research run",
                research_question: research_question || "Does signal provide persistent cross-sectional information?",
                mechanism: mechanism || "Cross-sectional alpha mechanism",
                expected_behavior: expected_behavior || "Positive continuation",
                family_code: family_code,
                neutralization: neutralization,
                target_budget: target_budget
            });
            showToast(`Experiment '${title}' initiated and evaluated through multi-stage pipeline!`, "success");
            window.verdeUI.closeNewExperimentModal();

            // Refresh Quality Dashboard lists if on quality-dashboard page
            try {
                const { loadExperimentsList, loadQualitySummary } = await import('./quality_dashboard.js');
                await loadExperimentsList();
                await loadQualitySummary();
            } catch (err) {
                // Ignore if not on quality dashboard page
            }
        } catch (err) {
            showToast(`Error starting experiment: ${err.message}`, "error");
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i data-lucide="flask-conical" style="width: 15px; height: 15px;"></i> Initiate Research Pipeline`;
                if (window.lucide) window.lucide.createIcons();
            }
        }
    },
    openLogDetailModal: (id) => {
        const modal = document.getElementById("diagnostic-modal");
        if (modal) {
            modal.classList.add("active");
            populateDiagnosticModal(id);
        }
    },
    simulateCandidate: async (id) => {
        try {
            showToast("Submitting candidate simulation to BRAIN...", "info");
            const res = await api.simulateCandidate(id, {});
            showToast(`Simulation ${res.status}: BRAIN ID ${res.brain_sim_id || 'Pending'}`, "success");
            navigateTo('simulations');
        } catch (err) {
            showToast(`Simulation submission failed: ${err.message}`, "error");
        }
    },
    pollSimulation: async (id) => {
        try {
            const res = await api.pollSimulation(id);
            showToast(`Simulation ${id.substring(0,8)} status: ${res.status}`, "info");
            const curPage = window.location.hash.replace('#', '') || 'dashboard';
            if (curPage === 'simulations') {
                const { refreshSimulationsData } = await import('./simulations.js');
                await refreshSimulationsData(true);
            } else {
                navigateTo('simulations');
            }
        } catch (err) {
            showToast(`Poll failed: ${err.message}`, "error");
        }
    },
    pollSimulationInline: async (id) => {
        const btn = document.getElementById(`btn-poll-${id}`);
        const icon = btn ? btn.querySelector("i, svg") : null;
        if (icon) icon.classList.add("spin");
        try {
            const res = await api.pollSimulation(id);
            showToast(`Simulation ${id.substring(0,8)} status: ${res.status}`, "info");
            const { refreshSimulationsData } = await import('./simulations.js');
            await refreshSimulationsData(true);
        } catch (err) {
            showToast(`Poll failed: ${err.message}`, "error");
        } finally {
            if (icon) icon.classList.remove("spin");
        }
    },
    handleQuickSearch: (query) => {
        if (!query) return;
        query = query.toLowerCase();
        if (query.includes('sim') || query.includes('run')) navigateTo('simulations');
        else if (query.includes('cand') || query.includes('expr')) navigateTo('candidates');
        else if (query.includes('gen') || query.includes('batch')) navigateTo('generators');
        else if (query.includes('fam') || query.includes('mom')) navigateTo('families');
        else if (query.includes('pareto')) navigateTo('pareto');
        else if (query.includes('ai') || query.includes('chat')) navigateTo('ai-lab');
        else if (query.includes('brain') || query.includes('auth')) navigateTo('brain-connection');
        else if (query.includes('log')) navigateTo('logs');
    },
    showSplashScreen: () => {
        const splash = document.getElementById("verde-splash-screen");
        if (splash) {
            splash.style.display = "flex";
            splash.classList.remove("fade-out");
            runSplashBootSequence();
        }
    },
    dismissSplashScreen: () => dismissSplash()
};

function dismissSplash() {
    const splash = document.getElementById("verde-splash-screen");
    if (!splash || splash.style.display === "none") return;
    splash.classList.add("fade-out");
    setTimeout(() => {
        splash.style.display = "none";
    }, 250);
}

function runSplashBootSequence() {
    const splash = document.getElementById("verde-splash-screen");
    if (!splash || splash.style.display === "none") return;

    // Hard safety timeout: guaranteed dismiss within 350ms
    setTimeout(dismissSplash, 350);
}

async function populateExperimentInspectorModal(experimentId) {
    const body = document.getElementById("experiment-inspector-modal-body");
    if (!body) return;

    body.innerHTML = `
        <div style="text-align: center; padding: 30px;">
            <i data-lucide="loader" class="spin" style="width: 24px; height: 24px; color: var(--verde-primary);"></i>
            <p style="margin-top: 8px; font-size: 13px; color: var(--text-muted);">Loading experiment details and evaluation pipeline telemetry...</p>
        </div>
    `;
    if (window.lucide) window.lucide.createIcons();

    try {
        const data = await api.get(`/api/research/experiments/${experimentId}`);
        const exp = data.experiment;
        const hyp = data.structured_hypothesis || {};
        const funnel = data.funnel || {};
        const cands = data.candidates || [];
        const conc = data.research_conclusion || {};

        body.innerHTML = `
            <!-- Experiment Header & Hypothesis -->
            <div style="padding: 16px 18px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md); margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h2 style="font-size: 17px; font-weight: 800; color: var(--text-main); margin: 0;">${exp.title}</h2>
                        <div style="font-size: 12.5px; font-weight: 700; color: #0284c7; margin-top: 4px;">Question: "${hyp.research_question || exp.hypothesis}"</div>
                    </div>
                    <span class="badge ${exp.status === 'COMPLETED' ? 'badge-success' : 'badge-info'}" style="font-size: 11px; font-weight: 700;">${exp.status}</span>
                </div>
                <div style="margin-top: 10px; font-size: 12.5px; color: var(--text-muted); line-height: 1.5; border-top: 1px solid var(--border-light); padding-top: 8px;">
                    <strong>Core Hypothesis:</strong> ${hyp.hypothesis || exp.hypothesis}
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 14px; margin-top: 10px; font-size: 11.5px; color: var(--text-muted);">
                    <span>Family: <strong style="color: var(--text-main);">${exp.family_code}</strong></span>
                    <span>Mechanism: <strong style="color: var(--text-main);">${hyp.mechanism || 'N/A'}</strong></span>
                    <span>Behavior: <strong style="color: var(--text-main);">${hyp.expected_behavior || 'N/A'}</strong></span>
                    <span>Neutralization: <strong style="color: var(--text-main);">${hyp.neutralization || 'SUBINDUSTRY'}</strong></span>
                </div>
            </div>

            <!-- Candidate Funnel Breakdown -->
            <div style="margin-bottom: 20px;">
                <h4 style="font-size: 11.5px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Evaluation Candidate Funnel</h4>
                <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; text-align: center; font-size: 11px;">
                    <div style="background: #f1f5f9; padding: 10px 4px; border-radius: var(--radius-sm);">
                        <span style="color: var(--text-muted); display: block; font-size: 9.5px;">GENERATED</span>
                        <strong style="font-size: 15px;">${funnel.generated || 0}</strong>
                    </div>
                    <div style="background: #f1f5f9; padding: 10px 4px; border-radius: var(--radius-sm);">
                        <span style="color: var(--text-muted); display: block; font-size: 9.5px;">VALIDATED</span>
                        <strong style="font-size: 15px; color: #0284c7;">${funnel.validated || 0}</strong>
                    </div>
                    <div style="background: #f1f5f9; padding: 10px 4px; border-radius: var(--radius-sm);">
                        <span style="color: var(--text-muted); display: block; font-size: 9.5px;">EVALUATED</span>
                        <strong style="font-size: 15px; color: #0284c7;">${funnel.evaluated || 0}</strong>
                    </div>
                    <div style="background: #f1f5f9; padding: 10px 4px; border-radius: var(--radius-sm);">
                        <span style="color: #ef4444; display: block; font-size: 9.5px;">REJECTED</span>
                        <strong style="font-size: 15px; color: #ef4444;">${funnel.rejected || 0}</strong>
                    </div>
                    <div style="background: #f1f5f9; padding: 10px 4px; border-radius: var(--radius-sm);">
                        <span style="color: #eab308; display: block; font-size: 9.5px;">PROMISING</span>
                        <strong style="font-size: 15px; color: #ca8a04;">${funnel.promising || 0}</strong>
                    </div>
                    <div style="background: #f1f5f9; padding: 10px 4px; border-radius: var(--radius-sm);">
                        <span style="color: #22c55e; display: block; font-size: 9.5px;">ELITE</span>
                        <strong style="font-size: 15px; color: #22c55e;">${funnel.elite || 0}</strong>
                    </div>
                    <div style="background: #f1f5f9; padding: 10px 4px; border-radius: var(--radius-sm);">
                        <span style="color: #22c55e; display: block; font-size: 9.5px;">SUBMITTED</span>
                        <strong style="font-size: 15px; color: #22c55e;">${funnel.submitted || 0}</strong>
                    </div>
                </div>
            </div>

            <!-- Synthesized Research Conclusion -->
            ${conc.key_finding ? `
                <div style="padding: 14px 16px; background: #f0fdf4; border: 1px solid rgba(34, 197, 94, 0.3); border-radius: var(--radius-md); margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <strong style="font-size: 13px; color: #15803d;"><i data-lucide="brain-circuit" style="width: 15px; height: 15px; display: inline;"></i> Research Conclusion & Synthesis</strong>
                        <span class="badge" style="background: #dcfce7; color: #15803d; font-size: 10px;">${conc.confidence || 'EVIDENCE_BASED'}</span>
                    </div>
                    <p style="font-size: 12px; color: #166534; margin: 0 0 6px 0; line-height: 1.45;">${conc.key_finding}</p>
                    <div style="font-size: 12px; font-weight: 700; color: #15803d;">Decision: ${conc.research_decision}</div>
                </div>
            ` : ''}

            <!-- Candidate Evaluation Table -->
            <div>
                <h4 style="font-size: 11.5px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Evaluated Candidates (${cands.length})</h4>
                <div class="table-container" style="max-height: 240px; overflow-y: auto;">
                    <table class="modern-table">
                        <thead>
                            <tr>
                                <th>Candidate ID</th>
                                <th>Expression</th>
                                <th>Lifecycle State</th>
                                <th>Quality Score</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${cands.map(c => `
                                <tr>
                                    <td><code style="font-size: 11px; font-weight: 700;">${c.id.substring(0, 8)}</code></td>
                                    <td><code style="font-size: 11px; color: var(--text-main);">${c.expression}</code></td>
                                    <td><span class="badge ${c.lifecycle_state === 'ELITE' || c.lifecycle_state === 'SUBMITTED' ? 'badge-success' : (c.lifecycle_state === 'PROMISING' ? 'badge-warning' : 'badge-danger')}" style="font-size: 10px;">${c.lifecycle_state}</span></td>
                                    <td><strong>${c.alpha_quality_score != null ? c.alpha_quality_score.toFixed(1) : 'N/A'}</strong></td>
                                    <td>
                                        <button class="btn btn-outline btn-sm" style="padding: 3px 8px; font-size: 11px;" onclick="window.verdeUI.openCandidateModal('${c.id}')">Inspect Candidate</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        if (window.lucide) window.lucide.createIcons();
    } catch (e) {
        console.error("Error populating experiment inspector:", e);
        body.innerHTML = `<div style="color: var(--status-danger); padding: 20px;">Failed to load experiment inspector: ${e.message}</div>`;
    }
}

function initApp() {
    // Run Splash Screen Telemetry Sequence
    runSplashBootSequence();

    // Bind navigation clicks
    document.querySelectorAll(".nav-item").forEach(item => {
        item.addEventListener("click", () => {
            const page = item.dataset.page;
            if (page) {
                window.location.hash = page;
                navigateTo(page);
            }
        });
    });

    // Hash change handler
    window.addEventListener("hashchange", () => {
        const page = window.location.hash.replace('#', '');
        navigateTo(page);
    });

    // Bind header status pill click
    document.getElementById("header-brain-status")?.addEventListener("click", () => {
        window.location.hash = "brain-connection";
        navigateTo("brain-connection");
    });

    // Close modals when clicking on backdrop overlay
    document.querySelectorAll(".modal-overlay").forEach(overlay => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) {
                overlay.classList.remove("active");
            }
        });
    });

    // Close modals on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            document.querySelectorAll(".modal-overlay.active").forEach(modal => {
                modal.classList.remove("active");
            });
        }
    });

    // Check initial hash or load dashboard
    const initialPage = window.location.hash.replace('#', '') || 'dashboard';
    navigateTo(initialPage);

    // Initialize user profile UI from cache and API
    loadSavedUserUI();
    syncBrainStatus();
    setInterval(syncBrainStatus, 6000);
}

// Immediate execution check
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
} else {
    initApp();
}
