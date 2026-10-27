import { NextResponse } from 'next/server';
import { answer } from '../../../lib/research.js';
import { checkRequest } from '../../../lib/guardrails.js';
export async function POST(req) {
  try {
    const { question } = await req.json();
    const gate = checkRequest(question || '');
    if (gate.blocked) return NextResponse.json({ found: false, answer: gate.reason, citations: [] });
    return NextResponse.json(answer(question || ''));
  } catch (e) {
    return NextResponse.json({ found: false, answer: 'Something went wrong: ' + e.message, citations: [] }, { status: 500 });
  }
}
