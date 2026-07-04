const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";

// ── brand palette (the product's own warm terracotta) ─────────────
const INK = "1E1B16", INK2 = "4A443B", MUTED = "837C6E";
const CLAY = "C4694A", CLAY_DEEP = "A9532F", CLAYSOFT = "EAD9CF";
const PAPER = "F6F2EA", WHITE = "FFFFFF", LINE = "E2DACB";
const SAGE = "5F6B57", GOLD = "B4842E", RED = "B23B32", CREAM = "C9C2B6";
const SERIF = "Cambria", SANS = "Calibri";
const W = 13.333, M = 0.7;

const slide = (bg) => { const s = p.addSlide(); s.background = { color: bg }; return s; };
function badge(s, x, y, d, txt, fill = CLAY, tc = WHITE) {
  s.addShape("ellipse", { x, y, w: d, h: d, fill: { color: fill } });
  s.addText(txt, { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: SERIF, bold: true, color: tc, fontSize: d * 25 });
}
const kicker = (s, t, color = CLAY) => s.addText(t.toUpperCase(),
  { x: M, y: 0.52, w: W - 2 * M, h: 0.35, fontFace: SANS, bold: true, color, fontSize: 12.5, charSpacing: 2.5 });
const title = (s, t, color = INK, y = 0.92, size = 34) => s.addText(t,
  { x: M, y, w: W - 2 * M, h: 1.3, fontFace: SERIF, bold: true, color, fontSize: size, lineSpacing: size * 1.04 });
const foot = (s, t, color = MUTED) => s.addText(t,
  { x: M, y: 6.95, w: W - 2 * M, h: 0.35, fontFace: SANS, italic: true, color, fontSize: 11.5 });

// ═══ 1 · TITLE ════════════════════════════════════════════════════
let s = slide(INK);
s.addText("₹", { x: 8.6, y: 0.9, w: 5, h: 6.2, fontFace: SERIF, bold: true, color: "2A2620", fontSize: 420, align: "center", valign: "middle" });
s.addText("SBI HACKATHON   ·   AGENTIC AI FOR FINANCIAL INCLUSION", { x: M, y: 1.95, w: 11, h: 0.4, fontFace: SANS, bold: true, color: CLAY, fontSize: 13, charSpacing: 2 });
s.addText("Nischay", { x: M - 0.05, y: 2.4, w: 11, h: 1.7, fontFace: SERIF, bold: true, color: PAPER, fontSize: 100 });
s.addText([{ text: "The bank that makes sure the money ", options: { color: PAPER } }, { text: "lands", options: { color: CLAY, italic: true } }, { text: ".", options: { color: PAPER } }],
  { x: M, y: 4.15, w: 11, h: 0.7, fontFace: SERIF, fontSize: 28 });
s.addText("Getting citizens the government money they are already owed — when a dormant account,\nan unlinked Aadhaar, or a lapsed KYC would otherwise send it back.",
  { x: M, y: 5.05, w: 10.6, h: 0.9, fontFace: SANS, color: CREAM, fontSize: 15, lineSpacing: 22 });
s.addText("Mahak Choradia", { x: M, y: 6.55, w: 8, h: 0.4, fontFace: SANS, bold: true, color: PAPER, fontSize: 14 });

// ═══ 2 · THE NUMBER ═══════════════════════════════════════════════
s = slide(INK);
kicker(s, "The problem, in one number", CLAY);
s.addText("72.85%", { x: M, y: 1.75, w: 12, h: 2.7, fontFace: SERIF, bold: true, color: CLAY, fontSize: 150 });
s.addText([{ text: "of India's welfare beneficiaries have hit a payment that ", options: { color: PAPER } }, { text: "didn't arrive", options: { color: PAPER, italic: true } }, { text: ".", options: { color: PAPER } }],
  { x: M, y: 4.55, w: 11.8, h: 1.0, fontFace: SERIF, fontSize: 30, lineSpacing: 36 });
s.addText("Not stolen. Not ineligible. The money was approved and sent — and the account couldn't receive it.",
  { x: M, y: 5.75, w: 11.5, h: 0.6, fontFace: SANS, color: CREAM, fontSize: 16 });
