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
import { showToast, loadSavedUserUI, updateUserUI, syncBrainStatus } from './utils.js';

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
    submitNewExperiment: async () => {
        const title = document.getElementById("exp-title-input")?.value?.trim();
        const hypothesis = document.getElementById("exp-hypothesis-input")?.value?.trim();
        const family_code = document.getElementById("exp-family-select")?.value || "MOMENTUM";
        const target_budget = parseInt(document.getElementById("exp-budget-input")?.value || "20", 10);

        if (!title) {
            showToast("Please enter an experiment title.", "warning");
            return;
        }

        const submitBtn = document.getElementById("btn-submit-exp");
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Starting...`;
        }

        try {
            await api.post("/api/research/experiments", {
                title: title,
                hypothesis: hypothesis || "Hypothesis-driven quantitative alpha research run",
                family_code: family_code,
                target_budget: target_budget
            });
            showToast(`Experiment '${title}' started successfully!`, "success");
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
                submitBtn.innerHTML = `<i data-lucide="flask-conical" style="width: 15px; height: 15px;"></i> Start Experiment`;
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
    }
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
