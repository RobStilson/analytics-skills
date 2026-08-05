const pptxgen = require("pptxgenjs");
const pres = new pptxgen();

pres.layout = "LAYOUT_WIDE";           // 13.3 x 7.5
pres.author = "Rob Stilson";
pres.title = "Vibe Analytics";

// Palette: ink dominates; orange marks findings and failures; teal marks verified.
const INK = "22303C";
const SLATE = "5A6B7A";
const PAPER = "FFFFFF";
const TINT = "F2F4F6";
const ORANGE = "E8663C";
const TEAL = "2D8A72";
const MUTED = "8A99A8";

const H = "Cambria";
const B = "Calibri";

const W = 13.33, HT = 7.5;
const M = 0.7;

// ---------------------------------------------------------------- helpers
function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: INK };
  return s;
}
function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  return s;
}
function title(s, text, opts = {}) {
  s.addText(text, {
    x: M, y: opts.y || 0.5, w: W - 2 * M, h: 0.9,
    fontFace: H, fontSize: opts.size || 34, bold: true,
    color: opts.color || INK, align: "left", margin: 0,
  });
}
function kicker(s, text, color) {
  s.addText(text.toUpperCase(), {
    x: M, y: 0.28, w: W - 2 * M, h: 0.3,
    fontFace: B, fontSize: 11, bold: true, charSpacing: 2,
    color: color || ORANGE, margin: 0,
  });
}
function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: fill || TINT }, line: { color: fill || TINT, width: 0 },
  });
}

// ================================================================ 1 TITLE
{
  const s = darkSlide();
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 2.0, w: 0.14, h: 2.5, rectRadius: 0.07,
    fill: { color: ORANGE }, line: { color: ORANGE, width: 0 },
  });
  s.addText("Vibe Analytics", {
    x: M + 0.45, y: 2.0, w: 9.5, h: 1.3,
    fontFace: H, fontSize: 58, bold: true, color: PAPER, margin: 0,
  });
  s.addText("Reimagining the analytics lifecycle in an AI era", {
    x: M + 0.45, y: 3.3, w: 9.5, h: 0.6,
    fontFace: B, fontSize: 22, color: "CBD5DD", margin: 0,
  });
  s.addText("Define  →  Build  →  Validate  →  Operationalize  →  Monitor  →  Compound", {
    x: M + 0.45, y: 4.05, w: 11, h: 0.4,
    fontFace: B, fontSize: 14, color: MUTED, margin: 0,
  });
  s.addText("3-hour hands-on workshop", {
    x: M + 0.45, y: 6.3, w: 8, h: 0.4,
    fontFace: B, fontSize: 13, color: MUTED, margin: 0,
  });
  s.addNotes("Open with the promise: everyone leaves with a working skill in their own repo, and a measured before/after from a real warehouse. Set expectation that we will run one workflow end to end rather than skim five.");
}

// ================================================================ 2 WHY CODING FIRST
{
  const s = lightSlide();
  kicker(s, "The premise");
  title(s, "Coding agents worked first for a structural reason");

  const colW = 5.55;
  card(s, M, 1.75, colW, 3.9, TINT);
  s.addText("Software", {
    x: M + 0.4, y: 2.0, w: colW - 0.8, h: 0.4,
    fontFace: H, fontSize: 22, bold: true, color: INK, margin: 0,
  });
  s.addText([
    { text: "Open-ended solution space", options: { bullet: true, breakLine: true } },
    { text: "Many valid answers", options: { bullet: true, breakLine: true } },
    { text: "Tests, types, compilers catch errors", options: { bullet: true, breakLine: true } },
    { text: "Wrong code usually fails loudly", options: { bullet: true } },
  ], {
    x: M + 0.4, y: 2.6, w: colW - 0.8, h: 2.8,
    fontFace: B, fontSize: 15, color: SLATE, paraSpaceAfter: 10, margin: 0,
  });

  card(s, M + colW + 0.5, 1.75, colW, 3.9, "FBEDE8");
  s.addText("Analytics", {
    x: M + colW + 0.9, y: 2.0, w: colW - 0.8, h: 0.4,
    fontFace: H, fontSize: 22, bold: true, color: ORANGE, margin: 0,
  });
  s.addText([
    { text: "Usually one correct answer", options: { bullet: true, breakLine: true } },
    { text: "From one correct source", options: { bullet: true, breakLine: true } },
    { text: "No deterministic way to prove it", options: { bullet: true, breakLine: true } },
    { text: "Wrong queries run cleanly", options: { bullet: true } },
  ], {
    x: M + colW + 0.9, y: 2.6, w: colW - 0.8, h: 2.8,
    fontFace: B, fontSize: 15, color: "8C4430", paraSpaceAfter: 10, margin: 0,
  });

  s.addText("Data is not software. Skills written for software development do not transfer.", {
    x: M, y: 5.95, w: W - 2 * M, h: 0.5,
    fontFace: H, fontSize: 19, italic: true, bold: true, color: INK, margin: 0,
  });
  s.addNotes("This is the framing that earns permission for everything else. Ask the room: who has shipped a number that was wrong and nobody noticed for weeks? Most hands go up.");
}