foot(s, "Source: Dvara–Haqdarshak beneficiary survey, 2022 (N = 1,477), across five schemes in Assam, Chhattisgarh & Andhra Pradesh.", "6E665A");

// ═══ 3 · THE SILENT FAILURE ═══════════════════════════════════════
s = slide(WHITE);
kicker(s, "How it vanishes");
title(s, "Approved. Sent. Returned —\nand no one is told.");
s.addText("The government's system releases the money into a single bank account. If that account has a small technical problem, the payment is simply rejected and turns around.",
  { x: M, y: 2.55, w: 6.6, h: 1.6, fontFace: SANS, color: INK2, fontSize: 17, lineSpacing: 26 });
s.addText([{ text: "No alarm rings. No one calls. ", options: { bold: true, color: INK } }, { text: "The family it was meant for never learns it existed — and next cycle, it happens again.", options: { color: INK2 } }],
  { x: M, y: 4.35, w: 6.6, h: 1.3, fontFace: SANS, fontSize: 17, lineSpacing: 26 });
s.addShape("roundRect", { x: 8.35, y: 2.7, w: 4.1, h: 2.6, rectRadius: 0.12, fill: { color: PAPER }, line: { color: LINE, width: 1 }, shadow: { type: "outer", blur: 12, offset: 3, angle: 90, opacity: 0.16 } });
s.addText("₹2,000", { x: 8.35, y: 3.0, w: 4.1, h: 0.9, align: "center", fontFace: SERIF, bold: true, color: INK, fontSize: 44 });
s.addText("PM-KISAN  ·  for Ramesh Kumar", { x: 8.35, y: 3.9, w: 4.1, h: 0.4, align: "center", fontFace: SANS, color: MUTED, fontSize: 13 });
s.addShape("rect", { x: 9.6, y: 4.45, w: 1.6, h: 0.5, fill: { color: RED }, rotate: -4 });
s.addText("RETURNED", { x: 9.6, y: 4.45, w: 1.6, h: 0.5, align: "center", valign: "middle", fontFace: SANS, bold: true, color: WHITE, fontSize: 13, rotate: -4, charSpacing: 1 });

// ═══ 4 · THE CAUSES ARE MUNDANE ═══════════════════════════════════
s = slide(WHITE);
kicker(s, "And the data names the cause");
title(s, "Three fixable fields. Not one is fraud.");
const cd = [
  ["51.3%", "Aadhaar not seeded", "in the NPCI mapper that routes the payment — so it is rejected outright.", CLAY],
  ["32%", "KYC pending or lapsed", "a periodic identity check expired, and the account froze against new credits.", GOLD],
  ["36%", "just a spelling error", "in the name — the kind of mismatch our name-reconciliation fixes with zero contact.", SAGE],
];
cd.forEach((c, i) => {
  const x = M + i * 4.0;
  s.addText(c[0], { x, y: 2.65, w: 3.7, h: 1.0, fontFace: SERIF, bold: true, color: c[3], fontSize: 52 });
  s.addText(c[1], { x, y: 3.75, w: 3.6, h: 0.5, fontFace: SERIF, bold: true, color: INK, fontSize: 18 });
  s.addText(c[2], { x, y: 4.3, w: 3.6, h: 1.7, fontFace: SANS, color: INK2, fontSize: 14, lineSpacing: 21 });
});
s.addShape("roundRect", { x: M, y: 6.15, w: 11.9, h: 0.75, rectRadius: 0.1, fill: { color: PAPER } });
s.addText([{ text: "Every one of these sits in the bank's own database ", options: { bold: true, color: INK } }, { text: "days before the payment runs. The failure is fully predictable — it is simply never acted on.", options: { color: INK2 } }],
  { x: M + 0.3, y: 6.15, w: 11.3, h: 0.75, valign: "middle", fontFace: SANS, fontSize: 14.5 });
foot(s, "Sources: East Godavari PM-KISAN administrative data (N=39,655) and Dvara beneficiary survey, 2022.");

