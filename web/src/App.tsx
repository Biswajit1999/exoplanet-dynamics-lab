import { Database, Pause, Play, RotateCcw, Search, ShieldCheck } from "lucide-react";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";

type Summary = {
  archive_rows_surveyed: number;
  confirmed_planets: number;
  host_systems: number;
  multi_planet_systems: number;
  high_multiplicity_systems: number;
  tier_a_systems: number;
  tier_b_systems: number;
  near_commensurate_pairs: number;
  data_last_synchronised: string;
};

type SystemRow = {
  canonical_system_id: string;
  canonical_host: string;
  n_planets: number;
  multiplicity_class: string;
  tier: string;
  is_transiting: boolean;
  is_rv_detected: boolean;
  data_completeness: number;
  dynamical_reconstruction_confidence: number;
};

export type Track = { x: number[]; y: number[]; z: number[]; a: number[]; e: number[]; inc: number[] };
export type Simulation = {
  system: string;
  stellar_mass_solar: number;
  time_years: number[];
  trajectories: Record<string, Track>;
  data_kind: "simulated";
  assumptions: string[];
};

const colors = ["#8bd3ff", "#f2c879", "#f49f7a", "#b8dd9a", "#c5acf4", "#efb9d0"];
const nf = new Intl.NumberFormat("en-GB");
const OrbitalCanvas = lazy(() => import("./OrbitalCanvas"));

function Stat({ label, value }: { label: string; value: number }) {
  return <div className="stat"><strong>{nf.format(value)}</strong><span>{label}</span></div>;
}