// ================================================================ 3 FAILURE MODES
{
  const s = lightSlide();
  kicker(s, "Diagnosis");
  title(s, "Three failure modes, and one that hides");

  const items = [
    ["Entity ambiguity", "Forty plausible tables could answer 'headcount'. The agent picks one."],
    ["Staleness", "Definitions and schemas change. Docs and agent knowledge rot."],
    ["Retrieval failure", "The right answer is documented. The agent never finds it."],
  ];
  let x = M;
  const cw = 3.85;
  items.forEach(([h, d]) => {
    card(s, x, 1.8, cw, 2.0, TINT);
    s.addText(h, {
      x: x + 0.3, y: 2.05, w: cw - 0.6, h: 0.4,
      fontFace: H, fontSize: 18, bold: true, color: INK, margin: 0,
    });
    s.addText(d, {
      x: x + 0.3, y: 2.5, w: cw - 0.6, h: 1.1,
      fontFace: B, fontSize: 13, color: SLATE, margin: 0,
    });
    x += cw + 0.42;
  });

  card(s, M, 4.1, W - 2 * M, 1.9, "FBEDE8");
  s.addText("Silent wrongness", {
    x: M + 0.4, y: 4.35, w: 6, h: 0.4,
    fontFace: H, fontSize: 22, bold: true, color: ORANGE, margin: 0,
  });
  s.addText("The answer is wrong, looks plausible, and is used without objection. None of the three fixes above fully catch it — and nothing in your stack raises an alarm.", {
    x: M + 0.4, y: 4.85, w: W - 2 * M - 0.8, h: 0.9,
    fontFace: B, fontSize: 15, color: "8C4430", margin: 0,
  });
  s.addNotes("The first three are tractable with better routing. The fourth is why provenance and review exist. Everything in the pack attacks at least one of these.");
}

// ================================================================ 4 THE LOOP
{
  const s = lightSlide();
  kicker(s, "The workflow");
  title(s, "Five stages, and the one that compounds");

  const stages = [
    ["Define", "Spec the question"],
    ["Build", "Find and query"],
    ["Validate", "Check and doubt"],
    ["Operationalize", "Ship with provenance"],
    ["Monitor", "Watch for drift"],
  ];
  let x = M;
  const cw = 2.28;
  stages.forEach(([h, d], i) => {
    card(s, x, 2.1, cw, 1.5, i === 4 ? TINT : TINT);
    s.addText(h, {
      x: x + 0.15, y: 2.3, w: cw - 0.3, h: 0.35,
      fontFace: H, fontSize: 15, bold: true, color: INK, align: "center", margin: 0,
    });
    s.addText(d, {
      x: x + 0.15, y: 2.7, w: cw - 0.3, h: 0.7,
      fontFace: B, fontSize: 11, color: SLATE, align: "center", margin: 0,
    });
    if (i < 4) {
      s.addText("→", {
        x: x + cw + 0.02, y: 2.6, w: 0.35, h: 0.4,
        fontFace: B, fontSize: 18, color: MUTED, align: "center", margin: 0,
      });
    }
    x += cw + 0.37;
  });

  card(s, M, 4.15, W - 2 * M, 1.85, "E6F2EE");
  s.addText("Compound", {
    x: M + 0.4, y: 4.4, w: 5, h: 0.4,
    fontFace: H, fontSize: 22, bold: true, color: TEAL, margin: 0,
  });
  s.addText("Every correction becomes a doc edit and an eval. Skip this step and you have done traditional analytics with an AI typing for you.", {
    x: M + 0.4, y: 4.9, w: W - 2 * M - 0.8, h: 0.85,
    fontFace: B, fontSize: 15, color: "1F5F4C", margin: 0,
  });
  s.addNotes("Credit Every's compound engineering for the loop shape. The fourth step is what separates this from ordinary AI-assisted work. A stakeholder correction is a labeled error diagnosed for free by someone with domain authority — throwing it away after patching the answer wastes the best signal you get.");
}