// ═══ 5 · THE REFRAME (the insight) ════════════════════════════════
s = slide(INK);
kicker(s, "The idea", CLAY);
title(s, "Stop rescuing payments.\nKeep every account payment-ready.", PAPER, 0.92, 33);
s.addText("Model each account as a set of fields a payment needs to land — Aadhaar seeded, KYC valid, name reconciled, account active. The agent's job is to keep every account green before the disbursement calendar event, not to firefight after it bounces.",
  { x: M, y: 2.85, w: 7.4, h: 2.0, fontFace: SANS, color: CREAM, fontSize: 17, lineSpacing: 27 });
s.addShape("roundRect", { x: 8.5, y: 2.85, w: 4.15, h: 3.4, rectRadius: 0.12, fill: { color: "2A2620" } });
s.addText("FIX ONCE, BENEFIT FOREVER", { x: 8.8, y: 3.1, w: 3.6, h: 0.4, fontFace: SANS, bold: true, color: CLAY, fontSize: 12.5, charSpacing: 1 });
s.addText("Seeding one Aadhaar or renewing one KYC unblocks every scheme, for every future cycle.",
  { x: 8.8, y: 3.55, w: 3.55, h: 1.3, fontFace: SANS, color: PAPER, fontSize: 15.5, lineSpacing: 23 });
s.addText("The return isn't per-payment. It is per-account-lifetime.",
  { x: 8.8, y: 5.15, w: 3.55, h: 0.9, fontFace: SERIF, italic: true, color: "FFD9C7", fontSize: 16, lineSpacing: 22 });

// ═══ 6 · WHY ONLY SBI ═════════════════════════════════════════════
s = slide(WHITE);
kicker(s, "Why only SBI");
title(s, "The rails exist. The auth exists.\nThe last-mile fix doesn't.");
s.addText("NPCI runs the payment rails; Aadhaar libraries do the auth; the failure data is public. What nobody has built — and only SBI can run — is the layer that predicts the failure and fixes it. It needs three things a private bank cannot buy:",
  { x: M, y: 2.6, w: 11.6, h: 1.1, fontFace: SANS, color: INK2, fontSize: 16, lineSpacing: 24 });
const moat = [
  ["Sees government payments as they route", "a primary DBT pipeline"],
  ["Accounts at village density", "~53 crore, every district"],
  ["The mandate to fix inclusion gaps", "banker to the nation"],
];
moat.forEach((r, i) => {
  const y = 3.95 + i * 0.82;
  badge(s, M, y, 0.5, "✓", SAGE);
  s.addText(r[0], { x: M + 0.72, y, w: 7.0, h: 0.5, fontFace: SANS, color: INK, fontSize: 16.5, valign: "middle" });
  s.addText("— " + r[1], { x: M + 7.7, y, w: 4.2, h: 0.5, fontFace: SANS, italic: true, color: CLAY_DEEP, fontSize: 15, valign: "middle" });
});
foot(s, "It sells nothing. It gets people money that is already theirs.", CLAY);

// ═══ 7 · CHEAPEST FIX FIRST (efficiency) ══════════════════════════
s = slide(WHITE);
kicker(s, "How — the cheapest fix first");
title(s, "Most systems would call everyone.\nWe don't.");
s.addText("Resolve in ascending order of cost and customer burden; stop the moment an account goes green. On a modelled district's at-risk cohort:",
  { x: M, y: 2.55, w: 11.6, h: 0.8, fontFace: SANS, color: INK2, fontSize: 16, lineSpacing: 24 });
const water = [
  ["22%", "Zero human contact", "already fixable from SBI's own data — the spelling-error names, a KYC done at another branch.", SAGE],
  ["+47%", "Voice / IVR", "self-serve re-KYC or one-tap reactivation, by phone. 69% resolved before anyone travels.", CLAY],
  ["27%", "Banking camp", "batched by field and village — one visit clears hundreds of unseeded Aadhaars.", GOLD],
  ["3%", "Human officer", "the genuine identity conflicts only. The gate refuses to auto-resolve these.", RED],
];
water.forEach((r, i) => {
  const x = M + i * 3.0;
  s.addText(r[0], { x, y: 3.5, w: 2.8, h: 0.8, fontFace: SERIF, bold: true, color: r[3], fontSize: 40 });
  s.addText(r[1], { x, y: 4.35, w: 2.75, h: 0.4, fontFace: SERIF, bold: true, color: INK, fontSize: 16 });
  s.addText(r[2], { x, y: 4.8, w: 2.75, h: 1.7, fontFace: SANS, color: INK2, fontSize: 13, lineSpacing: 19 });
});
foot(s, "Percentages computed by the readiness engine in this repo — deterministic, re-derivable. The cheap rungs carry the volume, so cost-per-rescue collapses.");

