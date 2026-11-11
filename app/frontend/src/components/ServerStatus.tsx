import { useEffect, useState } from "react";
import { getHealth } from "../api";

export type ServerState = "waking" | "ready" | "down";

const POLL_MS = 3_000;
const GIVE_UP_MS = 90_000;

/** Polls /api/health until the backend answers. Free hosts sleep when idle, so the first call can take a minute. */
export function useServerStatus(): ServerState {
  const [state, setState] = useState<ServerState>("waking");
  useEffect(() => {
    let cancelled = false;
    const started = Date.now();
    let timer: ReturnType<typeof setTimeout>;
    const tick = async () => {
      try {
        await getHealth();
        if (!cancelled) setState("ready");
      } catch {
        if (cancelled) return;
        if (Date.now() - started > GIVE_UP_MS) setState("down");
        else timer = setTimeout(tick, POLL_MS);
      }
    };
    tick();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);
  return state;
}

export function ServerBanner({ state }: { state: ServerState }) {
  if (state === "ready") return null;
  return (
    <div className={`banner ${state}`} role="status">
      {state === "waking"
        ? "Waking the server. On the free plan this can take up to a minute."
        : "The server did not respond. Please reload the page in a minute."}
    </div>
  );
}