// ================================================================ 5 THE REFRAME
{
  const s = darkSlide();
  kicker(s, "The reframe", ORANGE);
  title(s, "A skill is markdown, not code", { color: PAPER });

  s.addText("The agent doesn't need you to write code anymore.\nIt needs you to write down what you know.", {
    x: M, y: 2.1, w: 11.5, h: 1.4,
    fontFace: H, fontSize: 30, italic: true, color: PAPER, margin: 0, lineSpacing: 40,
  });

  const pts = [
    ["Anyone can contribute", "A SQL analyst and a senior DS both ship a real artifact in 90 minutes"],
    ["The bottleneck is judgment", "Which analysts have, and models don't"],
    ["Deployable Monday", "A folder of .md files, versioned in your repo"],
  ];
  let x = M;
  const cw = 3.85;
  pts.forEach(([h, d]) => {
    card(s, x, 4.1, cw, 1.9, "2E3E4C");
    s.addText(h, {
      x: x + 0.3, y: 4.35, w: cw - 0.6, h: 0.4,
      fontFace: H, fontSize: 16, bold: true, color: ORANGE, margin: 0,
    });
    s.addText(d, {
      x: x + 0.3, y: 4.78, w: cw - 0.6, h: 1.05,
      fontFace: B, fontSize: 13, color: "CBD5DD", margin: 0,
    });
    x += cw + 0.42;
  });
  s.addNotes("This is the moment the room relaxes. Most arrive expecting to write Python. The hard part is domain knowledge, which they already have and have never written down.");
}

// ================================================================ 6 WHAT WE BUILT
{
  const s = lightSlide();
  kicker(s, "The pack");
  title(s, "What you're getting");

  const stats = [
    ["11", "skills", "Full lifecycle plus two reviewer personas"],
    ["44", "tables", "Synthetic warehouse, eleven engineered traps"],
    ["29", "evals", "Pinned ground truth, six negative tests"],
  ];
  let x = M;
  const cw = 3.85;
  stats.forEach(([n, l, d]) => {
    card(s, x, 1.9, cw, 2.5, TINT);
    s.addText(n, {
      x: x + 0.3, y: 2.1, w: cw - 0.6, h: 1.0,
      fontFace: H, fontSize: 60, bold: true, color: ORANGE, margin: 0,
    });
    s.addText(l, {
      x: x + 0.3, y: 3.05, w: cw - 0.6, h: 0.35,
      fontFace: H, fontSize: 18, bold: true, color: INK, margin: 0,
    });
    s.addText(d, {
      x: x + 0.3, y: 3.45, w: cw - 0.6, h: 0.8,
      fontFace: B, fontSize: 12, color: SLATE, margin: 0,
    });
    x += cw + 0.42;
  });

  s.addText([
    { text: "github.com/RobStilson/analytics-skills", options: { bold: true, color: INK } },
    { text: "   ·   MIT   ·   contributors credited in the README", options: { color: SLATE } },
  ], {
    x: M, y: 4.9, w: W - 2 * M, h: 0.4,
    fontFace: B, fontSize: 15, margin: 0,
  });
  s.addText("Everything open. You leave as a contributor, not an attendee.", {
    x: M, y: 5.4, w: W - 2 * M, h: 0.4,
    fontFace: B, fontSize: 14, italic: true, color: SLATE, margin: 0,
  });
  s.addNotes("The expense-justification line: they leave as a named contributor to an open-source pack, not with a certificate of attendance.");
}

// ================================================================ 7 THE WAREHOUSE
{
  const s = lightSlide();
  kicker(s, "The sandbox");
  title(s, "A warehouse built to be wrong in specific ways");

  s.addText("A clean warehouse teaches nothing. Ours has the ambiguities a real HRIS accumulates.", {
    x: M, y: 1.5, w: W - 2 * M, h: 0.4,
    fontFace: B, fontSize: 15, color: SLATE, margin: 0,
  });

  const rows = [
    ["Four answers to \"how many employees?\"", "12,282  /  4,368  /  4,168  /  3,647"],
    ["A column renamed but never dropped", "54% populated, silently drops 1,668 people"],
    ["A rollup that stopped refreshing", "Frozen 2026-02-28, still looks current"],
    ["A join that fans out", "2.32x inflation, no error raised"],
    ["A program with a true effect of zero", "Shows a 7-point gap from selection alone"],
  ];
  let y = 2.15;
  rows.forEach(([l, r], i) => {
    card(s, M, y, W - 2 * M, 0.72, i % 2 === 0 ? TINT : PAPER);
    s.addText(l, {
      x: M + 0.35, y: y + 0.16, w: 6.6, h: 0.4,
      fontFace: B, fontSize: 15, bold: true, color: INK, margin: 0,
    });
    s.addText(r, {
      x: M + 7.1, y: y + 0.16, w: 4.7, h: 0.4,
      fontFace: "Consolas", fontSize: 13, color: ORANGE, align: "right", margin: 0,
    });
    y += 0.78;
  });
  s.addNotes("One DuckDB file, no server, works offline. Reproducible from a fixed seed. Participants get no reference docs — writing one is the exercise.");
}