// ═══ 8 · WHERE THE AI IS ══════════════════════════════════════════
s = slide(WHITE);
kicker(s, "Where the AI is — and isn't");
title(s, "The AI can talk.\nIt cannot open the gate.");
s.addText("The one place that genuinely needs AI is the last hundred metres: a patient, vernacular voice conversation that renews a KYC without a branch visit and self-heals a document-name mismatch.",
  { x: M, y: 2.75, w: 6.7, h: 1.7, fontFace: SANS, color: INK2, fontSize: 17, lineSpacing: 26 });
s.addText("Every consequential decision then runs through deterministic code — a gate the conversation cannot talk its way past. The agent never moves money; anything ambiguous defaults to a human.",
  { x: M, y: 4.5, w: 6.7, h: 1.3, fontFace: SANS, color: INK2, fontSize: 17, lineSpacing: 26 });
s.addShape("roundRect", { x: 8.3, y: 2.75, w: 4.3, h: 3.0, rectRadius: 0.12, fill: { color: PAPER }, line: { color: LINE, width: 1 } });
["identity reconciled", "screening clear", "person confirmed"].forEach((t, i) => {
  s.addText([{ text: "✓  ", options: { color: SAGE, bold: true } }, { text: t, options: { color: INK } }],
    { x: 8.62, y: 3.05 + i * 0.55, w: 3.7, h: 0.45, fontFace: SANS, fontSize: 15.5, valign: "middle" });
});
s.addShape("line", { x: 8.62, y: 4.8, w: 3.6, h: 0, line: { color: LINE, width: 1 } });
s.addText([{ text: "GATE → ", options: { color: MUTED, bold: true } }, { text: "OPEN", options: { color: SAGE, bold: true } }],
  { x: 8.62, y: 4.95, w: 3.6, h: 0.6, fontFace: "Courier New", fontSize: 18, valign: "middle" });

// ═══ 9 · THE 20% + HONEST METRICS (combined honesty) ══════════════
s = slide(INK);
kicker(s, "Honesty — both kinds", CLAY);
title(s, "It names what it can't do,\nand grades what it can.", PAPER, 0.92, 32);
s.addText("The 20% it can't fix", { x: M, y: 2.85, w: 5.6, h: 0.4, fontFace: SERIF, bold: true, color: "FFD9C7", fontSize: 18 });
s.addText("No phone → a camp is scheduled. A genuine identity conflict → a human reviews it. Volunteering your own limits is the strongest signal of maturity there is.",
  { x: M, y: 3.3, w: 5.6, h: 1.8, fontFace: SANS, color: CREAM, fontSize: 15.5, lineSpacing: 24 });
s.addText("It grades itself in public", { x: 7.0, y: 2.85, w: 5.6, h: 0.4, fontFace: SERIF, bold: true, color: "FFD9C7", fontSize: 18 });
const mm = [["70%", "raw accuracy — misleading", "B98A82"], ["86%", "precision on the riskiest 10%", SAGE], ["2.1×", "better than chance", SAGE]];
mm.forEach((x, i) => {
  const yy = 3.35 + i * 0.9;
  s.addText(x[0], { x: 7.0, y: yy, w: 1.6, h: 0.7, fontFace: SERIF, bold: true, color: x[2], fontSize: 30 });
  s.addText(x[1], { x: 8.7, y: yy + 0.12, w: 4.2, h: 0.5, fontFace: SANS, color: PAPER, fontSize: 14.5, valign: "middle" });
});
foot(s, "A calibration curve and Brier score back it — reported alongside the flattering numbers, not instead of them.", "6E665A");

