// Deliverable 1: risk capacity (facts) vs risk tolerance (behaviour), combined by "lower of the two".
const clamp = (s) => Math.min(5, Math.max(1, s));
export function capacityScore(c) {
  const horizon = Math.max(...c.goals.map((g) => g.years));
  let s = 3;
  s += horizon >= 10 ? 1 : horizon <= 3 ? -1 : 0;
  s += c.stability >= 4 ? 1 : c.stability <= 2 ? -1 : 0;
  s += c.dependants >= 3 ? -1 : 0;
  s += c.emiRatio >= 0.4 ? -1 : 0;
  s += c.emergencyMonths < 3 ? -1 : 0;
  s += c.age >= 60 ? -2 : 0;
  return clamp(s);
}
const EQUITY_BASE = { 1: 20, 2: 35, 3: 50, 4: 65, 5: 80 };
export function riskProfile(c) {
  const capacity = capacityScore(c);
  const tolerance = c.tolerance; // 1-5 from questionnaire
  const final = Math.min(capacity, tolerance);
  const why = capacity === tolerance
    ? `Capacity and tolerance agree at ${final}/5.`
    : `Capacity is ${capacity}/5 and tolerance is ${tolerance}/5, so the LOWER value (${final}/5) is used. ` +
      (tolerance > capacity ? 'Client is willing to take risk but cannot afford large losses.' : 'Client can afford risk but is uncomfortable with falls, which could cause panic selling.');
  return { capacity, tolerance, final, equityBase: EQUITY_BASE[final], explanation: why };
}