function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [systems, setSystems] = useState<SystemRow[]>([]);
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(1);
  const [query, setQuery] = useState("");
  useEffect(() => {
    Promise.all([
      fetch("./data/archive_summary.json").then((response) => response.json()),
      fetch("./data/systems.json").then((response) => response.json()),
      fetch("./data/selected_system.json").then((response) => response.json()),
    ]).then(([summaryData, systemsData, simulationData]) => {
      setSummary(summaryData); setSystems(systemsData); setSimulation(simulationData);
    });
  }, []);
  const filtered = useMemo(() => systems.filter((system) => system.canonical_host.toLowerCase().includes(query.toLowerCase())).slice(0, 40), [systems, query]);

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="EXODYNAMICS home"><span className="mark" aria-hidden="true" />EXODYNAMICS</a>
        <nav aria-label="Primary navigation"><a href="#laboratory">Laboratory</a><a href="#atlas">Atlas</a><a href="#methods">Methods</a></nav>
        <span className="sync">Archive-synchronised</span>
      </header>
      <main id="main">
        <section className="hero" id="top">
          <div className="hero-copy">
            <p className="eyebrow">Public archives → reconstructed dynamics → observable signatures</p>
            <h1>Multi-planet<br /><em>systems in motion.</em></h1>
            <p className="lede">A reproducible computational astrophysics platform built from measured exoplanet architectures—not invented worlds.</p>
            <div className="hero-actions"><a className="button primary" href="#laboratory"><Play size={17} aria-hidden="true" />Open the laboratory</a><a className="button secondary" href="#methods">Read the methods</a></div>
          </div>
          <div className="stats-panel" aria-label="Live archive survey statistics">
            {summary ? <><Stat label="genuine archive rows" value={summary.archive_rows_surveyed} /><Stat label="confirmed planets" value={summary.confirmed_planets} /><Stat label="multi-planet systems" value={summary.multi_planet_systems} /><Stat label="Tier A reconstructions" value={summary.tier_a_systems} /></> : <p>Loading timestamped survey…</p>}
          </div>
        </section>

        <section className="laboratory" id="laboratory">
          <div className="section-heading"><div><p className="eyebrow">01 / Dynamical laboratory</p><h2>{simulation?.system ?? "Archive-selected system"}</h2></div><div className="kind-badge"><span /> SIMULATED TRAJECTORY</div></div>
          <div className="lab-grid">
            <div className="viewport">
              {simulation && <Suspense fallback={<div className="scene-loading">Loading orbital renderer…</div>}><OrbitalCanvas simulation={simulation} playing={playing} speed={speed} /></Suspense>}
              <div className="scale-note">Orbital distance scaled uniformly · planet radii exaggerated</div>
            </div>
            <aside className="controls" aria-label="Simulation controls">
              <p className="control-label">Playback</p>
              <div className="control-row"><button onClick={() => setPlaying(!playing)} aria-pressed={playing}>{playing ? <Pause aria-hidden="true" /> : <Play aria-hidden="true" />}{playing ? "Pause" : "Play"}</button><button onClick={() => setSpeed(1)}><RotateCcw aria-hidden="true" />Reset speed</button></div>
              <label htmlFor="speed">Time multiplier <strong>{speed.toFixed(1)}×</strong></label><input id="speed" type="range" min="0.2" max="5" step="0.2" value={speed} onChange={(event) => setSpeed(Number(event.target.value))} />
              <div className="evidence"><ShieldCheck aria-hidden="true" /><div><strong>Reconstruction evidence</strong><p>Archive-selected Tier A architecture. Unknown nodes and phases use disclosed project priors.</p></div></div>
              <h3>Planet key</h3><ul className="planet-key">{simulation && Object.keys(simulation.trajectories).map((name, index) => <li key={name}><span style={{ background: colors[index % colors.length] }} />{name}</li>)}</ul>
            </aside>
          </div>
          <p className="caption">This 10-year WHFast trajectory is a model reconstructed from NASA Exoplanet Archive default parameters. It is not a direct image and does not establish gigayear stability.</p>
        </section>

        <section className="atlas" id="atlas">
          <div className="section-heading"><div><p className="eyebrow">02 / Population atlas</p><h2>Measured architectures, indexed.</h2></div><p className="section-note">Exact archive host identities · first 1,000 multi-planet systems</p></div>
          <label className="search"><Search aria-hidden="true" /><span className="sr-only">Search systems</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search a host, for example K2-138" /></label>
          <div className="table-wrap"><table><caption className="sr-only">Detected multi-planet systems and evidence coverage</caption><thead><tr><th>Host</th><th>Planets</th><th>Tier</th><th>Transit</th><th>RV</th><th>Evidence coverage</th></tr></thead><tbody>{filtered.map((system) => <tr key={system.canonical_system_id}><td><strong>{system.canonical_host}</strong><small>{system.canonical_system_id}</small></td><td>{system.n_planets}</td><td><span className={`tier tier-${system.tier.toLowerCase()}`}>{system.tier}</span></td><td>{system.is_transiting ? "Available" : "Not flagged"}</td><td>{system.is_rv_detected ? "Available" : "Not flagged"}</td><td><div className="meter"><span style={{ width: `${system.dynamical_reconstruction_confidence}%` }} /></div><small>{system.dynamical_reconstruction_confidence.toFixed(0)} / 100</small></td></tr>)}</tbody></table></div>
        </section>

        <section className="methods" id="methods">
          <div><p className="eyebrow">03 / Evidence chain</p><h2>Every result should answer: where did this come from?</h2></div>
          <ol className="pipeline"><li><Database aria-hidden="true" /><strong>Public source rows</strong><span>NASA Exoplanet Archive TAP snapshots with query, timestamp and SHA-256.</span></li><li><strong>System identity</strong><span>Exact canonical archive host names; no fuzzy joins.</span></li><li><strong>Parameter evidence</strong><span>Measured, derived, prior and unknown states remain distinct.</span></li><li><strong>N-body model</strong><span>REBOUND WHFast/IAS15 with conservation checks.</span></li><li><strong>Observable</strong><span>Predictions remain visibly separate from observed telescope data.</span></li></ol>
          <div className="disclosure"><strong>Observation status</strong><p>MAST light curves, DACE radial velocities, Gaia crossmatches and observed TTV comparisons are implemented as planned interfaces but are not claimed as analysed in this snapshot. No synthetic signal is displayed as an observation.</p></div>
          {summary && <p className="timestamp">Data last synchronised: {new Date(summary.data_last_synchronised).toLocaleString("en-GB", { timeZone: "UTC", dateStyle: "long", timeStyle: "short" })} UTC</p>}
        </section>
      </main>
      <footer><span>EXODYNAMICS v0.1.0</span><span>Open methods · explicit assumptions · reproducible results</span></footer>
    </div>
  );
}

export default App;