// ═══ 10 · IT RUNS ═════════════════════════════════════════════════
s = slide(WHITE);
kicker(s, "Not a mockup — it runs");
title(s, "Built, tested, and live on the web.");
const built = [
  ["Live now", "A ~2-minute film explains it from scratch, narrated in real Indian voices, at a public URL — nothing to install."],
  ["Real, not staged", "Name reconciliation, the gate, and the readiness engine are real server code — 66 automated tests, on CI."],
  ["Runs anywhere", "Standard-library Python; one command, auto-picks a free port. One-click deploy to Render, or GitHub Pages."],
  ["Honest data", "Synthetic and labelled as such on every screen. The logic and the voice are real; only the people are simulated."],
];
built.forEach((b, i) => {
  const x = M + (i % 2) * 6.05, y = 2.5 + Math.floor(i / 2) * 1.9;
  badge(s, x, y, 0.5, "▸", CLAYSOFT, CLAY_DEEP);
  s.addText(b[0], { x: x + 0.7, y: y - 0.05, w: 5.2, h: 0.4, fontFace: SERIF, bold: true, color: INK, fontSize: 19 });
  s.addText(b[1], { x: x + 0.7, y: y + 0.4, w: 5.2, h: 1.3, fontFace: SANS, color: INK2, fontSize: 14, lineSpacing: 20 });
});
s.addShape("roundRect", { x: M, y: 6.35, w: 11.9, h: 0.65, rectRadius: 0.1, fill: { color: INK } });
s.addText("github.com/mahakchoradia19-droid/nischay-sbi   ·   python3 app.py   ·   66 tests green",
  { x: M + 0.3, y: 6.35, w: 11.3, h: 0.65, valign: "middle", fontFace: "Courier New", color: CLAYSOFT, fontSize: 13.5 });

// ═══ 11 · THE ASK ═════════════════════════════════════════════════
s = slide(INK);
kicker(s, "The ask", CLAY);
title(s, "One district. One cycle.\nMeasured honestly.", PAPER);
s.addText("A 90-day pilot in a single SLBC lead-bank district, with permissioned access to the DBT rejection feed and account KYC status — wired to the same code that runs the demo.",
  { x: M, y: 2.9, w: 11.2, h: 1.0, fontFace: SANS, color: CREAM, fontSize: 18, lineSpacing: 28 });
s.addShape("roundRect", { x: M, y: 4.2, w: 11.9, h: 1.5, rectRadius: 0.12, fill: { color: "2A2620" } });
s.addText("The metric that matters isn't “how many did we rescue.” It is:", { x: M + 0.4, y: 4.4, w: 11.1, h: 0.5, fontFace: SANS, italic: true, color: MUTED, fontSize: 15 });
s.addText("Six months later — is the account still active, and did the next payment land on its own?", { x: M + 0.4, y: 4.85, w: 11.1, h: 0.7, fontFace: SERIF, bold: true, color: PAPER, fontSize: 21 });
s.addText("Rescuing money once is a demo. Making sure a family never misses a payment again is infrastructure.",
  { x: M, y: 6.05, w: 11.5, h: 0.6, fontFace: SANS, italic: true, color: CLAY, fontSize: 16 });

// ═══ 12 · CLOSE ═══════════════════════════════════════════════════
s = slide(INK);
s.addText("₹", { x: -1.3, y: 1.1, w: 6, h: 6, fontFace: SERIF, bold: true, color: "2A2620", fontSize: 420, align: "center", valign: "middle" });
s.addText("SBI already holds the nation's money.", { x: M, y: 2.7, w: 11.8, h: 0.9, fontFace: SERIF, color: CREAM, fontSize: 32 });
s.addText([{ text: "This makes SBI the bank that ", options: { color: PAPER } }, { text: "guarantees it lands", options: { color: CLAY, italic: true } }, { text: ".", options: { color: PAPER } }],
  { x: M, y: 3.6, w: 11.8, h: 1.4, fontFace: SERIF, bold: true, fontSize: 44, lineSpacing: 48 });
s.addText("Nischay", { x: M, y: 5.85, w: 6, h: 0.8, fontFace: SERIF, bold: true, color: PAPER, fontSize: 30 });
s.addText("SBI Hackathon  ·  Mahak Choradia", { x: 7.5, y: 6.0, w: 5.1, h: 0.5, align: "right", fontFace: SANS, color: MUTED, fontSize: 14 });

p.writeFile({ fileName: "/Users/mahakchoradia/Desktop/SBI_hackathon/docs/Nischay_SBI_Hackathon.pptx" }).then(f => console.log("wrote", f));
