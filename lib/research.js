// Deliverable 4: retrieval over document chunks (data/docs.json). Extractive answers only, with citations.
import fs from 'node:fs';
import path from 'node:path';
const STOP = new Set('the and for what which how does with this that from are is of in to a an on'.split(' '));
const toks = (s) => s.toLowerCase().match(/[a-z0-9]+/g)?.filter((w) => w.length > 2 && !STOP.has(w)) ?? [];
export const loadDocs = () => JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', 'docs.json'), 'utf8'));
export function answer(question, docs = loadDocs()) {
  const q = new Set(toks(question));
  const ranked = docs.map((d) => ({ d, s: toks(d.text).filter((w) => q.has(w)).length })).sort((a, b) => b.s - a.s);
  if (!ranked.length || ranked[0].s < 2) return { found: false, answer: 'I could not find this in the provided sources.', citations: [] };
  const top = ranked[0].d;
  return { found: true, answer: top.text, citations: [{ source: top.source, page: top.page }] };
}