// ================================================================ 8 THE DEMO
{
  const s = lightSlide();
  kicker(s, "Live demo");
  title(s, "Same question. Same warehouse. Skill off, then on.");

  s.addText("\"How many employees do we have? Just give me the number, I'm in a hurry.\"", {
    x: M, y: 1.55, w: W - 2 * M, h: 0.45,
    fontFace: H, fontSize: 18, italic: true, color: SLATE, margin: 0,
  });

  const cw = 5.55;
  card(s, M, 2.25, cw, 3.3, "FBEDE8");
  s.addText("Without the skill", {
    x: M + 0.35, y: 2.5, w: cw - 0.7, h: 0.4,
    fontFace: H, fontSize: 19, bold: true, color: ORANGE, margin: 0,
  });
  s.addText("0 / 4", {
    x: M + 0.35, y: 3.0, w: cw - 0.7, h: 0.85,
    fontFace: H, fontSize: 46, bold: true, color: ORANGE, margin: 0,
  });
  s.addText("No source. No confidence. No population stated. A number that will be forwarded.", {
    x: M + 0.35, y: 3.95, w: cw - 0.7, h: 1.2,
    fontFace: B, fontSize: 14, color: "8C4430", margin: 0,
  });

  card(s, M + cw + 0.5, 2.25, cw, 3.3, "E6F2EE");
  s.addText("With the skill", {
    x: M + cw + 0.85, y: 2.5, w: cw - 0.7, h: 0.4,
    fontFace: H, fontSize: 19, bold: true, color: TEAL, margin: 0,
  });
  s.addText("4 / 4", {
    x: M + cw + 0.85, y: 3.0, w: cw - 0.7, h: 0.85,
    fontFace: H, fontSize: 46, bold: true, color: TEAL, margin: 0,
  });
  s.addText("Source table, confidence, freshness, population — attached despite the time pressure.", {
    x: M + cw + 0.85, y: 3.95, w: cw - 0.7, h: 1.2,
    fontFace: B, fontSize: 14, color: "1F5F4C", margin: 0,
  });

  s.addText("Measured on claude-sonnet-5 against the workshop warehouse. Single slice, single run.", {
    x: M, y: 5.8, w: W - 2 * M, h: 0.35,
    fontFace: B, fontSize: 12, italic: true, color: MUTED, margin: 0,
  });
  s.addNotes("Show the actual response text from results/baseline.json next to results/skills.json. Real output beats any abstract argument. Caveat honestly: one slice, one run.");
}

// ================================================================ 9 DIFFERENTIATORS
{
  const s = lightSlide();
  kicker(s, "What analysts bring that models don't");
  title(s, "Two skills with no software-engineering analogue");

  card(s, M, 1.85, 5.55, 4.1, TINT);
  s.addText("causal-claim-guardrail", {
    x: M + 0.35, y: 2.1, w: 4.9, h: 0.4,
    fontFace: "Consolas", fontSize: 17, bold: true, color: INK, margin: 0,
  });
  s.addText("Licenses causal language by design, not by correlation size.", {
    x: M + 0.35, y: 2.55, w: 4.9, h: 0.5,
    fontFace: B, fontSize: 14, color: SLATE, margin: 0,
  });
  s.addText([
    { text: "Selection into treatment", options: { bullet: true, breakLine: true } },
    { text: "Reverse causality", options: { bullet: true, breakLine: true } },
    { text: "Immortal time bias", options: { bullet: true, breakLine: true } },
    { text: "Survivorship, range restriction", options: { bullet: true, breakLine: true } },
    { text: "Compositional shift", options: { bullet: true } },
  ], {
    x: M + 0.35, y: 3.05, w: 4.9, h: 2.5,
    fontFace: B, fontSize: 13, color: SLATE, paraSpaceAfter: 8, margin: 0,
  });

  card(s, M + 6.05, 1.85, 5.55, 4.1, TINT);
  s.addText("uncertainty-reporting", {
    x: M + 6.4, y: 2.1, w: 4.9, h: 0.4,
    fontFace: "Consolas", fontSize: 17, bold: true, color: INK, margin: 0,
  });
  s.addText("Denominators, intervals, suppression, multiplicity.", {
    x: M + 6.4, y: 2.55, w: 4.9, h: 0.5,
    fontFace: B, fontSize: 14, color: SLATE, margin: 0,
  });
  s.addText([
    { text: "Wilson, not Wald, at small n", options: { bullet: true, breakLine: true } },
    { text: "Small-cell suppression is a legal duty", options: { bullet: true, breakLine: true } },
    { text: "Complementary disclosure", options: { bullet: true, breakLine: true } },
    { text: "Ranking 40 managers is 40 comparisons", options: { bullet: true, breakLine: true } },
    { text: "\"No difference\" vs \"no evidence\"", options: { bullet: true } },
  ], {
    x: M + 6.4, y: 3.05, w: 4.9, h: 2.5,
    fontFace: B, fontSize: 13, color: SLATE, paraSpaceAfter: 8, margin: 0,
  });
  s.addNotes("This is the I-O contribution. A software engineer would not think to write down immortal time bias or why Wald intervals fail exactly where workforce data lives.");
}

