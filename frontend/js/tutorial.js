/**
 * Onboarding Tutorial Tour Engine for VERDE Quant Platform.
 * Provides interactive step-by-step guided onboarding with spotlight highlights,
 * smart auto-positioning, smooth glassmorphism UI popovers, and page navigation.
 */

export const TUTORIAL_STEPS = [
    {
        step: 1,
        page: "dashboard",
        targetSelector: "#top-header",
        sidebarTarget: "[data-page='dashboard']",
        title: "1. Dashboard & Executive Command",
        description: "Welcome to VERDE! The Dashboard gives you a live quantitative overview of active candidate counts, yield meters, BRAIN connection status, and total research runs.",
        hint: "Click any metric card to drill down, or use the header CTA button to launch instant alpha generation.",
        position: "bottom"
    },
    {
        step: 2,
        page: "analytics",
        targetSelector: ".card-header",
        sidebarTarget: "[data-page='analytics']",
        title: "2. Analytics & Factor Exposure",
        description: "Track quantitative factor exposure, Sharpe ratio distributions, turnover curves, and cross-sectional correlations across all simulated candidate signals.",
        hint: "Notice 'Analytics' is highlighted on the sidebar menu. Use interactive charts to analyze risk-adjusted return profiles.",
        position: "bottom"
    },
    {
        step: 3,
        page: "alpha-lab",
        targetSelector: ".control-panel",
        sidebarTarget: "[data-page='alpha-lab']",
        title: "3. Alpha Lab & Hypothesis Generator",
        description: "Synthesize quantitative alpha formulas across 15 research families. Customize lookbacks, group neutralizations, and strategy ratios (Exploitation, Mutations, Gaps, Composites, Novel).",
        hint: "Notice 'Alpha Lab' is highlighted on the sidebar menu. Click 'Synthesize & Preflight' to generate candidates.",
        position: "right"
    },
    {
        step: 4,
        page: "generators",
        targetSelector: "#content-view",
        sidebarTarget: "[data-page='generators']",
        title: "4. Batch Generators & Worker Queue",
        description: "Configure background worker tasks, set execution concurrency, and monitor active preflight generation streams.",
        hint: "Notice 'Generators' is highlighted on the sidebar menu. Background workers process candidates asynchronously.",
        position: "bottom"
    },
    {
        step: 5,
        page: "families",
        targetSelector: "#content-view",
        sidebarTarget: "[data-page='families']",
        title: "5. Quantitative Research Families",
        description: "Explore formal mathematical specifications for Momentum, Mean Reversion, Fundamental Value, Quality, Volatility, Sentiment, and Technical families.",
        hint: "Inspect core hypotheses, mathematical templates, and field compatibility rules for each family.",
        position: "bottom"
    },
    {
        step: 6,
        page: "simulations",
        targetSelector: ".telemetry-ribbon-container",
        sidebarTarget: "[data-page='simulations']",
        title: "6. BRAIN Simulation Monitor & Telemetry",
        description: "Monitor real-time backtest telemetry: Total Runs, Live Pulse status, and an interactive 34%/66% Alpha Yield Distribution Meter.",
        hint: "Click filter chips (Valid Alphas, In Progress, Failures) to instantly filter the backtest table below.",
        position: "bottom"
    },
    {
        step: 7,
        page: "candidates",
        targetSelector: ".card-header",
        sidebarTarget: "[data-page='candidates']",
        title: "7. Candidate Repository & Inspector",
        description: "Inspect candidate formulas to view AST Component Hierarchy, Pre-BRAIN Quality Score breakdowns, parameter sensitivity, and structured 'WHY THIS ALPHA?' explainability.",
        hint: "Click the eye icon on any candidate row to open the Candidate Inspector drawer.",
        position: "bottom"
    },
    {
        step: 8,
        page: "quality-dashboard",
        targetSelector: "#experiments-list-container",
        sidebarTarget: "[data-page='quality-dashboard']",
        title: "8. Quality Control V2 & Preflight Gates",
        description: "Our 8-dimensional Pre-BRAIN Quality Engine evaluates syntax, field quality, temporal semantics, and redundancy risk (<65 rejected) to preserve your BRAIN budget.",
        hint: "Check the Automatic Research Gap Detection card to discover underexplored factor categories.",
        position: "right"
    },
    {
        step: 9,
        page: "pareto",
        targetSelector: "#content-view",
        sidebarTarget: "[data-page='pareto']",
        title: "9. Pareto Frontier Optimization",
        description: "Identify non-dominated alpha candidates that maximize Sharpe ratio and fitness while minimizing turnover and correlation.",
        hint: "Notice 'Pareto Lab' is highlighted on the sidebar menu. Pareto-optimal alphas represent top multi-objective candidates.",
        position: "bottom"
    },
    {
        step: 10,
        page: "memory",
        targetSelector: "#content-view",
        sidebarTarget: "[data-page='memory']",
        title: "10. Empirical Research Memory",
        description: "Leverage empirical performance matrices across families, fields, and operators to continuously guide future hypothesis generation.",
        hint: "Notice 'Research Memory' is highlighted on the sidebar menu. Memory matrices filter single-sample noise spikes.",
        position: "bottom"
    },
    {
        step: 11,
        page: "ai-lab",
        targetSelector: "#content-view",
        sidebarTarget: "[data-page='ai-lab']",
        title: "11. AI Hypothesis Co-Pilot",
        description: "Collaborate with the AI assistant to refine alpha hypotheses, fix AST expression errors, optimize lookbacks, and interpret portfolio diagnostics.",
        hint: "Type custom prompts or click suggested quantitative actions to interact with the co-pilot.",
        position: "bottom"
    },
    {
        step: 12,
        page: "brain-connection",
        targetSelector: "#content-view",
        sidebarTarget: "[data-page='brain-connection']",
        title: "12. WorldQuant BRAIN Authentication",
        description: "Manage WorldQuant BRAIN API credentials, session cookie tokens, authentication keep-alive loops, and API quota limits.",
        hint: "Ensure BRAIN status shows 'Connected' to enable live simulation submissions.",
        position: "bottom"
    },
    {
        step: 13,
        page: "logs",
        targetSelector: "#content-view",
        sidebarTarget: "[data-page='logs']",
        title: "13. Audit Logs & Telemetry",
        description: "Review structured JSON event logs, worker job status changes, diagnostic telemetry, and system exceptions.",
        hint: "Click any log entry to view full execution traces and payload details.",
        position: "bottom"
    },
    {
        step: 14,
        page: "settings",
        targetSelector: "#top-header",
        sidebarTarget: "[data-page='settings']",
        title: "14. Settings & Pro Tips",
        description: "Customize platform preferences, default lookback windows, preflight score thresholds, and notification alerts. You've completed the tour!",
        hint: "Press ⌘+F to search formulas, or click 'Guided Tour' in the top header anytime to replay.",
        position: "bottom"
    }
];

