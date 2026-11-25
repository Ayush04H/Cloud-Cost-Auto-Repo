import { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  service: string;
  rss_mb: number;
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/v1/health")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<HealthResponse>;
      })
      .then(setHealth)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        <header className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              CloudCost-Autopilot
            </h1>
            <p className="text-sm text-slate-400">
              Kubernetes FinOps &amp; OR-Tools CP-SAT Pod Bin-Packing
            </p>
          </div>
          <div className="flex items-center gap-3">
            {health ? (
              <span className="inline-flex items-center gap-2 rounded-full bg-emerald-950/60 border border-emerald-700/50 px-3 py-1 text-xs font-medium text-emerald-300">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                API Online · {health.rss_mb} MB RSS
              </span>
            ) : (
              <span className="inline-flex items-center gap-2 rounded-full bg-slate-900 border border-slate-700 px-3 py-1 text-xs text-slate-400">
                {error ? `API Offline (${error})` : "Connecting to API..."}
              </span>
            )}
          </div>
        </header>

        <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
            Phase 1 Shell Ready
          </h2>
          <p className="mt-2 text-sm text-slate-300">
            Backend proxy configured at <code className="text-sky-400">/api</code>. Node
            Packing Grid, Cost Gauge, and Gemini Policy Bar will be mounted here in Phase 5.
          </p>
        </section>
      </div>
    </main>
  );
}
