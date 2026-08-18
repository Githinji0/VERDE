/**
 * VERDE Quant Research Platform - Working Documentation & Reference Module.
 * Provides interactive search, detailed indexed sections, FastExpr reference,
 * formula recipes, candidate state machine walkthroughs, and FAQ / Q&A accordions.
 */

export async function renderDocs(container) {
    container.innerHTML = `
        <div class="docs-container" style="max-width: 1200px; margin: 0 auto; padding-bottom: 40px;">
            <!-- Top Hero Banner & Search -->
            <div class="card" style="background: #ffffff; border: 1px solid var(--border-color); color: var(--text-main); padding: 28px 32px; border-radius: var(--radius-lg); margin-bottom: 24px; box-shadow: var(--shadow-card);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span class="badge" style="background: #f0fdf4; color: #16a34a; border: 1px solid rgba(34, 197, 94, 0.3); font-size: 11px; font-weight: 700;">DOCUMENTATION & WORKING GUIDE</span>
                            <span class="badge" style="background: #e0f2fe; color: #0284c7; border: 1px solid rgba(2, 132, 199, 0.3); font-size: 11px; font-weight: 700;">VERDE V2.4</span>
                        </div>
                        <h1 style="font-size: 26px; font-weight: 800; color: var(--text-main); margin: 0 0 8px 0; letter-spacing: -0.5px;">
                            VERDE Alpha Research Engine Working Manual
                        </h1>
                        <p style="font-size: 13.5px; color: var(--text-muted); margin: 0; max-width: 720px; line-height: 1.5;">
                            Complete technical reference guide explaining the 10-Stage Experiment Lifecycle, Decoupled Candidate State Machine, Pre-BRAIN Quality Engine V2, 3-Tier Redundancy Engine, FastExpr formula recipes, and FAQ.
                        </p>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-primary" onclick="window.verdeUI.openNewExperimentModal()">
                            <i data-lucide="flask-conical" style="width: 15px; height: 15px;"></i> Start Research Run
                        </button>
                    </div>
                </div>

                <!-- Instant Search & Quick Category Filter Bar -->
                <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-light); display: flex; flex-wrap: wrap; gap: 14px; align-items: center;">
                    <div style="position: relative; flex: 1; min-width: 280px;">
                        <i data-lucide="search" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: var(--text-muted);"></i>
                        <input type="text" id="docs-search-input" placeholder="Search documentation, operators (e.g. ts_rank), metrics, or FAQs..." style="width: 100%; padding: 10px 14px 10px 40px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md); color: var(--text-main); font-size: 13px; outline: none; transition: all 0.2s;" onkeyup="window.filterDocsContent(this.value)">
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px;" id="docs-category-pills">
                        <button class="pill-filter-btn active" onclick="window.filterDocsCategory('all', this)">All Topics</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('pipeline', this)">10-Stage Pipeline</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('state-machine', this)">State Machine</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('quality-v2', this)">Quality Engine V2</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('fastexpr', this)">FastExpr Reference</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('recipes', this)">Formula Recipes</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('faq', this)">FAQ & Q&A</button>
                    </div>
                </div>
            </div>

            <!-- Main Layout Grid: TOC Sidebar & Content Area -->
            <div style="display: grid; grid-template-columns: 260px 1fr; gap: 24px; align-items: start;">
                
                <!-- Left Sticky Table of Contents -->
                <div class="card" style="padding: 16px; position: sticky; top: 20px; background: #ffffff;">
                    <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                        <i data-lucide="list" style="width: 14px; height: 14px; color: var(--verde-primary);"></i> Table of Contents
                    </div>
                    <nav style="display: flex; flex-direction: column; gap: 4px; font-size: 12.5px;">
                        <a href="#doc-sec-overview" class="docs-toc-item active" onclick="window.scrollToDocSec('doc-sec-overview', this)">1. System Architecture & Vision</a>
                        <a href="#doc-sec-pipeline" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-pipeline', this)">2. 10-Stage Research Lifecycle</a>
                        <a href="#doc-sec-state-machine" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-state-machine', this)">3. Candidate State Machine</a>
                        <a href="#doc-sec-telemetry" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-telemetry', this)">4. Portfolio Empty Diagnostics</a>
                        <a href="#doc-sec-quality" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-quality', this)">5. Quality Engine V2 Benchmark</a>
                        <a href="#doc-sec-redundancy" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-redundancy', this)">6. 3-Tier Redundancy Engine</a>
                        <a href="#doc-sec-fastexpr" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-fastexpr', this)">7. FastExpr Operator Library</a>
                        <a href="#doc-sec-recipes" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-recipes', this)">8. Tested Formula Recipes</a>
                        <a href="#doc-sec-faq" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-faq', this)">9. FAQ & Q&A Section</a>
                    </nav>
                </div>

                <!-- Right Main Articles Area -->
                <div style="display: flex; flex-direction: column; gap: 24px;" id="docs-articles-wrapper">

                    <!-- Section 1: System Vision -->
                    <div class="card docs-article-card" id="doc-sec-overview" data-category="overview">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(34, 197, 94, 0.1); color: var(--verde-primary); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">1</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">1. Architecture Vision: Evaluation-First Engine</h2>
                        </div>
                        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 14px;">
                            VERDE is built to eliminate the <em>"alpha generator with a submission filter"</em> anti-pattern. Rather than randomly spitting out mathematical formulas and filtering them at the end, VERDE operates as an <strong>evaluation-first hypothesis engine</strong>.
                        </p>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 14px;">
                            <div style="padding: 14px; background: #fff1f2; border: 1px solid rgba(244, 63, 94, 0.2); border-radius: var(--radius-sm);">
                                <strong style="color: #be123c; font-size: 12.5px; display: block; margin-bottom: 6px;">❌ Legacy Generator Pattern</strong>
                                <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #9f1239; line-height: 1.5;">
                                    <li>Random string mutation without hypothesis.</li>
                                    <li>Candidate generation tightly coupled to submission gate.</li>
                                    <li>Zero root-cause analysis when portfolio yields empty positions.</li>
                                    <li>High duplicate submission rates.</li>
                                </ul>
                            </div>
                            <div style="padding: 14px; background: #f0fdf4; border: 1px solid rgba(34, 197, 94, 0.2); border-radius: var(--radius-sm);">
                                <strong style="color: #15803d; font-size: 12.5px; display: block; margin-bottom: 6px;">✓ VERDE Evaluation-First Engine</strong>
                                <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #166534; line-height: 1.5;">
                                    <li>Structured economic hypotheses (Question, Mechanism, Horizon).</li>
                                    <li>10-Stage decoupled evaluation pipeline.</li>
                                    <li>Full portfolio construction telemetry diagnostics.</li>
                                    <li>3-Tier redundancy engine (Exact, AST topology, Jaccard overlap).</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- Section 2: 10-Stage Research Lifecycle -->
                    <div class="card docs-article-card" id="doc-sec-pipeline" data-category="pipeline">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(2, 132, 199, 0.1); color: #0284c7; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">2</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">2. 10-Stage Research Experiment Lifecycle</h2>
                        </div>
                        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 14px;">
                            Every research experiment moves through 10 strict, observable stages from initial hypothesis definition to final evidence-based conclusion synthesis:
                        </p>

                        <div style="display: flex; flex-direction: column; gap: 10px; font-size: 12.5px;">
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #64748b; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 1: CREATED</strong> — Initial experiment container created with target candidate budget and target research family.
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #0284c7; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 2: HYPOTHESIS_DEFINED</strong> — Captures research question, economic mechanism, expected behavior, horizon, universe, and neutralization.
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #0284c7; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 3: GENERATING</strong> — Invokes combinatorial generator and multi-LLM synthesis to generate candidate expressions.
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #0284c7; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 4: GENERATED</strong> — Computes exact expression hash and structural AST topology hash for candidates.
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #ca8a04; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 5: VALIDATING</strong> — Executes expression AST parser to verify syntax, argument types, operator bounds, and field existence.
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #ca8a04; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 6: EVALUATING</strong> — Runs portfolio construction in simulation sandbox, tracking stage-by-stage position weights.
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #22c55e; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 7: QUALITY_REVIEW</strong> — Passes candidate through Pre-BRAIN Quality Engine V2 across 8 quality dimensions.
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #22c55e; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 8: RESEARCH_REVIEW</strong> — Evaluates 3-tier redundancy engine (Exact hash, AST topology, and Jaccard overlap > 0.85).
                            </div>
                            <div style="padding: 10px 14px; background: #f8fafc; border-left: 3px solid #22c55e; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: var(--text-main);">Stage 9: SUBMISSION_REVIEW</strong> — Qualified ELITE candidates undergo submission gate verification for production execution.
                            </div>
                            <div style="padding: 10px 14px; background: #f0fdf4; border-left: 3px solid #16a34a; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
                                <strong style="color: #15803d;">Stage 10: COMPLETED</strong> — Synthesizes evidence-based Research Conclusion and updates historical research memory.
                            </div>
                        </div>
                    </div>

                    <!-- Section 3: Candidate State Machine -->
                    <div class="card docs-article-card" id="doc-sec-state-machine" data-category="state-machine">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(168, 85, 247, 0.1); color: #a855f7; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">3</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">3. Candidate Lifecycle State Machine</h2>
                        </div>
                        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 14px;">
                            Every candidate formula progresses strictly through the following state machine:
                        </p>

                        <div style="padding: 16px; background: #1e293b; color: #f8fafc; border-radius: var(--radius-md); font-family: monospace; font-size: 11.5px; line-height: 1.7; overflow-x: auto; margin-bottom: 14px;">
[ GENERATED ]
      │
      ▼
[ VALIDATING ] ──► (Syntax/AST Fail) ──► [ INVALID ] (Rejected)
      │
      ▼ (Valid Syntax)
   [ VALID ]
      │
      ▼
[ EVALUATING ] ──► (Zero Positions) ──► [ PORTFOLIO_EMPTY ] (Rejected + Diagnosed)
      │
      ▼ (Positions Constructed)
  [ EVALUATED ]
      │
      ├──► (Quality Score < 45 or Redundant) ──► [ REJECTED ]
      ├──► (Quality Score 45.0 - 64.9)      ──► [ PROMISING ] (Retained in Memory)
      └──► (Quality Score ≥ 65.0 & Novel)   ──► [ ELITE ]
                                                  │
                                                  ▼
                                       [ SUBMISSION_PENDING ]
                                                  │
                                                  ▼
                                            [ SUBMITTED ]
                        </div>
                    </div>

                    <!-- Section 4: Portfolio Empty Diagnostics -->
                    <div class="card docs-article-card" id="doc-sec-telemetry" data-category="pipeline">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(234, 179, 8, 0.1); color: #ca8a04; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">4</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">4. Portfolio Construction Telemetry Diagnostics</h2>
                        </div>
                        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 14px;">
                            When portfolio construction produces zero positions, VERDE records stage telemetry to pinpoint the exact failure stage:
                        </p>

                        <table class="modern-table" style="font-size: 12px;">
                            <thead>
                                <tr>
                                    <th>Pipeline Stage</th>
                                    <th>Metric Tracked</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><code>RAW_DATA</code></td>
                                    <td><code>raw_count</code></td>
                                    <td>Initial universe asset count before expression evaluation.</td>
                                </tr>
                                <tr>
                                    <td><code>EXPRESSION</code></td>
                                    <td><code>nonzero_count</code></td>
                                    <td>Assets producing non-NaN signal values.</td>
                                </tr>
                                <tr>
                                    <td><code>RANKING</code></td>
                                    <td><code>ranked_count</code></td>
                                    <td>Assets with valid cross-sectional ranks.</td>
                                </tr>
                                <tr>
                                    <td><code>NEUTRALIZATION</code></td>
                                    <td><code>neutralized_count</code></td>
                                    <td>Assets remaining after group neutralization.</td>
                                </tr>
                                <tr>
                                    <td><code>TRUNCATION</code></td>
                                    <td><code>eligible_count</code></td>
                                    <td>Assets exceeding max position weight truncation limit.</td>
                                </tr>
                                <tr>
                                    <td><code>FINAL_POSITIONS</code></td>
                                    <td><code>position_count</code></td>
                                    <td>Constructed long/short portfolio positions.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Section 5: Pre-BRAIN Quality Engine V2 -->
                    <div class="card docs-article-card" id="doc-sec-quality" data-category="quality-v2">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(34, 197, 94, 0.1); color: #22c55e; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">5</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">5. Pre-BRAIN Quality Engine V2 Benchmark</h2>
                        </div>
                        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 14px;">
                            The Quality Engine evaluates candidate formulas across 8 weighted sub-dimensions to compute the Pre-BRAIN Quality Score (0 - 100):
                        </p>

                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 12px;">
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>1. Semantic Quality (20 pts):</strong> Penalizes constant signals, zero variance, or trivial expressions.
                            </div>
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>2. Expression Simplicity (15 pts):</strong> Penalizes AST depth > 4 or operator count > 6.
                            </div>
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>3. Parameter Stability (15 pts):</strong> Penalizes arbitrary magic numbers (e.g. <code>returns * 1.00034</code>).
                            </div>
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>4. Cross-Sectional Spread (15 pts):</strong> Rewards non-zero rank dispersion across universe.
                            </div>
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>5. Field Intelligence (10 pts):</strong> Rewards high-quality price, volume, and fundamental data fields.
                            </div>
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>6. Operator Hygiene (10 pts):</strong> Rewards decay linear & group neutralize operators.
                            </div>
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>7. Data Compatibility (10 pts):</strong> Verifies universe & delay alignment.
                            </div>
                            <div style="padding: 10px 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong>8. Robustness (5 pts):</strong> Verifies out-of-sample decay stability.
                            </div>
                        </div>
                    </div>

                    <!-- Section 6: 3-Tier Redundancy Engine -->
                    <div class="card docs-article-card" id="doc-sec-redundancy" data-category="quality-v2">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(225, 29, 72, 0.1); color: #e11d48; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">6</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">6. 3-Tier Redundancy Engine</h2>
                        </div>
                        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 14px;">
                            To prevent submitting redundant alpha formulas to WorldQuant BRAIN, candidates are evaluated through three levels of similarity:
                        </p>

                        <div style="display: flex; flex-direction: column; gap: 10px; font-size: 12px;">
                            <div style="padding: 12px; background: #fff1f2; border: 1px solid rgba(244, 63, 94, 0.2); border-radius: var(--radius-sm);">
                                <strong style="color: #be123c;">Tier 1: Exact Match (Score = 1.0)</strong> — Verifies <code>expression_hash</code> against all past candidates.
                            </div>
                            <div style="padding: 12px; background: #fffbe6; border: 1px solid rgba(234, 179, 8, 0.3); border-radius: var(--radius-sm);">
                                <strong style="color: #854d0e;">Tier 2: Structural AST Topology Match (Score ≥ 0.90)</strong> — Checks normalized AST tree structure (ignoring lookback window integer changes).
                            </div>
                            <div style="padding: 12px; background: #f0fdf4; border: 1px solid rgba(34, 197, 94, 0.2); border-radius: var(--radius-sm);">
                                <strong style="color: #15803d;">Tier 3: Operator & Field Overlap Similarity (Jaccard > 0.85)</strong> — Computes field and operator set overlap similarity.
                            </div>
                        </div>
                    </div>

                    <!-- Section 7: FastExpr Operator Library Reference -->
                    <div class="card docs-article-card" id="doc-sec-fastexpr" data-category="fastexpr">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(14, 165, 233, 0.1); color: #0ea5e9; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">7</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">7. FastExpr Operator Library Reference</h2>
                        </div>

                        <div class="table-container">
                            <table class="modern-table" style="font-size: 12px;">
                                <thead>
                                    <tr>
                                        <th>Operator</th>
                                        <th>Signature</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>rank</code></td>
                                        <td><code>rank(x)</code></td>
                                        <td>Cross-sectional percentile rank of <code>x</code> (0.0 to 1.0) across universe.</td>
                                    </tr>
                                    <tr>
                                        <td><code>group_neutralize</code></td>
                                        <td><code>group_neutralize(x, g)</code></td>
                                        <td>Demeans and normalizes <code>x</code> within industry group <code>g</code> (e.g. <code>subindustry</code>, <code>sector</code>).</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_rank</code></td>
                                        <td><code>ts_rank(x, d)</code></td>
                                        <td>Time-series percentile rank of current value relative to past <code>d</code> days.</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_decay_linear</code></td>
                                        <td><code>ts_decay_linear(x, d)</code></td>
                                        <td>Linearly weighted moving average of <code>x</code> over <code>d</code> days.</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_std_dev</code></td>
                                        <td><code>ts_std_dev(x, d)</code></td>
                                        <td>Rolling standard deviation of <code>x</code> over <code>d</code> days.</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_delta</code></td>
                                        <td><code>ts_delta(x, d)</code></td>
                                        <td>Difference between current value and value <code>d</code> days ago: <code>x[t] - x[t-d]</code>.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Section 8: Formula Recipes -->
                    <div class="card docs-article-card" id="doc-sec-recipes" data-category="recipes">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(34, 197, 94, 0.1); color: #22c55e; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">8</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">8. Tested Alpha Formula Recipes</h2>
                        </div>
                        <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 14px;">
                            Ready-to-use alpha expression recipes passing Quality Engine V2 benchmarks:
                        </p>

                        <div style="display: flex; flex-direction: column; gap: 14px;">
                            <div style="padding: 14px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <strong style="font-size: 13px; color: #0284c7;">Recipe 1: Subindustry-Neutralized Linear Momentum</strong>
                                    <span class="badge badge-success" style="font-size: 10px;">Quality Score: 84.9</span>
                                </div>
                                <div class="code-expr" style="padding: 10px; background: #1e293b; color: #38bdf8; font-family: monospace; font-size: 12px; border-radius: 4px; margin-bottom: 6px;">
                                    group_neutralize(rank(ts_decay_linear(returns, 10)), subindustry)
                                </div>
                                <div style="font-size: 12px; color: var(--text-muted);">
                                    Calculates 10-day linearly weighted return momentum, converts to cross-sectional rank, and neutralizes by subindustry group to eliminate sector exposure.
                                </div>
                            </div>

                            <div style="padding: 14px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <strong style="font-size: 13px; color: #0284c7;">Recipe 2: Volatility-Normalized Mean Reversion</strong>
                                    <span class="badge badge-success" style="font-size: 10px;">Quality Score: 83.9</span>
                                </div>
                                <div class="code-expr" style="padding: 10px; background: #1e293b; color: #38bdf8; font-family: monospace; font-size: 12px; border-radius: 4px; margin-bottom: 6px;">
                                    group_neutralize(rank(-ts_delta(close, 5) / (ts_std_dev(returns, 20) + 0.0001)), subindustry)
                                </div>
                                <div style="font-size: 12px; color: var(--text-muted);">
                                    Identifies short-term 5-day price pullbacks normalized by 20-day return volatility, ranking negative price shifts for mean reversion.
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Section 9: FAQ / Q&A Accordion -->
                    <div class="card docs-article-card" id="doc-sec-faq" data-category="faq">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(99, 102, 241, 0.1); color: #6366f1; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">9</div>
                            <h2 style="font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0;">9. Frequently Asked Questions (FAQ & Q&A)</h2>
                        </div>

                        <div style="display: flex; flex-direction: column; gap: 10px;" id="docs-faq-accordion">
                            
                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q: Why was my alpha candidate marked as PORTFOLIO_EMPTY?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    A <code>PORTFOLIO_EMPTY</code> state occurs when portfolio construction produces zero position weights. Click "Inspect Candidate" to view the <code>portfolio_telemetry</code> diagnostic block. It displays the <strong>LAST NONZERO STAGE</strong> and <strong>FIRST EMPTY STAGE</strong> (e.g. <code>NEUTRALIZATION</code> when all assets fall into a single industry group, or <code>TRUNCATION</code> when weights fall below threshold).
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q: What is the difference between PROMISING and ELITE candidates?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    <code>ELITE</code> candidates achieve a Pre-BRAIN Quality Score ≥ 65.0, pass all 3-tier redundancy checks, and automatically qualify for BRAIN platform submission. <code>PROMISING</code> candidates score between 45.0 and 64.9; they are retained in persistent research memory for near-miss mutation synthesis.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q: How does the 3-Tier Redundancy Engine prevent alpha overcrowding?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    Tier 1 checks exact string hashes, Tier 2 checks AST structural topologies (ignoring lookback window parameter shifts), and Tier 3 computes field/operator Jaccard similarity (> 0.85). Any duplicate is rejected to preserve portfolio uniqueness.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q: How do I initiate a new hypothesis-driven Research Experiment?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    Click "+ New Experiment" on the Dashboard or Quality Control page. Fill out the Research Title, Research Question, Core Hypothesis, Mechanism, Expected Behavior, Neutralization, and Target Candidate Budget.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q: How is the Pre-BRAIN Quality Score calculated?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    The score is a 0 - 100 weighted combination across 8 dimensions: 40% Pre-BRAIN AST & Semantic Quality + 60% Portfolio Simulation Performance (Sharpe, Fitness, Turnover, and Margin).
                                </div>
                            </div>

                        </div>
                    </div>

                </div>
            </div>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Bind helper functions to window for interactive search & navigation
    window.filterDocsContent = (query) => {
        const q = (query || "").toLowerCase().trim();
        document.querySelectorAll(".docs-article-card").forEach(card => {
            const text = card.innerText.toLowerCase();
            if (!q || text.includes(q)) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
    };

    window.filterDocsCategory = (cat, btn) => {
        document.querySelectorAll("#docs-category-pills button").forEach(b => b.className = "pill-filter-btn light");
        if (btn) btn.className = "pill-filter-btn active";

        document.querySelectorAll(".docs-article-card").forEach(card => {
            if (cat === "all" || card.dataset.category === cat) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
    };

    window.scrollToDocSec = (id, link) => {
        document.querySelectorAll(".docs-toc-item").forEach(a => a.classList.remove("active"));
        if (link) link.classList.add("active");
        const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    window.toggleFaqItem = (header) => {
        const item = header.parentElement;
        item.classList.toggle("active");
    };
}