// ================================================================ 10 BUILD BLOCK
{
  const s = lightSlide();
  kicker(s, "Hands on — 45 minutes");
  title(s, "You write the reference doc");

  const rows = [
    ["Quick Reference", "5 min", "Which table, what grain, person key"],
    ["Required Filters", "10 min", "Largest source of silently wrong numbers"],
    ["Gotchas", "15 min", "The only section a model cannot generate"],
    ["Measures", "10 min", "Stops two teams reporting two rates"],
    ["Query Patterns", "5 min", "Saves the next person the same join"],
  ];
  let y = 1.9;
  rows.forEach(([l, t, d]) => {
    const hot = l === "Gotchas";
    card(s, M, y, W - 2 * M, 0.78, hot ? "FBEDE8" : TINT);
    s.addText(l, {
      x: M + 0.35, y: y + 0.19, w: 3.0, h: 0.4,
      fontFace: H, fontSize: 17, bold: true, color: hot ? ORANGE : INK, margin: 0,
    });
    s.addText(t, {
      x: M + 3.4, y: y + 0.22, w: 1.0, h: 0.35,
      fontFace: "Consolas", fontSize: 13, color: hot ? ORANGE : MUTED, margin: 0,
    });
    s.addText(d, {
      x: M + 4.6, y: y + 0.21, w: 7.2, h: 0.4,
      fontFace: B, fontSize: 14, color: hot ? "8C4430" : SLATE, margin: 0,
    });
    y += 0.84;
  });

  s.addText("What would you tell a new analyst in week one so they don't embarrass themselves?", {
    x: M, y: 6.15, w: W - 2 * M, h: 0.5,
    fontFace: H, fontSize: 19, italic: true, bold: true, color: INK, margin: 0,
  });
  s.addNotes("Sections are ordered by how much each reduces wrong answers. If someone runs out of time at minute 30, the parts they finished are the parts that mattered. The Gotchas prompt is the one that unlocks the room — everyone has twenty of these in their head.");
}

// ================================================================ 11 MEASURE
{
  const s = lightSlide();
  kicker(s, "The discipline");
  title(s, "Write the evals before you write the skill");

  s.addText("Same 29 questions, run twice. Skills off, then on. The difference is the measurement.", {
    x: M, y: 1.5, w: W - 2 * M, h: 0.4,
    fontFace: B, fontSize: 15, color: SLATE, margin: 0,
  });

  const steps = [
    ["1", "Pin ground truth", "Generated from the database, never hand-typed"],
    ["2", "Write negative tests", "Evals the skill should NOT change"],
    ["3", "Run the ablation", "Baseline, then skills, then compare"],
  ];
  let x = M;
  const cw = 3.85;
  steps.forEach(([n, h, d]) => {
    card(s, x, 2.2, cw, 2.3, TINT);
    s.addText(n, {
      x: x + 0.3, y: 2.4, w: 0.6, h: 0.55,
      fontFace: H, fontSize: 30, bold: true, color: ORANGE, margin: 0,
    });
    s.addText(h, {
      x: x + 0.3, y: 3.0, w: cw - 0.6, h: 0.4,
      fontFace: H, fontSize: 17, bold: true, color: INK, margin: 0,
    });
    s.addText(d, {
      x: x + 0.3, y: 3.45, w: cw - 0.6, h: 0.85,
      fontFace: B, fontSize: 13, color: SLATE, margin: 0,
    });
    x += cw + 0.42;
  });

  card(s, M, 4.8, W - 2 * M, 1.35, "E6F2EE");
  s.addText("A skill that fires on everything is indistinguishable from a skill that works. 21% of our evals test that the skill stays quiet.", {
    x: M + 0.4, y: 5.15, w: W - 2 * M - 0.8, h: 0.7,
    fontFace: B, fontSize: 15, color: "1F5F4C", margin: 0,
  });
  s.addNotes("Evals-before-skill is the TDD analogy and it earns credibility with a rigorous audience. Nobody gets to claim their skill 'feels better'.");
}

