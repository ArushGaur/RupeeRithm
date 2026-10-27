// Deliverable 3: fund shortlist + backtest. Data: data/funds.json (monthly NAV series).
import fs from 'node:fs';
import path from 'node:path';
export const loadFunds = () => JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', 'funds.json'), 'utf8'));
const rets = (nav) => nav.slice(1).map((v, i) => v / nav[i] - 1);
export const cagr = (nav) => Math.pow(nav.at(-1) / nav[0], 12 / (nav.length - 1)) - 1;
export function maxDrawdown(nav) { let p = nav[0], m = 0; for (const v of nav) { p = Math.max(p, v); m = Math.min(m, v / p - 1); } return m; }
export function vol(nav) { const r = rets(nav), m = r.reduce((a, b) => a + b) / r.length; return Math.sqrt(r.reduce((a, b) => a + (b - m) ** 2, 0) / (r.length - 1)) * Math.sqrt(12); }
export function rolling3y(nav) { const o = []; for (let i = 36; i < nav.length; i++) o.push(Math.pow(nav[i] / nav[i - 36], 1 / 3) - 1); o.sort((a, b) => a - b); return o[Math.floor(o.length / 2)]; }
export function score(f) {
  return rolling3y(f.nav) * 100 - f.expense * 3 + maxDrawdown(f.nav) * 10 - (f.trackingError || 0) * 5;
}
const MIX = { equity: { 'Large Cap Index': 0.5, 'Flexi Cap': 0.5 }, debt: { 'Short Duration': 0.6, 'Corporate Bond': 0.4 } };
export function buildPortfolio(equityPct, funds = loadFunds()) {
  const picks = [];
  for (const [bucket, cats] of Object.entries(MIX)) {
    const share = bucket === 'equity' ? equityPct / 100 : 1 - equityPct / 100;
    for (const [cat, w] of Object.entries(cats)) {
      const ok = funds.filter((f) => f.category === cat && f.plan === 'Direct' && f.aum >= 500 && f.tenure >= 3);
      if (!ok.length) continue;
      const best = ok.sort((a, b) => score(b) - score(a))[0];
      picks.push({ fund: best, weight: share * w, why: `Best score in ${cat}: expense ${best.expense}%, AUM ₹${best.aum} cr, manager ${best.tenure} yrs, 3y rolling median ${(rolling3y(best.nav) * 100).toFixed(1)}%` });
    }
  }
  const total = picks.reduce((a, p) => a + p.weight, 0);
  picks.forEach((p) => (p.weight /= total));
  return { picks: picks.map((p) => ({ name: p.fund.name, category: p.fund.category, weight: p.weight, why: p.why })), backtest: backtest(picks) };
}
export function backtest(picks) {
  const n = Math.min(...picks.map((p) => p.fund.nav.length));
  const port = [100];
  for (let i = 1; i < n; i++) port.push(port[i - 1] * (1 + picks.reduce((a, p) => a + p.weight * (p.fund.nav[i] / p.fund.nav[i - 1] - 1), 0)));
  return { months: n - 1, cagr: cagr(port), volatility: vol(port), maxDrawdown: maxDrawdown(port), note: 'Past performance, not a prediction. Monthly rebalanced.' };
}