class OnboardingTutorialEngine {
    constructor() {
        this.currentStepIndex = 0;
        this.isActive = false;
    }

    async startTour() {
        this.currentStepIndex = 0;
        this.isActive = true;
        document.getElementById("tutorial-overlay")?.classList.add("active");
        await this.renderCurrentStep();
    }

    endTour() {
        this.isActive = false;
        document.getElementById("tutorial-overlay")?.classList.remove("active");
        document.querySelectorAll(".tutorial-target-active").forEach(el => el.classList.remove("tutorial-target-active"));
        document.querySelectorAll(".sidebar-nav-highlight").forEach(el => el.classList.remove("sidebar-nav-highlight"));
        localStorage.setItem("verde_tutorial_completed", "true");
    }

    async nextStep() {
        if (this.currentStepIndex < TUTORIAL_STEPS.length - 1) {
            this.currentStepIndex++;
            await this.renderCurrentStep();
        } else {
            this.endTour();
        }
    }

    async prevStep() {
        if (this.currentStepIndex > 0) {
            this.currentStepIndex--;
            await this.renderCurrentStep();
        }
    }

    async renderCurrentStep() {
        const stepData = TUTORIAL_STEPS[this.currentStepIndex];
        if (!stepData) return;

        // Auto-navigate to page if necessary
        if (window.verdeUI && typeof window.verdeUI.navigateTo === "function") {
            await window.verdeUI.navigateTo(stepData.page);
            // Short delay to allow DOM to render
            await new Promise(r => setTimeout(r, 200));
        }

        // Update Popover Text Content
        const counterEl = document.getElementById("tutorial-step-counter");
        const titleEl = document.getElementById("tutorial-step-title");
        const descEl = document.getElementById("tutorial-step-desc");
        const hintBoxEl = document.getElementById("tutorial-step-hint-box");
        const hintEl = document.getElementById("tutorial-step-hint");
        const prevBtn = document.getElementById("btn-tutorial-prev");
        const nextBtn = document.getElementById("btn-tutorial-next");

        if (counterEl) counterEl.textContent = `Step ${stepData.step} of ${TUTORIAL_STEPS.length}`;
        if (titleEl) titleEl.textContent = stepData.title;
        if (descEl) descEl.textContent = stepData.description;
        
        if (hintEl && stepData.hint) {
            if (hintBoxEl) hintBoxEl.style.display = "flex";
            hintEl.textContent = stepData.hint;
        } else if (hintBoxEl) {
            hintBoxEl.style.display = "none";
        }

        if (prevBtn) prevBtn.style.display = stepData.step === 1 ? "none" : "inline-flex";
        if (nextBtn) {
            if (stepData.step === TUTORIAL_STEPS.length) {
                nextBtn.innerHTML = `Finish Tour <i data-lucide="check-circle" style="width: 14px; height: 14px;"></i>`;
            } else {
                nextBtn.innerHTML = `Next Step <i data-lucide="arrow-right" style="width: 14px; height: 14px;"></i>`;
            }
        }

        if (window.lucide) window.lucide.createIcons();

        // Position Spotlight & Popover Card
        this.positionSpotlightAndPopover(stepData);
    }