// ================================================================ 12 THE RESULT
{
  const s = darkSlide();
  kicker(s, "What we measured", ORANGE);
  title(s, "56% to 84%, across every slice", { color: PAPER });

  const rows = [
    ["uncertainty-reporting", "43%", "93%", "+50"],
    ["provenance-footer", "39%", "82%", "+42"],
    ["warehouse-navigation", "61%", "83%", "+23"],
    ["question-intake", "61%", "82%", "+21"],
    ["adversarial-sql-review", "54%", "72%", "+18"],
    ["causal-claim-guardrail", "74%", "87%", "+13"],
  ];
  let y = 1.75;
  rows.forEach(([n, b, k, d], i) => {
    card(s, M, y, W - 2 * M, 0.6, i % 2 === 0 ? "2E3E4C" : INK);
    s.addText(n, {
      x: M + 0.35, y: y + 0.13, w: 5.2, h: 0.35,
      fontFace: "Consolas", fontSize: 14, color: "CBD5DD", margin: 0,
    });
    s.addText(b, {
      x: M + 6.0, y: y + 0.13, w: 1.4, h: 0.35,
      fontFace: B, fontSize: 14, color: MUTED, align: "right", margin: 0,
    });
    s.addText(k, {
      x: M + 7.7, y: y + 0.13, w: 1.4, h: 0.35,
      fontFace: B, fontSize: 14, color: PAPER, align: "right", margin: 0,
    });
    s.addText(d, {
      x: M + 9.6, y: y + 0.12, w: 2.2, h: 0.38,
      fontFace: H, fontSize: 16, bold: true, color: TEAL, align: "right", margin: 0,
    });
    y += 0.66;
  });

  s.addText("29 paired observations · mean +28 pts · 95% CI +12 to +44 · p = 0.009", {
    x: M, y: 5.85, w: W - 2 * M, h: 0.4,
    fontFace: B, fontSize: 15, color: "CBD5DD", margin: 0,
  });
  s.addText("Single model, single session, synthetic warehouse, authors' own evals.", {
    x: M, y: 6.25, w: W - 2 * M, h: 0.4,
    fontFace: B, fontSize: 13, italic: true, color: MUTED, margin: 0,
  });
  s.addNotes("Lead with the number, then immediately give the caveats on the next slide. The mean and median agree (+28.2 / +27.8), so it is not one outlier carrying the result. Say plainly that this is one run by the people who wrote the skills.");
}

// ================================================================ 13 THE CAVEATS
{
  const s = lightSlide();
  kicker(s, "What the headline hides");
  title(s, "Three things that belong with that number");

  card(s, M, 1.8, W - 2 * M, 1.35, "FBEDE8");
  s.addText("Skills over-fire. Negative tests fell 87% to 70%.", {
    x: M + 0.4, y: 2.02, w: W - 2 * M - 0.8, h: 0.42,
    fontFace: H, fontSize: 22, bold: true, color: ORANGE, margin: 0,
  });
  s.addText("The worst case attaches a full provenance footer to a schema lookup. A real cost, not noise.", {
    x: M + 0.4, y: 2.5, w: W - 2 * M - 0.8, h: 0.45,
    fontFace: B, fontSize: 15, color: "8C4430", margin: 0,
  });

  card(s, M, 3.3, W - 2 * M, 1.35, TINT);
  s.addText("Five runs died on the turn budget — and not at random.", {
    x: M + 0.4, y: 3.52, w: W - 2 * M - 0.8, h: 0.42,
    fontFace: H, fontSize: 22, bold: true, color: INK, margin: 0,
  });
  s.addText("Four of the five were in the slice reporting the largest gain. Losing the hardest runs biases the estimate upward.", {
    x: M + 0.4, y: 4.0, w: W - 2 * M - 0.8, h: 0.45,
    fontFace: B, fontSize: 15, color: SLATE, margin: 0,
  });

  card(s, M, 4.8, W - 2 * M, 1.5, "E6F2EE");
  s.addText("It survives the sensitivity analysis anyway.", {
    x: M + 0.4, y: 5.02, w: W - 2 * M - 0.8, h: 0.42,
    fontFace: H, fontSize: 22, bold: true, color: TEAL, margin: 0,
  });
  s.addText("Drop every eval with a failed run: +22. Assume every lost run scored zero: +23. The honest headline is roughly +20 to +28 with a measurable over-firing cost.", {
    x: M + 0.4, y: 5.5, w: W - 2 * M - 0.8, h: 0.65,
    fontFace: B, fontSize: 15, color: "1F5F4C", margin: 0,
  });
  s.addNotes("This slide is the point of the workshop. Anyone can report +28. Reporting +28 alongside the over-firing cost, the non-random missing data, and a sensitivity analysis is what makes it trustworthy. Note that the censoring problem here is exactly pattern 2 in analysis-patterns.md — we hit it in our own measurement.");
}

