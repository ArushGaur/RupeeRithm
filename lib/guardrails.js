// Deliverable 5: code-level guardrails (not just prompt text).
const BANNED = /(guarantee|assured return|risk[- ]?free|sure[- ]?shot|can'?t lose|double my money)/i;
export const DISCLOSURE = 'Direct plans only: no commission is earned on fund selection. The adviser is paid a fee by the client. Past performance does not indicate future returns. Returns shown are assumptions, not guarantees.';
export function checkRequest(text) {
  if (BANNED.test(text)) return { blocked: true, reason: 'Returns cannot be guaranteed. Investments are subject to market risk; only assumptions and past data can be shown.' };
  return { blocked: false };
}
export function checkSuitability(client, profile, text) {
  const f = [];
  if (/small[- ]?cap/i.test(text) && (client.age >= 60 || profile.final <= 2)) f.push('Small-cap-only exposure is unsuitable for this client (age/risk profile).');
  if (/(100% ?equity|all[- ]?equity|everything in)/i.test(text) && profile.final <= 3) f.push('Full equity exposure exceeds the suitable allocation for this risk profile.');
  if (/(high returns? fast|quick(ly)?|f&o|options trading)/i.test(text) && profile.final <= 3) f.push('Expectation of fast, high returns conflicts with the risk profile. Needs adviser discussion.');
  return f;
}
// The mandatory disclosure legitimately says returns are "not guarantees", so it is removed before scanning.
export function scanOutput(text) {
  const body = text.split(DISCLOSURE).join('');
  if (BANNED.test(body)) throw new Error('Output blocked: contains guarantee language.');
  return text;
}
