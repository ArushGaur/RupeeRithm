'use client';
import { useEffect, useState } from 'react';

const inr = (n) => '₹' + Math.round(n).toLocaleString('en-IN');
const pct = (n) => (n * 100).toFixed(1) + '%';
const TABS = ['Profile', 'Goal Plan', 'Portfolio', 'Research Q&A', 'Adviser Approval'];
const SUGGESTIONS = ['What is the exit load?', 'What is the minimum SIP amount?', 'What is the fund manager tenure?'];

const Meter = ({ label, value }) => (
  <div className="stat">
    <span>{label}</span>
    <b>{value}/5</b>
    <div className="meter">{[1, 2, 3, 4, 5].map((i) => <i key={i} className={i <= value ? 'f' : ''} />)}</div>
  </div>
);

export default function Home() {
  const [personas, setPersonas] = useState([]);
  const [id, setId] = useState('');
  const [req, setReq] = useState('');
  const [res, setRes] = useState(null);
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState('Profile');
  const [approved, setApproved] = useState(false);
  const [q, setQ] = useState('');
  const [ans, setAns] = useState(null);

  useEffect(() => {
    fetch('/api/plan').then((r) => r.json()).then((p) => { setPersonas(p); setId(p[0].id); setReq(p[0].request); }).catch(() => setErr('Could not load client personas.'));
  }, []);

  const pick = (p) => { setId(p.id); setReq(p.request); setRes(null); setErr(''); setApproved(false); };

  const run = async () => {
    setLoading(true); setErr(''); setApproved(false);
    try {
      const r = await fetch('/api/plan', { method: 'POST', body: JSON.stringify({ personaId: id, request: req }) });
      const data = await r.json();
      if (!r.ok) throw new Error(data.reason || data.error || 'Request failed');
      setRes(data); setTab('Profile');
    } catch (e) { setErr(e.message); setRes(null); }
    setLoading(false);
  };

  const ask = async (text) => {
    const question = typeof text === 'string' ? text : q;
    if (!question.trim()) return;
    setQ(question);
    try {
      const r = await fetch('/api/research', { method: 'POST', body: JSON.stringify({ question }) });
      setAns(await r.json());
    } catch { setAns({ found: false, answer: 'Could not reach the server.', citations: [] }); }
  };

  const draft = res?.status === 'DRAFT' ? res : null;

  return (
    <main className="wrap">
      <header className="hdr">
        <div className="logo">A</div>
        <div><h1>Adviser Co-pilot</h1><p>Goal-based planning with built-in compliance guardrails</p></div>
        <span className="badge">Direct plans only</span>
      </header>

      <section className="card">
        <span className="lbl">Client</span>
        <div className="chips">{personas.map((p) => <button key={p.id} className={'chip' + (p.id === id ? ' on' : '')} onClick={() => pick(p)}>{p.name}</button>)}</div>
        <span className="lbl">Client request</span>
        <textarea rows={2} value={req} onChange={(e) => setReq(e.target.value)} />
        <div style={{ marginTop: 12 }}><button className="btn" onClick={run} disabled={loading || !id}>{loading ? 'Generating…' : 'Generate draft plan'}</button></div>
        {err && <div className="note bad">⚠ {err}</div>}
      </section>

      <nav className="tabs">{TABS.map((t) => <button key={t} className={'tab' + (tab === t ? ' on' : '')} onClick={() => setTab(t)}>{t}</button>)}</nav>

      {res?.status === 'BLOCKED' && tab !== 'Research Q&A' && <div className="card"><div className="note bad"><b>Request blocked.</b> {res.reason}</div></div>}
      {!res && tab !== 'Research Q&A' && !err && <div className="card empty">Choose a client and click <b>Generate draft plan</b> to begin.</div>}

      {tab === 'Research Q&A' && (
        <div className="card">
          <span className="lbl">Ask about the fund documents</span>
          <div className="row">
            <input value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && ask()} placeholder="e.g. What is the exit load?" />
            <button className="btn" onClick={() => ask()}>Ask</button>
          </div>
          <div className="chips" style={{ marginTop: 12 }}>{SUGGESTIONS.map((s) => <button key={s} className="chip" onClick={() => ask(s)}>{s}</button>)}</div>
          {ans && (
            <div className="note" style={{ background: 'var(--bg)' }}>
              <p style={{ margin: '0 0 8px' }}>{ans.answer}</p>
              {ans.citations.map((c, i) => <span key={i} className="tag">{c.source} · p.{c.page}</span>)}
            </div>
          )}
        </div>
      )}

      {draft && tab === 'Profile' && (
        <div className="card">
          <div className="h"><b>{draft.client.name}</b><span className="tag">Age {draft.client.age}</span></div>
          <div className="grid">
            <Meter label="Risk capacity" value={draft.profile.capacity} />
            <Meter label="Risk tolerance" value={draft.profile.tolerance} />
            <Meter label="Final score" value={draft.profile.final} />
          </div>
          <span className="lbl" style={{ marginTop: 16 }}>Suggested base allocation</span>
          <div className="split"><div style={{ width: draft.profile.equityBase + '%' }} /><div style={{ width: 100 - draft.profile.equityBase + '%' }} /></div>
          <div className="legend"><span>Equity {draft.profile.equityBase}%</span><span>Debt {100 - draft.profile.equityBase}%</span></div>
          <p>{draft.profile.explanation}</p>
          {draft.flags.map((f, i) => <div key={i} className="note warn">⚠ {f}</div>)}
        </div>
      )}

      {draft && tab === 'Goal Plan' && draft.goals.map((g) => (
        <div key={g.name} className="card">
          <div className="h"><b>{g.name}</b><span className="tag">{g.years} {g.years === 1 ? 'year' : 'years'}</span></div>
          <div className="grid">
            <div className="stat"><span>Inflation-adjusted corpus</span><b>{inr(g.corpus)}</b></div>
            <div className="stat"><span>Monthly SIP needed</span><b>{inr(g.monthlySip)}</b></div>
            <div className="stat"><span>Assumed return</span><b>{pct(g.assumedReturn)}</b></div>
          </div>
          <p className="mut">Return is an assumption, not guaranteed.</p>
          <span className="lbl">Glide path (equity share)</span>
          <div className="glide">{g.glide.map((x, i) => (
            <div key={i}><div className="col"><i style={{ height: x.equityPct + '%' }} /></div><b>{x.equityPct}%</b>{x.yearsLeft}y left</div>
          ))}</div>
        </div>
      ))}

      {draft && tab === 'Portfolio' && (
        <div className="card">
          <div className="h"><b>Recommended funds</b></div>
          {draft.portfolio.picks.map((p) => (
            <div key={p.name} className="pick">
              <div className="top"><div><b>{p.name}</b> <span className="tag">{p.category}</span></div><b>{pct(p.weight)}</b></div>
              <div className="bar"><div style={{ width: p.weight * 100 + '%' }} /></div>
              <div className="mut" style={{ marginTop: 6 }}>{p.why}</div>
            </div>
          ))}
          <span className="lbl" style={{ marginTop: 16 }}>Backtest · {draft.portfolio.backtest.months} months</span>
          <div className="grid">
            <div className="stat"><span>CAGR</span><b>{pct(draft.portfolio.backtest.cagr)}</b></div>
            <div className="stat"><span>Volatility</span><b>{pct(draft.portfolio.backtest.volatility)}</b></div>
            <div className="stat"><span>Max drawdown</span><b>{pct(draft.portfolio.backtest.maxDrawdown)}</b></div>
          </div>
          <p className="mut">{draft.portfolio.backtest.note}</p>
        </div>
      )}

      {draft && tab === 'Adviser Approval' && (
        <div className="card">
          <div className="h"><b>Adviser sign-off</b><span className={'tag ' + (approved ? 'green' : 'amber')}>{approved ? 'Approved' : 'Draft'}</span></div>
          <p>{approved ? 'Approved and releasable to the client.' : 'Draft: not visible to the client until approved.'}</p>
          <p className="mut">{draft.disclosure}</p>
          {draft.flags.length > 0 && <div className="note warn">{draft.flags.length} suitability flag(s) on the Profile tab. Review before approving.</div>}
          {!approved
            ? <div style={{ marginTop: 12 }}><button className="btn ok" onClick={() => setApproved(true)}>Approve for client</button></div>
            : <div className="note" style={{ background: 'var(--tint)' }}>Client view: {draft.client.name}. Plan approved by adviser.{draft.flags.length ? ' Adviser noted suitability flags.' : ''}</div>}
        </div>
      )}
    </main>
  );
}
