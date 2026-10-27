import { NextResponse } from 'next/server';
import fs from 'node:fs';
import path from 'node:path';
import { riskProfile } from '../../../lib/risk.js';
import { planGoal } from '../../../lib/planning.js';
import { buildPortfolio } from '../../../lib/portfolio.js';
import { checkRequest, checkSuitability, DISCLOSURE, scanOutput } from '../../../lib/guardrails.js';
const personas = () => JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', 'personas.json'), 'utf8'));
export async function GET() { return NextResponse.json(personas()); }
export async function POST(req) {
  try {
  const { personaId, request } = await req.json();
  const client = personas().find((p) => p.id === personaId);
  if (!client) return NextResponse.json({ error: 'Unknown persona' }, { status: 400 });
  const gate = checkRequest(request || '');
  if (gate.blocked) return NextResponse.json({ status: 'BLOCKED', reason: gate.reason });
  const profile = riskProfile(client);
  const flags = checkSuitability(client, profile, request || '');
  const goals = client.goals.map((g) => planGoal(g, profile.equityBase));
  const portfolio = buildPortfolio(profile.equityBase);
  const result = { status: 'DRAFT', client, profile, flags, goals, portfolio, disclosure: DISCLOSURE };
  scanOutput(JSON.stringify(result));
  return NextResponse.json(result);
  } catch (e) {
    return NextResponse.json({ status: 'ERROR', reason: e.message }, { status: 500 });
  }
}