// ================================================================ 13B THE LOAD-ALL TEST
{
  const s = darkSlide();
  kicker(s, "One variable, isolated", ORANGE);
  title(s, "Loading everything doesn't break accuracy. It breaks discipline.", { color: PAPER, size: 30 });

  s.addText("Same skills, same model, same warehouse. Only the loading strategy changed: one relevant skill vs. all six, every question.", {
    x: M, y: 1.55, w: W - 2 * M, h: 0.55,
    fontFace: B, fontSize: 15, color: "CBD5DD", margin: 0,
  });

  const cw = 3.85;
  const rows = [
    ["Accuracy", "No measurable difference", "-3.1 pts  ·  95% CI -10.3 to +4.2", "Crosses zero. 8 up, 10 down, 11 flat — indistinguishable from noise.", MUTED],
    ["Discipline", "Erodes as loading gets less targeted", "87% → 83% → 74%", "Negative-test pass rate, baseline → per-slice → load-all. Monotonic.", ORANGE],
    ["Efficiency", "More context, more wasted turns", "4 runs lost vs. 0", "Turn-budget exhaustion under load-all. Same cap, more to wade through.", ORANGE],
  ];
  let x = M;
  rows.forEach(([h, sub, stat, detail, accent]) => {
    card(s, x, 2.35, cw, 3.9, "2E3E4C");
    s.addText(h.toUpperCase(), {
      x: x + 0.3, y: 2.58, w: cw - 0.6, h: 0.35,
      fontFace: B, fontSize: 12, bold: true, charSpacing: 1.5, color: MUTED, margin: 0,
    });
    s.addText(sub, {
      x: x + 0.3, y: 2.95, w: cw - 0.6, h: 0.7,
      fontFace: H, fontSize: 17, bold: true, color: PAPER, margin: 0,
    });
    s.addText(stat, {
      x: x + 0.3, y: 3.75, w: cw - 0.6, h: 0.7,
      fontFace: H, fontSize: 24, bold: true, color: accent, margin: 0,
    });
    s.addText(detail, {
      x: x + 0.3, y: 4.55, w: cw - 0.6, h: 1.5,
      fontFace: B, fontSize: 13, color: "CBD5DD", margin: 0,
    });
    x += cw + 0.42;
  });

  s.addText("The routing argument isn't “dilution makes the model dumber.” It's “dilution makes the model less careful about when to apply what it knows.”", {
    x: M, y: 6.55, w: W - 2 * M, h: 0.6,
    fontFace: H, fontSize: 16, italic: true, color: PAPER, margin: 0,
  });
  s.addNotes("This is the sharper, more defensible version of the routing argument. The earlier broken run suggested loading everything tanks accuracy outright (-9) -- that was a harness bug, not a finding. The clean isolation shows something more interesting and more true: raw task performance barely moves, but the agent's judgment about when a rule applies degrades measurably, and it burns more of its own turn budget doing so. That is a better argument for a thin router than a scarier, less accurate one would have been.");
}

