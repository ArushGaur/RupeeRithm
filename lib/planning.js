// Deliverable 2: inflation-adjusted corpus, SIP, glide path. Return rates are ASSUMPTIONS, not promises.
export const inflate = (cost, rate, years) => cost * Math.pow(1 + rate, years);
export const expectedReturn = (eqPct) => (eqPct / 100) * 0.12 + (1 - eqPct / 100) * 0.07;
const mRate = (annual) => Math.pow(1 + annual, 1 / 12) - 1;
export function sipFor(fv, annual, years) {
  const r = mRate(annual), n = years * 12;
  return (fv * r) / ((Math.pow(1 + r, n) - 1) * (1 + r));
}
export function sipFV(sip, annual, years) {
  const r = mRate(annual), n = years * 12;
  return sip * ((Math.pow(1 + r, n) - 1) / r) * (1 + r);
}
export function equityAt(base, yearsLeft) {
  return yearsLeft >= 10 ? base : Math.max(10, Math.round((base * yearsLeft) / 10));
}
export function planGoal(g, equityBase) {
  const ret = expectedReturn(equityBase);
  const corpus = inflate(g.costToday, g.inflation, g.years);
  const existingFV = (g.existing || 0) * Math.pow(1 + ret, g.years);
  const gap = Math.max(0, corpus - existingFV);
  const glide = [g.years, Math.ceil(g.years / 2), 1].map((y) => ({ yearsLeft: y, equityPct: equityAt(equityBase, y) }));
  return { name: g.name, years: g.years, assumedReturn: ret, corpus, monthlySip: gap ? sipFor(gap, ret, g.years) : 0, glide };
}
