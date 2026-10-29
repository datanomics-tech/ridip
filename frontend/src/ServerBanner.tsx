import { useEffect, useState } from "react";
import { onServerStatus } from "./api";

/** Explains the free server's wake-up time instead of leaving a blank page. */
export default function ServerBanner() {
  const [status, setStatus] = useState<"ok" | "waking" | "down">("ok");
  useEffect(() => onServerStatus(setStatus), []);
  if (status === "ok") return null;
  return (
    <div className={`server-banner ${status}`} role="status" aria-live="polite">
      {status === "waking"
        ? "The server is waking up (free hosting sleeps when idle). This can take up to a minute; the page will load by itself."
        : "The server could not be reached. Please refresh the page in a minute."}
    </div>
  );
}
