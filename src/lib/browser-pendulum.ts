// Only browser/runtime glue lives here; simulation and drawing are in browser.py.
const runtimeUrl = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

interface PythonProxy { destroy(): void }
interface PythonPendulum extends PythonProxy {
  advance(now: number): void;
  draw(context: CanvasRenderingContext2D, width: number, height: number): void;
  reset(): void;
  pause_clock(): void;
}
interface PythonRuntime {
  runPython(source: string, options?: { globals: PythonProxy; filename?: string }): unknown;
}

let runtimePromise: Promise<PythonRuntime> | undefined;

function loadRuntime(): Promise<PythonRuntime> {
  runtimePromise ??= import(/* @vite-ignore */ runtimeUrl)
    .then(({ loadPyodide }) => loadPyodide())
    .catch((error) => { runtimePromise = undefined; throw error; });
  return runtimePromise!;
}

export function mountPendulums(source: string): void {
  document.querySelectorAll<HTMLElement>(".pendulum-demo").forEach(async (demo) => {
    const canvas = demo.querySelector("canvas");
    const reset = demo.querySelector("button");
    const status = demo.querySelector<HTMLElement>("[data-pendulum-status]");
    if (!canvas || !reset || !status) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    let pendulum: PythonPendulum | undefined;
    let frame = 0;
    let disposed = false;
    const listeners = new AbortController();
    function dispose(): void {
      disposed = true;
      cancelAnimationFrame(frame);
      listeners.abort();
      pendulum?.destroy();
      pendulum = undefined;
    }
    function fail(error: unknown): void {
      console.error("Pendulum simulation failed", error);
      dispose();
      reset!.disabled = true;
      status!.textContent = "Unable to run the simulation. Reload to try again.";
      status!.hidden = false;
    }
    function animate(now: number): void {
      if (!demo.isConnected) { dispose(); return; }
      if (disposed || !pendulum) return;
      try {
        pendulum.advance(now);
        pendulum.draw(context!, canvas!.width, canvas!.height);
        frame = requestAnimationFrame(animate);
      } catch (error) { fail(error); }
    }

    try {
      const runtime = await loadRuntime();
      if (!demo.isConnected) return;
      const namespace = runtime.runPython("dict(__name__='browser_pendulum')") as PythonProxy;
      try {
        pendulum = runtime.runPython(`${source}\nPendulum()`, {
          globals: namespace,
          filename: "simulations/pendulum/browser.py"
        }) as PythonPendulum;
      } finally { namespace.destroy(); }
      pendulum.draw(context, canvas.width, canvas.height);
      status.hidden = true;
      reset.disabled = false;
      reset.addEventListener("click", () => {
        try { pendulum?.reset(); } catch (error) { fail(error); }
      }, { signal: listeners.signal });
      window.addEventListener("pagehide", (event) => {
        cancelAnimationFrame(frame);
        if (event.persisted) pendulum?.pause_clock();
        else dispose();
      }, { signal: listeners.signal });
      window.addEventListener("pageshow", (event) => {
        if (event.persisted && !disposed) frame = requestAnimationFrame(animate);
      }, { signal: listeners.signal });
      frame = requestAnimationFrame(animate);
    } catch (error) { fail(error); }
  });
}
