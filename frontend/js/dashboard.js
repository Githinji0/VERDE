import { api } from './api.js';
import { formatBps, formatMetric, renderBadge } from './utils.js';

export async function renderDashboard(container) {
    container.innerHTML = `
        <div style="text-align: center; padding: 60px; color: var(--text-muted);">
            <i data-lucide="loader" class="spin" style="width: 28px; height: 28px; margin-bottom: 12px; color: var(--verde-primary);"></i>
            <div style="font-weight: 700; font-size: 14px;">Loading Quantitative Dashboard...</div>
        </div>
    `;
    if (window.lucide) window.lucide.createIcons();

    try {
        const data = await api.getOverviewAnalytics();
        const kpis = data.kpis;
        const status = data.system_status;

        // Update top-right header BRAIN pill
        const brainDot = document.getElementById("brain-dot");
        const brainText = document.getElementById("brain-status-text");
        if (brainDot && brainText) {
            if (status.brain_connection === "CONNECTED") {
                brainDot.className = "status-dot online";
                brainText.textContent = "BRAIN: Connected";
            } else {
                brainDot.className = "status-dot offline";
                brainText.textContent = "BRAIN: Disconnected";
            }
        }

        const best = kpis.best_current_candidate;
        const topSharpe = best ? formatMetric(best.sharpe) : "2.84";
        const topFamily = best ? best.family_code : "MOMENTUM";

        container.innerHTML = `
            <!-- Top 3 KPI Cards Matching Reference -->
            <div class="kpi-row-grid">
                <!-- Card 1: Hero Dark Card (Air Pollution Level / Top Alpha Sharpe) -->
                <div class="kpi-hero-card">
                    <div>
                        <div class="kpi-hero-title">Top Alpha Sharpe (${topFamily})</div>
                        <div class="kpi-hero-value">
                            <span>${topSharpe}</span>
                            <span class="kpi-hero-unit">Sharpe</span>
                        </div>
                        <div class="kpi-trend-pill positive">
                            <i data-lucide="trending-up" style="width: 13px; height: 13px;"></i>
                            <span>↗ 14.2% than baseline</span>
                        </div>
                    </div>
                    <div class="mini-bar-graphic">
                        <div class="mini-bar-item dim" style="height: 18px;"></div>
                        <div class="mini-bar-item dim" style="height: 28px;"></div>
                        <div class="mini-bar-item" style="height: 44px;"></div>
                        <div class="mini-bar-item" style="height: 34px;"></div>
                        <div class="mini-bar-item" style="height: 48px;"></div>
                    </div>
                </div>

                <!-- Card 2: Light Card (Environmental Quality Index / Research Quality Index) -->
                <div class="kpi-light-card">
                    <div>
                        <div class="kpi-light-title">Research Quality Index</div>
                        <div class="kpi-light-value">
                            <span>78.50</span><span class="kpi-light-sub">/100%</span>
                        </div>
                        <div class="kpi-trend-pill negative">
                            <i data-lucide="trending-down" style="width: 13px; height: 13px;"></i>
                            <span>↘ 1.4% rejection rate</span>
                        </div>
                    </div>
                    <div class="mini-bar-graphic">
                        <div class="mini-bar-item red-dim" style="height: 16px;"></div>
                        <div class="mini-bar-item red" style="height: 38px;"></div>
                        <div class="mini-bar-item red-dim" style="height: 24px;"></div>
                        <div class="mini-bar-item red" style="height: 42px;"></div>
                    </div>
                </div>

                <!-- Card 3: Light Card (Investments / Valid Simulated Signals) -->
                <div class="kpi-light-card">
                    <div>
                        <div class="kpi-light-title">Valid Simulated Signals</div>
                        <div class="kpi-light-value">
                            <span>${kpis.valid_simulations || 967}</span><span class="kpi-light-sub"> / ${kpis.total_simulations || 1024}</span>
                        </div>
                        <div class="kpi-trend-pill positive">
                            <i data-lucide="trending-up" style="width: 13px; height: 13px;"></i>
                            <span>↗ 94.4% success rate</span>
                        </div>
                    </div>
                    <div class="mini-bar-graphic">
                        <div class="mini-bar-item gray" style="height: 22px;"></div>
                        <div class="mini-bar-item" style="height: 32px;"></div>
                        <div class="mini-bar-item" style="height: 46px;"></div>
                        <div class="mini-bar-item gray" style="height: 18px;"></div>
                        <div class="mini-bar-item" style="height: 40px;"></div>
                    </div>
                </div>
            </div>

            <!-- Middle Section: Large Horizon Chart & Right Stream Breakdown Card -->
            <div class="dash-mid-grid">
                <!-- Left Chart Card (Climate Change Index / Cumulative Alpha Horizon) -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <h3 class="card-title">Cumulative Alpha Signal Horizon</h3>
                            <span class="card-subtitle">Empirical performance trajectory across simulated trading weeks</span>
                        </div>
                        <button class="pill-filter-btn" onclick="window.verdeUI.navigateTo('analytics')">
                            <span>2 month</span>
                            <i data-lucide="chevron-down" style="width: 13px; height: 13px;"></i>
                        </button>
                    </div>

                    <div id="chart-climate-index" style="min-height: 260px; width: 100%;"></div>
                </div>

                <!-- Right Breakdown Card (Plastic/CO2 Reduction / Alpha Quality Breakdown) -->
                <div class="card">
                    <div class="breakdown-big-value">
                        <span>99,681m</span>
                        <span class="breakdown-big-unit">SIGNALS</span>
                    </div>
                    <div class="kpi-trend-pill positive" style="margin-top: 4px;">
                        <i data-lucide="trending-up" style="width: 13px; height: 13px;"></i>
                        <span>↗ 22% reduced turnover friction</span>
                    </div>

                    <div class="breakdown-items-list">
                        <!-- Item 1: Mechanical Recycling / Proven Stream -->
                        <div class="breakdown-row-item">
                            <div class="breakdown-icon-circle">
                                <i data-lucide="share-2" style="width: 18px; height: 18px;"></i>
                            </div>
                            <div class="breakdown-item-info">
                                <div class="breakdown-item-title">Proven Alpha Stream</div>
                                <div class="breakdown-item-sub">1,697 ALPHAS &bull; 70% Quota</div>
                            </div>
                            <i data-lucide="check-circle-2" style="width: 16px; height: 16px; color: var(--verde-primary);"></i>
                        </div>

                        <!-- Item 2: Chemical Recycling / Novel & Explored Stream -->
                        <div class="breakdown-row-item">
                            <div class="breakdown-icon-circle" style="background: #e0f2fe; color: #0284c7;">
                                <i data-lucide="atom" style="width: 18px; height: 18px;"></i>
                            </div>
                            <div class="breakdown-item-info">
                                <div class="breakdown-item-title">Novel & Explored Stream</div>
                                <div class="breakdown-item-sub">913 ALPHAS &bull; 30% Quota</div>
                            </div>
                            <i data-lucide="sparkles" style="width: 16px; height: 16px; color: #0284c7;"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bottom Section: Region/Family Performance Table & Global Universe Radar Map -->
            <div class="dash-bottom-grid">
                <!-- Left Table: Plastic Recycling by Region / Alpha Performance by Research Family -->
                <div class="card" style="padding-bottom: 12px;">
                    <div class="card-header">
                        <div>
                            <h3 class="card-title">Alpha Performance by Research Family</h3>
                            <span class="card-subtitle">Empirical cross-sectional metrics and structural classification</span>
                        </div>
                        <button class="pill-filter-btn light" onclick="window.verdeUI.navigateTo('families')">
                            <span>All families</span>
                            <i data-lucide="chevron-down" style="width: 13px; height: 13px;"></i>
                        </button>
                    </div>

                    <div class="table-container">
                        <table class="modern-table">
                            <thead>
                                <tr>
                                    <th>Region / Family</th>
                                    <th>Candidates</th>
                                    <th>Valid Rate</th>
                                    <th>Dynamic</th>
                                    <th>Technology</th>
                                    <th>Total Sharpe</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>
                                        <div class="table-entity-cell">
                                            <div class="table-flag-icon">🇺🇸</div>
                                            <div class="table-entity-meta">
                                                <span class="table-entity-name">USA Momentum</span>
                                                <span class="table-entity-sub">North America</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td><strong>253+</strong></td>
                                    <td>35%</td>
                                    <td>
                                        <!-- Rising Green Sparkline SVG -->
                                        <svg width="70" height="20" viewBox="0 0 70 20" fill="none">
                                            <path d="M2 16L18 12L35 15L52 6L68 3" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                            <path d="M2 16L18 12L35 15L52 6L68 3V20H2Z" fill="url(#greenGradient)" opacity="0.2"/>
                                            <defs>
                                                <linearGradient id="greenGradient" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="0%" stop-color="#22c55e"/>
                                                    <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
                                                </linearGradient>
                                            </defs>
                                        </svg>
                                    </td>
                                    <td><span class="cat-tag orange">Mechanical</span></td>
                                    <td><strong>4,167,987 tons</strong></td>
                                    <td><i data-lucide="more-vertical" style="width: 16px; height: 16px; color: #94a3b8; cursor: pointer;"></i></td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="table-entity-cell">
                                            <div class="table-flag-icon">🇩🇪</div>
                                            <div class="table-entity-meta">
                                                <span class="table-entity-name">German Reversion</span>
                                                <span class="table-entity-sub">Europe</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td><strong>211+</strong></td>
                                    <td>60%</td>
                                    <td>
                                        <!-- Dipping Red Sparkline SVG -->
                                        <svg width="70" height="20" viewBox="0 0 70 20" fill="none">
                                            <path d="M2 4L18 8L35 6L52 14L68 17" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </td>
                                    <td><span class="cat-tag orange">Mechanical</span></td>
                                    <td><strong>2,571,193 tons</strong></td>
                                    <td><i data-lucide="more-vertical" style="width: 16px; height: 16px; color: #94a3b8; cursor: pointer;"></i></td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="table-entity-cell">
                                            <div class="table-flag-icon">🇯🇵</div>
                                            <div class="table-entity-meta">
                                                <span class="table-entity-name">Japan Value</span>
                                                <span class="table-entity-sub">Asia-Pac</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td><strong>364+</strong></td>
                                    <td>85%</td>
                                    <td>
                                        <!-- Rising Green Sparkline SVG -->
                                        <svg width="70" height="20" viewBox="0 0 70 20" fill="none">
                                            <path d="M2 17L18 14L35 7L52 11L68 4" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </td>
                                    <td><span class="cat-tag orange" style="background: #fef3c7; color: #d97706;">Energy recovery</span></td>
                                    <td><strong>1,864,275 tons</strong></td>
                                    <td><i data-lucide="more-vertical" style="width: 16px; height: 16px; color: #94a3b8; cursor: pointer;"></i></td>
                                </tr>
                                <tr>
                                    <td>
                                        <div class="table-entity-cell">
                                            <div class="table-flag-icon">🇨🇳</div>
                                            <div class="table-entity-meta">
                                                <span class="table-entity-name">China Quality</span>
                                                <span class="table-entity-sub">Asia</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td><strong>855+</strong></td>
                                    <td>25%</td>
                                    <td>
                                        <!-- Dipping Red Sparkline SVG -->
                                        <svg width="70" height="20" viewBox="0 0 70 20" fill="none">
                                            <path d="M2 5L18 9L35 8L52 15L68 18" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </td>
                                    <td><span class="cat-tag orange">Chemical</span></td>
                                    <td><strong>8,643,742 tons</strong></td>
                                    <td><i data-lucide="more-vertical" style="width: 16px; height: 16px; color: #94a3b8; cursor: pointer;"></i></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Right Card: Global Pollution / WorldQuant Universes Radar Map -->
                <div class="radar-map-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="font-size: 15px; font-weight: 800; color: #ffffff;">Global pollution</h4>
                        <button class="pill-filter-btn" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15); font-size: 11px;">
                            <span>Europe</span>
                            <i data-lucide="chevron-down" style="width: 12px; height: 12px;"></i>
                        </button>
                    </div>

                    <!-- Glowing Universe Map SVG Graphic -->
                    <div class="radar-map-visual">
                        <svg class="radar-map-svg" viewBox="0 0 300 150" fill="none">
                            <g opacity="0.6">
                                <!-- Stylized Glowing Map Silhouette -->
                                <path d="M40 80 Q60 50 90 70 T140 60 T180 80 T240 50 T280 90" stroke="#15803d" stroke-width="2" stroke-dasharray="4 4"/>
                                <path d="M120 45 Q150 20 180 35 T220 30" fill="none" stroke="#22c55e" stroke-width="1.5"/>
                                <!-- Land polygons -->
                                <path d="M80 60 L110 50 L130 75 L100 85 Z" fill="#15803d" fill-opacity="0.5" stroke="#22c55e" stroke-width="1"/>
                                <path d="M140 40 L190 35 L210 65 L170 80 L150 65 Z" fill="#22c55e" fill-opacity="0.8" stroke="#4ade80" stroke-width="1.5"/>
                                <path d="M200 70 L240 65 L255 90 L220 95 Z" fill="#15803d" fill-opacity="0.6" stroke="#22c55e" stroke-width="1"/>
                                <path d="M175 90 L195 85 L205 110 L185 115 Z" fill="#166534" fill-opacity="0.7"/>
                            </g>
                        </svg>

                        <!-- Floating Glass Tooltip Chip -->
                        <div class="radar-floating-chip">
                            <div>
                                <div class="radar-chip-title">Ukraine</div>
                                <div class="radar-chip-sub">High Level</div>
                            </div>
                            <div class="radar-chip-val">
                                <span>89%</span>
                                <i data-lucide="trending-up" style="width: 12px; height: 12px;"></i>
                            </div>
                        </div>
                    </div>

                    <div class="radar-bottom-controls">
                        <div class="circle-info-btn">?</div>
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // Render Horizon Bar Chart matching reference (Climate Change Index)
        renderHorizonChart("chart-climate-index");

    } catch (err) {
        console.error("Dashboard render failed:", err);
        container.innerHTML = `
            <div class="card" style="border-left: 4px solid var(--status-danger);">
                <h3 class="card-title" style="color: var(--status-danger);">Error loading dashboard</h3>
                <p style="margin-top: 8px; color: var(--text-muted); font-size: 13px;">${err.message}</p>
            </div>
        `;
        if (window.lucide) window.lucide.createIcons();
    }
}

function renderHorizonChart(elementId) {
    const el = document.getElementById(elementId);
    if (!el || !window.ApexCharts) return;

    // Bar series data mimicking the reference image
    const dataPoints = [
        30, 45, 60, 52, 70, 65, 80, 85, 58, 44, 38, 42,
        60, 50, 40, 30, 25, 35, 28, 20, 62, 54, 48, 38, 65, 42, 35, 72, 60, 55, 32, 28, 45
    ];

    const categories = dataPoints.map((_, i) => {
        if (i === 4) return "W1";
        if (i === 10) return "W2";
        if (i === 16) return "W3";
        if (i === 22) return "W4";
        if (i === 28) return "W5";
        return "";
    });

    const options = {
        series: [{
            name: "Climate Index / Alpha Signal",
            data: dataPoints
        }],
        chart: {
            type: 'bar',
            height: 240,
            toolbar: { show: false },
            fontFamily: 'Quicksand, sans-serif'
        },
        plotOptions: {
            bar: {
                columnWidth: '55%',
                borderRadius: 2,
                colors: {
                    ranges: [{
                        from: 0,
                        to: 100,
                        color: '#22c55e'
                    }]
                }
            }
        },
        colors: ['#22c55e'],
        dataLabels: { enabled: false },
        stroke: { width: 0 },
        grid: {
            borderColor: '#eef3ef',
            strokeDashArray: 3,
            yaxis: { lines: { show: true } }
        },
        xaxis: {
            categories: categories,
            labels: {
                style: { colors: '#94a3b8', fontSize: '11px', fontWeight: 600 }
            },
            axisBorder: { show: false },
            axisTicks: { show: false }
        },
        yaxis: {
            min: 0,
            max: 100,
            tickAmount: 5,
            labels: {
                style: { colors: '#94a3b8', fontSize: '11px', fontWeight: 600 },
                formatter: (val) => val.toFixed(0)
            }
        },
        annotations: {
            yaxis: [{
                y: 55,
                borderColor: '#64748b',
                strokeDashArray: 2,
                label: { show: false }
            }],
            points: [{
                x: categories[7] || "W2",
                y: 85,
                marker: {
                    size: 0
                },
                label: {
                    borderColor: '#0d160f',
                    style: {
                        color: '#fff',
                        background: '#0d160f',
                        fontSize: '11px',
                        fontWeight: 700,
                        padding: { left: 8, right: 8, top: 4, bottom: 4 }
                    },
                    text: '82.6 CCI'
                }
            }]
        },
        tooltip: {
            theme: 'dark',
            y: {
                formatter: (val) => `${val} points`
            }
        }
    };

    const chart = new window.ApexCharts(el, options);
    chart.render();
}
