// Generates SYNTHETIC sample NAV data (seeded). Replace data/funds.json with real AMFI data before the demo.
import fs from 'node:fs';
let seed = 42;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296);
const gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-9)) * Math.cos(2 * Math.PI * rnd());
const cats = { 'Large Cap Index': [0.010, 0.04], 'Flexi Cap': [0.012, 0.045], 'Short Duration': [0.006, 0.004], 'Corporate Bond': [0.0065, 0.006] };
const funds = [];
for (const [category, [mu, sd]] of Object.entries(cats)) {
  for (const k of ['A', 'B', 'C']) {
    const nav = [100];
    const bump = (rnd() - 0.5) * 0.002;
    for (let i = 0; i < 120; i++) nav.push(+(nav[i] * (1 + mu + bump + sd * gauss())).toFixed(4));
    funds.push({ name: `SAMPLE ${category} Fund ${k}`, category, plan: 'Direct', expense: +(0.2 + rnd() * 0.9).toFixed(2), aum: Math.round(800 + rnd() * 9000), tenure: +(3 + rnd() * 8).toFixed(1), trackingError: category === 'Large Cap Index' ? +(0.1 + rnd() * 0.4).toFixed(2) : 0, nav });
  }
}
fs.writeFileSync('data/funds.json', JSON.stringify(funds));
console.log('wrote', funds.length, 'sample funds');
