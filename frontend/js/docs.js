/**
 * VERDE Quant Research Platform - Exhaustive Working Documentation & Reference Module.
 * Provides interactive search, TOC section scrolling, 10-stage lifecycle,
 * candidate state machine, portfolio diagnostics, Quality Engine V2 benchmark,
 * 3-tier redundancy engine, FastExpr operator library, code recipes, and FAQ accordion.
 */

export async function renderDocs(container) {
    container.innerHTML = `
        <div class="docs-container" style="max-width: 1240px; margin: 0 auto; padding-bottom: 50px;">
            <!-- Top Hero Banner & Search -->
            <div class="card" style="background: #ffffff; border: 1px solid var(--border-color); color: var(--text-main); padding: 28px 32px; border-radius: var(--radius-lg); margin-bottom: 24px; box-shadow: var(--shadow-card);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span class="badge" style="background: #f0fdf4; color: #16a34a; border: 1px solid rgba(34, 197, 94, 0.3); font-size: 11px; font-weight: 700;">DOCUMENTATION & EXHAUSTIVE MANUAL</span>
                            <span class="badge" style="background: #e0f2fe; color: #0284c7; border: 1px solid rgba(2, 132, 199, 0.3); font-size: 11px; font-weight: 700;">VERDE V2.4 ARCHITECTURE</span>
                        </div>
                        <h1 style="font-size: 26px; font-weight: 800; color: var(--text-main); margin: 0 0 8px 0; letter-spacing: -0.5px;">
                            VERDE Quantitative Alpha Research Engine Manual
                        </h1>
                        <p style="font-size: 13.5px; color: var(--text-muted); margin: 0; max-width: 760px; line-height: 1.55;">
                            Exhaustive technical documentation detailing the 10-Stage Experiment Lifecycle, Decoupled Candidate State Machine, Portfolio Construction Telemetry Diagnostics, Pre-BRAIN Quality Engine V2, 3-Tier Redundancy Engine, FastExpr Syntax & Operator Library, Tested Formula Recipes, and FAQ.
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
                        <input type="text" id="docs-search-input" placeholder="Search documentation, operators (e.g. ts_rank), metrics, state machines, or FAQs..." style="width: 100%; padding: 10px 14px 10px 40px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md); color: var(--text-main); font-size: 13px; outline: none; transition: all 0.2s;" onkeyup="window.filterDocsContent(this.value)">
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px;" id="docs-category-pills">
                        <button class="pill-filter-btn active" onclick="window.filterDocsCategory('all', this)">All Topics</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('pipeline', this)">10-Stage Pipeline</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('state-machine', this)">State Machine</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('telemetry', this)">Telemetry Diagnostics</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('quality-v2', this)">Quality Engine V2</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('redundancy', this)">3-Tier Redundancy</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('fastexpr', this)">FastExpr Reference</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('recipes', this)">Formula Recipes</button>
                        <button class="pill-filter-btn light" onclick="window.filterDocsCategory('faq', this)">FAQ & Q&A</button>
                    </div>
                </div>
            </div>

            <!-- Main Layout Grid: TOC Sidebar & Content Area -->
            <div style="display: grid; grid-template-columns: 280px 1fr; gap: 24px; align-items: start;">
                
                <!-- Left Sticky Table of Contents -->
                <div class="card" style="padding: 18px; position: sticky; top: 20px; background: #ffffff;">
                    <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                        <i data-lucide="list" style="width: 14px; height: 14px; color: var(--verde-primary);"></i> Table of Contents
                    </div>
                    <nav style="display: flex; flex-direction: column; gap: 3px; font-size: 12.5px;">
                        <a href="javascript:void(0)" class="docs-toc-item active" onclick="window.scrollToDocSec('doc-sec-overview', this)">1. Architecture Vision & Paradigm</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-pipeline', this)">2. 10-Stage Research Lifecycle</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-state-machine', this)">3. Candidate State Machine</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-telemetry', this)">4. Portfolio Empty Diagnostics</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-quality', this)">5. Quality Engine V2 Benchmark</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-redundancy', this)">6. 3-Tier Redundancy Engine</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-fastexpr', this)">7. FastExpr Operator Library</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-recipes', this)">8. Tested Formula Recipes</a>
                        <a href="javascript:void(0)" class="docs-toc-item" onclick="window.scrollToDocSec('doc-sec-faq', this)">9. Exhaustive FAQ / Q&A</a>
                    </nav>
                </div>

                <!-- Right Main Articles Area -->
                <div style="display: flex; flex-direction: column; gap: 24px;" id="docs-articles-wrapper">

                    <!-- Section 1: System Vision -->
                    <div class="card docs-article-card" id="doc-sec-overview" data-category="overview">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(34, 197, 94, 0.1); color: var(--verde-primary); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">1</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">1. System Architecture & Vision: Evaluation-First Engine</h2>
                        </div>
                        <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.65; margin-bottom: 16px;">
                            The VERDE Platform operates as an <strong>evaluation-first hypothesis engine</strong> designed specifically for WorldQuant BRAIN quantitative alpha creation. Rather than behaving like an unconstrained formula generator with a submission filter at the tail end, VERDE decouples candidate generation from portfolio submission, ensuring every candidate is evaluated across empirical quality, AST structural uniqueness, and execution telemetry.
                        </p>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px;">
                            <div style="padding: 16px; background: #fff1f2; border: 1px solid rgba(244, 63, 94, 0.25); border-radius: var(--radius-md);">
                                <strong style="color: #be123c; font-size: 13px; display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                                    <i data-lucide="x-circle" style="width: 16px; height: 16px;"></i> Legacy Alpha Generator Anti-Pattern
                                </strong>
                                <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #9f1239; line-height: 1.6;">
                                    <li>Random token mutation without underlying economic hypothesis.</li>
                                    <li>Candidate creation directly tied to submission attempt.</li>
                                    <li>Zero root-cause analysis when portfolio yields 0 positions.</li>
                                    <li>Repeated submission of structural duplicates across research runs.</li>
                                    <li>Lack of persistent memory for rejected near-miss candidates.</li>
                                </ul>
                            </div>
                            <div style="padding: 16px; background: #f0fdf4; border: 1px solid rgba(34, 197, 94, 0.25); border-radius: var(--radius-md);">
                                <strong style="color: #15803d; font-size: 13px; display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                                    <i data-lucide="check-circle" style="width: 16px; height: 16px;"></i> VERDE Evaluation-First Research Architecture
                                </strong>
                                <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #166534; line-height: 1.6;">
                                    <li>Structured economic hypotheses (Research Question, Mechanism, Horizon).</li>
                                    <li>10-stage transparent experiment lifecycle with granular progress telemetry.</li>
                                    <li>Full portfolio construction telemetry (Last Non-Zero vs. First Empty Stage).</li>
                                    <li>3-Tier Redundancy Engine (Exact hash, AST topology, Jaccard overlap).</li>
                                    <li>Pre-BRAIN Quality Engine V2 evaluating 8 independent sub-scores.</li>
                                </ul>
                            </div>
                        </div>

                        <div style="padding: 16px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md); font-size: 12.5px; color: var(--text-main);">
                            <strong style="color: var(--verde-dark); display: block; margin-bottom: 6px;">Quantitative Signal Flow Paradigm:</strong>
                            <div style="color: var(--text-muted); line-height: 1.6;">
                                High-quality alpha formulas express cross-sectional information advantage over asset universes. VERDE evaluates signal validity through normalized FastExpr syntax:
                                <code style="display: block; padding: 10px; margin-top: 8px; background: #1e293b; color: #38bdf8; border-radius: 4px; font-size: 12px;">
                                    w_i(t) = GroupNeutralize( Rank( f(X_{i,t-d:t}) ), Group_i )
                                </code>
                                Where \(X\) represents asset time-series data, \(f\) represents temporal/cross-sectional operator composition, and \(w_i(t)\) represents the dollar position weight.
                            </div>
                        </div>
                    </div>

                    <!-- Section 2: 10-Stage Research Lifecycle -->
                    <div class="card docs-article-card" id="doc-sec-pipeline" data-category="pipeline">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(2, 132, 199, 0.1); color: #0284c7; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">2</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">2. 10-Stage Research Experiment Lifecycle</h2>
                        </div>
                        <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.65; margin-bottom: 16px;">
                            Every research experiment moves through 10 strict, observable stages from initial hypothesis definition to final evidence-based research conclusion synthesis:
                        </p>

                        <div style="display: flex; flex-direction: column; gap: 12px; font-size: 12.5px;">
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #64748b; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 1: CREATED</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Experiment container created with candidate budget allocation, target research family (e.g., <code>MOMENTUM</code>, <code>VALUE</code>, <code>VOLATILITY</code>), and metadata profile.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #0284c7; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 2: HYPOTHESIS_DEFINED</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Structured economic hypothesis parameters defined: <em>Research Question</em>, <em>Core Anomaly Hypothesis</em>, <em>Economic Mechanism</em>, <em>Expected Asset Behavior</em>, <em>Investment Horizon</em>, <em>Target Universe</em>, and <em>Neutralization Scheme</em>.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #0284c7; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 3: GENERATING</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Combinatorial generator engine and multi-LLM synthesis modules assemble candidate FastExpr mathematical expressions aligned with the hypothesis.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #0284c7; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 4: GENERATED</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Candidates saved to DB with exact string hash (<code>expression_hash</code>), normalized AST tree topology hash (<code>structure_hash</code>), and field/operator usage indices.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #ca8a04; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 5: VALIDATING</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    AST parser verifies expression syntax, balanced parentheses, valid operator argument counts, field availability, and domain parameter bounds (\(d > 0\)). Candidates failing syntax become <code>INVALID</code>.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #ca8a04; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 6: EVALUATING</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Candidate executed in portfolio simulation sandbox. The pipeline constructs position weights across all pipeline stages, recording position counts and non-zero status.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #22c55e; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 7: QUALITY_REVIEW</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Candidate evaluated across Quality Engine V2's 8 independent dimensions (Semantic Quality, Expression Simplicity, Parameter Stability, Cross-Sectional Spread, Field Quality, Operator Hygiene, Data Compatibility, Robustness).
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #22c55e; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 8: RESEARCH_REVIEW</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Redundancy Engine evaluates candidate uniqueness against exact string match, AST topology, and Jaccard overlap similarity (threshold > 0.85). Structural duplicates are marked <code>REJECTED</code>.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f8fafc; border-left: 4px solid #22c55e; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: var(--text-main); font-size: 13px;">Stage 9: SUBMISSION_REVIEW</strong>
                                <p style="margin: 4px 0 0 0; color: var(--text-muted); line-height: 1.5;">
                                    Qualified <code>ELITE</code> candidates (Score ≥ 65.0, novel) pass the Submission Gate and transition to <code>SUBMISSION_PENDING</code> → <code>SUBMITTED</code>.
                                </p>
                            </div>
                            <div style="padding: 12px 16px; background: #f0fdf4; border-left: 4px solid #16a34a; border-radius: 0 var(--radius-md) var(--radius-md) 0;">
                                <strong style="color: #15803d; font-size: 13px;">Stage 10: COMPLETED</strong>
                                <p style="margin: 4px 0 0 0; color: #166534; line-height: 1.5;">
                                    Synthesizes evidence-based <code>ResearchConclusion</code> (Key Findings, Production Decision, Evidence Confidence) and persists detailed evidence into historical Research Memory.
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Section 3: Candidate State Machine -->
                    <div class="card docs-article-card" id="doc-sec-state-machine" data-category="state-machine">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(168, 85, 247, 0.1); color: #a855f7; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">3</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">3. Candidate Lifecycle State Machine</h2>
                        </div>
                        <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.65; margin-bottom: 16px;">
                            Every candidate formula progresses strictly through a state machine with explicit preconditions, trigger events, and state outputs:
                        </p>

                        <div style="padding: 18px; background: #0f172a; color: #38bdf8; border-radius: var(--radius-md); font-family: monospace; font-size: 11.5px; line-height: 1.7; overflow-x: auto; margin-bottom: 16px; border: 1px solid rgba(56, 189, 248, 0.2);">
[ GENERATED ]
      │
      ▼
[ VALIDATING ] ──────────► (Syntax/AST Failure) ──────────► [ INVALID ] (Rejected)
      │
      ▼ (Syntax Passed)
   [ VALID ]
      │
      ▼
[ EVALUATING ] ──────────► (Zero Positions Built) ────────► [ PORTFOLIO_EMPTY ] (Diagnosed)
      │
      ▼ (Positions Constructed > 0)
  [ EVALUATED ]
      │
      ├──► (Quality Score < 45.0 OR Duplicate > 0.85) ────► [ REJECTED ]
      ├──► (Quality Score 45.0 - 64.9 AND Novel)       ────► [ PROMISING ] (Stored in Memory)
      └──► (Quality Score ≥ 65.0 AND Novel)           ────► [ ELITE ]
                                                                 │
                                                                 ▼
                                                      [ SUBMISSION_PENDING ]
                                                                 │
                                                                 ▼
                                                           [ SUBMITTED ]
                        </div>

                        <h4 style="font-size: 13px; font-weight: 700; color: var(--text-main); margin: 16px 0 10px 0;">State Machine Definition Table</h4>
                        <div class="table-container">
                            <table class="modern-table" style="font-size: 12px;">
                                <thead>
                                    <tr>
                                        <th>State Name</th>
                                        <th>Preconditions</th>
                                        <th>Description & Action Taken</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>GENERATED</code></td>
                                        <td>Formula synthesized</td>
                                        <td>Initial candidate state. AST parsed, hashes generated.</td>
                                    </tr>
                                    <tr>
                                        <td><code>VALIDATING</code></td>
                                        <td>State = GENERATED</td>
                                        <td>Undergoing syntax and parameter domain validation.</td>
                                    </tr>
                                    <tr>
                                        <td><code>VALID</code></td>
                                        <td>Validation passed</td>
                                        <td>Candidate expression is syntactically sound; ready for portfolio construction.</td>
                                    </tr>
                                    <tr>
                                        <td><code>INVALID</code></td>
                                        <td>Validation failed</td>
                                        <td>Syntax error, unbalanced parens, or invalid operator arguments. Terminal rejection.</td>
                                    </tr>
                                    <tr>
                                        <td><code>EVALUATING</code></td>
                                        <td>State = VALID</td>
                                        <td>Running portfolio simulation sandbox to build positions.</td>
                                    </tr>
                                    <tr>
                                        <td><code>EVALUATED</code></td>
                                        <td>Simulation complete</td>
                                        <td>Portfolio constructed with non-zero position weights and performance metrics.</td>
                                    </tr>
                                    <tr>
                                        <td><code>PORTFOLIO_EMPTY</code></td>
                                        <td>Positions = 0</td>
                                        <td>Portfolio construction produced zero positions. Diagnostic classification recorded.</td>
                                    </tr>
                                    <tr>
                                        <td><code>REJECTED</code></td>
                                        <td>Score < 45 or Dup > 0.85</td>
                                        <td>Weak performance or structural duplicate of existing candidate.</td>
                                    </tr>
                                    <tr>
                                        <td><code>PROMISING</code></td>
                                        <td>Score 45.0 - 64.9</td>
                                        <td>Strong candidate near quality cutoff; stored in research memory for targeted mutation.</td>
                                    </tr>
                                    <tr>
                                        <td><code>ELITE</code></td>
                                        <td>Score ≥ 65.0 & Novel</td>
                                        <td>Production-grade alpha candidate passing all Quality Engine V2 & Redundancy checks.</td>
                                    </tr>
                                    <tr>
                                        <td><code>SUBMITTED</code></td>
                                        <td>Passed Submission Gate</td>
                                        <td>Successfully submitted to WorldQuant BRAIN platform.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Section 4: Portfolio Empty Diagnostics -->
                    <div class="card docs-article-card" id="doc-sec-telemetry" data-category="telemetry">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(234, 179, 8, 0.1); color: #ca8a04; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">4</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">4. Portfolio Construction Telemetry Diagnostics</h2>
                        </div>
                        <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.65; margin-bottom: 16px;">
                            When portfolio construction produces 0 positions, VERDE records stage telemetry to pinpoint the exact failure stage. The diagnostic tracks <code>LAST NONZERO STAGE</code> (final stage with active weights) and <code>FIRST EMPTY STAGE</code> (stage where weights collapsed to zero).
                        </p>

                        <div class="table-container" style="margin-bottom: 16px;">
                            <table class="modern-table" style="font-size: 12px;">
                                <thead>
                                    <tr>
                                        <th>Pipeline Stage</th>
                                        <th>Telemetry Metric</th>
                                        <th>Failure Root Cause & Diagnostic Classification</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>RAW_DATA</code></td>
                                        <td><code>raw_count</code></td>
                                        <td><strong>DATA_UNAVAILABLE:</strong> Asset price/volume data missing or empty for target universe.</td>
                                    </tr>
                                    <tr>
                                        <td><code>EXPRESSION</code></td>
                                        <td><code>nonzero_count</code></td>
                                        <td><strong>EXPRESSION_NULL:</strong> FastExpr formula evaluated to NaN or constant 0.0 across all assets.</td>
                                    </tr>
                                    <tr>
                                        <td><code>RANKING</code></td>
                                        <td><code>ranked_count</code></td>
                                        <td><strong>RANK_COLLAPSE:</strong> Zero variance in expression output (all assets produce identical signal).</td>
                                    </tr>
                                    <tr>
                                        <td><code>NEUTRALIZATION</code></td>
                                        <td><code>neutralized_count</code></td>
                                        <td><strong>GROUP_NEUTRAL_FAILURE:</strong> All assets belong to single group or industry group data is missing.</td>
                                    </tr>
                                    <tr>
                                        <td><code>TRUNCATION</code></td>
                                        <td><code>eligible_count</code></td>
                                        <td><strong>WEIGHT_TRUNCATED:</strong> Extreme concentration causing all position weights to fall below min limit.</td>
                                    </tr>
                                    <tr>
                                        <td><code>FINAL_POSITIONS</code></td>
                                        <td><code>position_count</code></td>
                                        <td><strong>VALID:</strong> Active long/short portfolio constructed (e.g., 250 long / 250 short positions).</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Section 5: Pre-BRAIN Quality Engine V2 -->
                    <div class="card docs-article-card" id="doc-sec-quality" data-category="quality-v2">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(34, 197, 94, 0.1); color: #22c55e; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">5</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">5. Pre-BRAIN Quality Engine V2 Benchmark</h2>
                        </div>
                        <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.65; margin-bottom: 16px;">
                            The Quality Engine evaluates candidate formulas across 8 weighted sub-dimensions to compute the overall Pre-BRAIN Quality Score (0 - 100):
                        </p>

                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; font-size: 12px; margin-bottom: 16px;">
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">1. Semantic Quality (20 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Penalizes constant signals, zero variance, or trivial expressions. Requires active signal variance.</div>
                            </div>
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">2. Expression Simplicity (15 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Penalizes AST depth > 4 or operator count > 6: \(P = \max(0, (\text{depth} - 4) \times 3)\).</div>
                            </div>
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">3. Parameter Stability (15 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Penalizes arbitrary magic floating point numbers (e.g. <code>returns * 1.00034</code>).</div>
                            </div>
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">4. Cross-Sectional Spread (15 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Rewards non-zero rank dispersion across the asset universe (\(\sigma(\text{rank}) > 0.20\)).</div>
                            </div>
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">5. Field Intelligence (10 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Rewards high-quality price, volume, and fundamental data fields over low-coverage fields.</div>
                            </div>
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">6. Operator Hygiene (10 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Rewards decay linear and group neutralize operators for risk management.</div>
                            </div>
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">7. Data Compatibility (10 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Verifies universe definition and execution delay alignment (e.g. <code>delay=1</code>).</div>
                            </div>
                            <div style="padding: 12px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                                <strong style="color: var(--text-main); font-size: 12.5px;">8. Robustness Score (5 pts):</strong>
                                <div style="color: var(--text-muted); margin-top: 4px;">Verifies out-of-sample decay stability across sub-periods.</div>
                            </div>
                        </div>

                        <div style="padding: 14px 16px; background: #f0fdf4; border: 1px solid rgba(34, 197, 94, 0.3); border-radius: var(--radius-sm); font-size: 12.5px; color: #15803d;">
                            <strong>Quality Weighting Formula:</strong><br>
                            <code>Overall Quality Score = 0.40 * PreBrain_Score + 0.60 * Simulation_Performance_Score</code>
                        </div>
                    </div>

                    <!-- Section 6: 3-Tier Redundancy Engine -->
                    <div class="card docs-article-card" id="doc-sec-redundancy" data-category="redundancy">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(225, 29, 72, 0.1); color: #e11d48; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">6</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">6. 3-Tier Redundancy Engine & Similarity</h2>
                        </div>
                        <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.65; margin-bottom: 16px;">
                            To prevent submitting redundant alpha formulas to WorldQuant BRAIN, candidates are evaluated through three levels of similarity:
                        </p>

                        <div style="display: flex; flex-direction: column; gap: 12px; font-size: 12px; margin-bottom: 16px;">
                            <div style="padding: 14px; background: #fff1f2; border: 1px solid rgba(244, 63, 94, 0.25); border-radius: var(--radius-sm);">
                                <strong style="color: #be123c; font-size: 12.5px;">Tier 1: Exact String Match (Score = 1.0)</strong>
                                <p style="margin: 4px 0 0 0; color: #9f1239; line-height: 1.5;">
                                    Compares candidate <code>expression_hash</code> against all previously evaluated candidates in the database.
                                </p>
                            </div>
                            <div style="padding: 14px; background: #fffbe6; border: 1px solid rgba(234, 179, 8, 0.3); border-radius: var(--radius-sm);">
                                <strong style="color: #854d0e; font-size: 12.5px;">Tier 2: Structural AST Topology Match (Score ≥ 0.90)</strong>
                                <p style="margin: 4px 0 0 0; color: #854d0e; line-height: 1.5;">
                                    Normalizes AST operator tree nodes, stripping lookback integer variations (e.g. <code>ts_rank(close, 20)</code> vs. <code>ts_rank(close, 30)</code>).
                                </p>
                            </div>
                            <div style="padding: 14px; background: #f0fdf4; border: 1px solid rgba(34, 197, 94, 0.25); border-radius: var(--radius-sm);">
                                <strong style="color: #15803d; font-size: 12.5px;">Tier 3: Operator & Field Overlap Similarity (Jaccard Overlap > 0.85)</strong>
                                <p style="margin: 4px 0 0 0; color: #166534; line-height: 1.5;">
                                    Computes Jaccard set similarity between field and operator sets:
                                    <code style="display: inline-block; margin-top: 4px; padding: 2px 6px; background: #dcfce7; color: #15803d; border-radius: 4px;">J(A, B) = |A ∩ B| / |A ∪ B|</code>.
                                    Candidates exceeding 0.85 overlap are marked <code>REJECTED</code> to prevent alpha cannibalization.
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Section 7: FastExpr Operator Library Reference -->
                    <div class="card docs-article-card" id="doc-sec-fastexpr" data-category="fastexpr">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(14, 165, 233, 0.1); color: #0ea5e9; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">7</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">7. FastExpr Syntax & Operator Library Reference</h2>
                        </div>

                        <div class="table-container">
                            <table class="modern-table" style="font-size: 12px;">
                                <thead>
                                    <tr>
                                        <th>Operator</th>
                                        <th>Signature</th>
                                        <th>Category</th>
                                        <th>Math Definition / Operation Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>rank</code></td>
                                        <td><code>rank(x)</code></td>
                                        <td>Cross-Sectional</td>
                                        <td>Cross-sectional percentile rank of <code>x</code> across all universe stocks (0.0 to 1.0).</td>
                                    </tr>
                                    <tr>
                                        <td><code>group_neutralize</code></td>
                                        <td><code>group_neutralize(x, g)</code></td>
                                        <td>Risk Neutralization</td>
                                        <td>Demeans and normalizes signal <code>x</code> within group <code>g</code> (e.g. <code>subindustry</code>, <code>sector</code>).</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_rank</code></td>
                                        <td><code>ts_rank(x, d)</code></td>
                                        <td>Time-Series</td>
                                        <td>Percentile rank of current value relative to its past <code>d</code> days: \(\frac{\text{Count}(x_{t-i} < x_t)}{d}\).</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_decay_linear</code></td>
                                        <td><code>ts_decay_linear(x, d)</code></td>
                                        <td>Time-Series</td>
                                        <td>Linearly weighted moving average over <code>d</code> days: \(\sum_{i=0}^{d-1} (d-i) x_{t-i} / \sum w\).</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_std_dev</code></td>
                                        <td><code>ts_std_dev(x, d)</code></td>
                                        <td>Time-Series</td>
                                        <td>Rolling sample standard deviation of <code>x</code> over past <code>d</code> days.</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_delta</code></td>
                                        <td><code>ts_delta(x, d)</code></td>
                                        <td>Time-Series</td>
                                        <td>Difference between current value and value <code>d</code> days ago: \(x_t - x_{t-d}\).</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_mean</code></td>
                                        <td><code>ts_mean(x, d)</code></td>
                                        <td>Time-Series</td>
                                        <td>Simple moving average of <code>x</code> over past <code>d</code> days.</td>
                                    </tr>
                                    <tr>
                                        <td><code>ts_delay</code></td>
                                        <td><code>ts_delay(x, d)</code></td>
                                        <td>Time-Series</td>
                                        <td>Lagged value of <code>x</code> from <code>d</code> days ago: \(x_{t-d}\).</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Section 8: Formula Recipes -->
                    <div class="card docs-article-card" id="doc-sec-recipes" data-category="recipes">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(34, 197, 94, 0.1); color: #22c55e; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">8</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">8. Tested Alpha Formula Recipes & Case Studies</h2>
                        </div>
                        <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.65; margin-bottom: 16px;">
                            Exhaustive, tested alpha expression recipes passing Quality Engine V2 benchmarks:
                        </p>

                        <div style="display: flex; flex-direction: column; gap: 16px;">
                            
                            <div style="padding: 16px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="font-size: 13.5px; color: #0284c7;">Recipe 1: Subindustry-Neutralized Linear Momentum</strong>
                                    <span class="badge badge-success" style="font-size: 10.5px;">Quality Score: 84.9</span>
                                </div>
                                <div class="code-expr" style="padding: 12px; background: #0f172a; color: #38bdf8; font-family: monospace; font-size: 12.5px; border-radius: 6px; margin-bottom: 8px; border: 1px solid rgba(56, 189, 248, 0.2);">
                                    group_neutralize(rank(ts_decay_linear(returns, 10)), subindustry)
                                </div>
                                <div style="font-size: 12px; color: var(--text-muted); line-height: 1.5;">
                                    Calculates 10-day linearly weighted return momentum, converts to cross-sectional rank, and neutralizes by subindustry group to eliminate sector bias.
                                </div>
                            </div>

                            <div style="padding: 16px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="font-size: 13.5px; color: #0284c7;">Recipe 2: Volatility-Normalized Mean Reversion</strong>
                                    <span class="badge badge-success" style="font-size: 10.5px;">Quality Score: 83.9</span>
                                </div>
                                <div class="code-expr" style="padding: 12px; background: #0f172a; color: #38bdf8; font-family: monospace; font-size: 12.5px; border-radius: 6px; margin-bottom: 8px; border: 1px solid rgba(56, 189, 248, 0.2);">
                                    group_neutralize(rank(-ts_delta(close, 5) / (ts_std_dev(returns, 20) + 0.0001)), subindustry)
                                </div>
                                <div style="font-size: 12px; color: var(--text-muted); line-height: 1.5;">
                                    Identifies short-term 5-day price pullbacks normalized by 20-day return volatility, ranking negative price shifts for mean reversion.
                                </div>
                            </div>

                            <div style="padding: 16px; background: #f8fafc; border: 1px solid var(--border-light); border-radius: var(--radius-md);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="font-size: 13.5px; color: #0284c7;">Recipe 3: Volume-Trend Momentum Confirmation</strong>
                                    <span class="badge badge-success" style="font-size: 10.5px;">Quality Score: 79.7</span>
                                </div>
                                <div class="code-expr" style="padding: 12px; background: #0f172a; color: #38bdf8; font-family: monospace; font-size: 12.5px; border-radius: 6px; margin-bottom: 8px; border: 1px solid rgba(56, 189, 248, 0.2);">
                                    group_neutralize(rank(ts_rank(volume, 20) * ts_delta(close, 5)), sector)
                                </div>
                                <div style="font-size: 12px; color: var(--text-muted); line-height: 1.5;">
                                    Combines 20-day volume percentile rank with 5-day price momentum, sector neutralized to capture volume-confirmed price trends.
                                </div>
                            </div>

                        </div>
                    </div>

                    <!-- Section 9: Exhaustive FAQ / Q&A Accordion -->
                    <div class="card docs-article-card" id="doc-sec-faq" data-category="faq">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                            <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(99, 102, 241, 0.1); color: #6366f1; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px;">9</div>
                            <h2 style="font-size: 19px; font-weight: 800; color: var(--text-main); margin: 0;">9. Exhaustive Frequently Asked Questions (FAQ & Q&A)</h2>
                        </div>

                        <div style="display: flex; flex-direction: column; gap: 12px;" id="docs-faq-accordion">
                            
                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q1: Why was my alpha candidate marked as PORTFOLIO_EMPTY?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    A <code>PORTFOLIO_EMPTY</code> state occurs when portfolio construction produces zero position weights. Click "Inspect Candidate" to view the <code>portfolio_telemetry</code> diagnostic block. It displays the <strong>LAST NONZERO STAGE</strong> and <strong>FIRST EMPTY STAGE</strong> (e.g. <code>NEUTRALIZATION</code> when all assets fall into a single industry group, or <code>TRUNCATION</code> when weights fall below threshold).
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q2: What is the difference between PROMISING and ELITE candidates?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    <code>ELITE</code> candidates achieve a Pre-BRAIN Quality Score ≥ 65.0, pass all 3-tier redundancy checks, and automatically qualify for WorldQuant BRAIN platform submission. <code>PROMISING</code> candidates score between 45.0 and 64.9; they are retained in persistent research memory for near-miss mutation synthesis.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q3: How does the 3-Tier Redundancy Engine prevent alpha overcrowding?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    Tier 1 checks exact string hashes, Tier 2 checks AST structural topologies (ignoring lookback window parameter shifts), and Tier 3 computes field/operator Jaccard similarity (> 0.85). Any duplicate is rejected to preserve portfolio uniqueness.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q4: How do I initiate a new hypothesis-driven Research Experiment?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    Click "+ New Experiment" on the Dashboard or Quality Control page. Fill out the Research Title, Research Question, Core Hypothesis, Mechanism, Expected Behavior, Neutralization, and Target Candidate Budget.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q5: How is the Pre-BRAIN Quality Score calculated?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    The score is a 0 - 100 weighted combination across 8 dimensions: 40% Pre-BRAIN AST & Semantic Quality + 60% Portfolio Simulation Performance (Sharpe, Fitness, Turnover, and Margin).
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q6: What are the minimum performance benchmarks for WorldQuant BRAIN submission?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    Qualified candidates require: Sharpe Ratio ≥ 1.25, Fitness ≥ 1.00, Turnover ≤ 0.70 (70%), Margin ≥ 4.0 bps, Subindustry Neutralization, and zero exact/structural redundancy.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q7: How does Evidence-Driven Gap Detection allocate research budgets?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    Gap Detection evaluates historical experiment performance across all 15 research families. Underexplored families with high potential receive higher proportional candidate generation budgets (e.g. 35% vs 15%).
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q8: Can I simulate custom alpha expressions on WorldQuant BRAIN?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    Yes! Navigate to the Alpha Lab or Candidates tab and click "Simulate on BRAIN" on any candidate card to run portfolio simulation and calculate live metrics.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q9: What is AST Structural Topology Matching?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    AST Structural Topology Matching normalizes the Abstract Syntax Tree of an expression by stripping lookback window integer constants (e.g., converting <code>ts_rank(close, 20)</code> and <code>ts_rank(close, 30)</code> into the identical structural hash). This prevents parameter-jitter duplicate submissions.
                                </div>
                            </div>

                            <div class="docs-faq-item">
                                <div class="docs-faq-question" onclick="window.toggleFaqItem(this)">
                                    <span>Q10: How does VERDE handle missing telemetry or missing field metrics?</span>
                                    <i data-lucide="chevron-down"></i>
                                </div>
                                <div class="docs-faq-answer">
                                    VERDE strictly enforces non-fabrication of metrics. If simulation stats or telemetry fields are missing, the system outputs <code>UNKNOWN</code> or <code>N/A</code> rather than converting nulls into misleading zeros.
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