// ================================================================ 14 FABRICATION
{
  const s = lightSlide();
  kicker(s, "What kept happening");
  title(s, "Five fabrications, all caught only by running the query");

  const rows = [
    ["An invented performance-tier table", "Looked entirely plausible. Wrong in every cell."],
    ["A wrong department-drop figure", "Right shape, wrong number."],
    ["A correct figure in the wrong context", "2,008 quoted where 1,668 applied."],
    ["A skew example with no skew", "The data was symmetric. The claim implied otherwise."],
    ["A 0/0 result written to disk", "Zero evals ran. It reported as a 0% score."],
  ];
  let y = 1.9;
  rows.forEach(([l, r], i) => {
    card(s, M, y, W - 2 * M, 0.72, i % 2 === 0 ? TINT : PAPER);
    s.addText(l, {
      x: M + 0.35, y: y + 0.16, w: 5.6, h: 0.4,
      fontFace: B, fontSize: 15, bold: true, color: INK, margin: 0,
    });
    s.addText(r, {
      x: M + 6.1, y: y + 0.16, w: 5.7, h: 0.4,
      fontFace: B, fontSize: 14, color: SLATE, margin: 0,
    });
    y += 0.78;
  });

  s.addText("Every one was fluent, plausible, and would have passed review. Run the query.", {
    x: M, y: 6.15, w: W - 2 * M, h: 0.5,
    fontFace: H, fontSize: 19, italic: true, bold: true, color: ORANGE, margin: 0,
  });
  s.addNotes("These happened while building the pack whose entire purpose is preventing them. That is not embarrassing, it is the point — the failure mode is structural, not a matter of care. Tell this story; it lands harder than any abstract warning.");
}

// ================================================================ 15 AGENDA
{
  const s = lightSlide();
  kicker(s, "Today");
  title(s, "Three hours");

  const rows = [
    ["0:00", "Why coding agents worked first", "Framing"],
    ["0:20", "The failure demo", "Watch an agent answer confidently and wrong"],
    ["0:40", "Define — your own recurring question", "Hands on"],
    ["1:00", "Validate — write the evals first", "Hands on"],
    ["1:30", "Build — author the skill", "Hands on, the main block"],
    ["2:15", "Run the ablation", "Measure it"],
    ["2:35", "Operationalize and compound", "How skills stay alive"],
    ["2:50", "Contribute and wrap", "PR to the repo"],
  ];
  let y = 1.65;
  rows.forEach(([t, l, d], i) => {
    const hot = l.startsWith("Build");
    card(s, M, y, W - 2 * M, 0.6, hot ? "FBEDE8" : (i % 2 === 0 ? TINT : PAPER));
    s.addText(t, {
      x: M + 0.35, y: y + 0.13, w: 0.9, h: 0.35,
      fontFace: "Consolas", fontSize: 14, bold: true, color: hot ? ORANGE : MUTED, margin: 0,
    });
    s.addText(l, {
      x: M + 1.45, y: y + 0.12, w: 6.5, h: 0.38,
      fontFace: B, fontSize: 15, bold: true, color: hot ? ORANGE : INK, margin: 0,
    });
    s.addText(d, {
      x: M + 8.1, y: y + 0.13, w: 3.7, h: 0.35,
      fontFace: B, fontSize: 13, color: hot ? "8C4430" : SLATE, margin: 0,
    });
    y += 0.66;
  });
  s.addNotes("One workflow end to end. Everything else ships as reference material they take home. Depth over coverage.");
}

// ================================================================ 16 CLOSE
{
  const s = darkSlide();
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 1.8, w: 0.14, h: 3.4, rectRadius: 0.07,
    fill: { color: ORANGE }, line: { color: ORANGE, width: 0 },
  });
  s.addText("What you take home", {
    x: M + 0.45, y: 1.75, w: 10, h: 0.7,
    fontFace: H, fontSize: 38, bold: true, color: PAPER, margin: 0,
  });
  s.addText([
    { text: "A skill you wrote, running in your own environment", options: { bullet: true, breakLine: true } },
    { text: "An eval that proves it does something", options: { bullet: true, breakLine: true } },
    { text: "A reference doc for a domain you actually own", options: { bullet: true, breakLine: true } },
    { text: "A merged PR and your name in the README", options: { bullet: true, breakLine: true } },
    { text: "The habit of running the query instead of trusting the number", options: { bullet: true } },
  ], {
    x: M + 0.45, y: 2.65, w: 10.5, h: 2.6,
    fontFace: B, fontSize: 17, color: "CBD5DD", paraSpaceAfter: 12, margin: 0,
  });
  s.addText("github.com/RobStilson/analytics-skills", {
    x: M + 0.45, y: 5.7, w: 10, h: 0.4,
    fontFace: "Consolas", fontSize: 16, bold: true, color: ORANGE, margin: 0,
  });
  s.addNotes("Close on the habit, not the artifact. The skills will go stale; the discipline of verifying instead of eyeballing is what survives.");
}

pres.writeFile({ fileName: "vibe-analytics-workshop.pptx" })
  .then(f => console.log("written:", f));