    positionSpotlightAndPopover(stepData) {
        const spotlight = document.getElementById("tutorial-spotlight");
        const popover = document.getElementById("tutorial-popover");
        if (!spotlight || !popover) return;

        // Clear previous active target & sidebar highlight classes
        document.querySelectorAll(".tutorial-target-active").forEach(el => el.classList.remove("tutorial-target-active"));
        document.querySelectorAll(".sidebar-nav-highlight").forEach(el => el.classList.remove("sidebar-nav-highlight"));

        // Highlight sidebar target if specified
        if (stepData.sidebarTarget) {
            const sidebarEl = document.querySelector(stepData.sidebarTarget);
            if (sidebarEl) {
                sidebarEl.classList.add("sidebar-nav-highlight");
            }
        }

        let targetEl = document.querySelector(stepData.targetSelector);
        if (!targetEl) targetEl = document.body;

        if (targetEl !== document.body) {
            targetEl.classList.add("tutorial-target-active");
        }

        const rect = targetEl.getBoundingClientRect();

        // Position Spotlight box over target element
        spotlight.style.top = `${Math.max(0, rect.top - 6)}px`;
        spotlight.style.left = `${Math.max(0, rect.left - 6)}px`;
        spotlight.style.width = `${rect.width + 12}px`;
        spotlight.style.height = `${rect.height + 12}px`;

        // Calculate smart popover position
        const popoverWidth = 420;
        const popoverHeight = popover.offsetHeight || 280;
        const winWidth = window.innerWidth;
        const winHeight = window.innerHeight;
        const headerOffset = 90; // Strictly ensure popover never collides with top header!

        let popTop = rect.bottom + 16;
        let popLeft = rect.left + (rect.width / 2) - (popoverWidth / 2);

        if (stepData.position === "right") {
            popLeft = rect.right + 20;
            popTop = Math.max(headerOffset, rect.top);
            if (popLeft + popoverWidth > winWidth - 20) {
                popLeft = Math.max(20, rect.left - popoverWidth - 20);
            }
        } else if (stepData.position === "left") {
            popLeft = Math.max(20, rect.left - popoverWidth - 20);
            popTop = Math.max(headerOffset, rect.top);
        } else if (stepData.position === "top") {
            // Check if top placement stays below headerOffset
            if (rect.top - popoverHeight - 16 >= headerOffset) {
                popTop = rect.top - popoverHeight - 16;
            } else {
                // Auto-flip to bottom if top placement collides with header
                popTop = rect.bottom + 16;
            }
            popLeft = rect.left + (rect.width / 2) - (popoverWidth / 2);
        } else {
            // "bottom" default
            popTop = rect.bottom + 16;
            popLeft = rect.left + (rect.width / 2) - (popoverWidth / 2);
        }

        // Clamp popTop strictly between headerOffset (90px) and winHeight - popoverHeight - 20
        if (popTop < headerOffset) {
            popTop = headerOffset;
        }
        if (popTop + popoverHeight > winHeight - 20) {
            popTop = Math.max(headerOffset, winHeight - popoverHeight - 20);
        }

        // Clamp popLeft strictly between 20px and winWidth - popoverWidth - 20
        if (popLeft + popoverWidth > winWidth - 20) {
            popLeft = winWidth - popoverWidth - 20;
        }
        if (popLeft < 20) popLeft = 20;

        popover.style.top = `${popTop}px`;
        popover.style.left = `${popLeft}px`;
    }
}

export const onboardingEngine = new OnboardingTutorialEngine();
