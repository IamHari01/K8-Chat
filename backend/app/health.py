"""Health, readiness, and eLife uptime checks for the Enterprise RAG API."""

import time
import logfire
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.services.health.connection_checker import check_all_connections

router = APIRouter(tags=["health"])

_START_TIME = time.time()


@router.get("/health")
def health():
    """Liveness probe — returns 200 if the process is running."""
    return {"status": "ok", "uptime_seconds": round(time.time() - _START_TIME, 2)}


@router.get("/ready")
def ready(request: Request):
    """
    Readiness probe — verifies that critical external dependencies are reachable.
    Returns 200 only if Postgres, Redis, Qdrant, the LLM gateway, Jina Embeddings,
    and Jina Reranker are all healthy.
    """
    results = check_all_connections()
    checks = {name: result.to_dict()["status"] for name, result in results.items()}
    healthy = all(r.healthy for r in results.values())

    if not healthy:
        logfire.warning("Readiness check failed", checks=checks)

    status_code = 200 if healthy else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if healthy else "not_ready", "checks": checks},
    )


@router.get("/elife")
def elife(request: Request, format: str = "json"):
    """
    eLife (Electronic Life & System Warmth Engine) endpoint.
    Returns detailed system uptime, dependency health, and cold-start protection status.
    Pass format=html or Accept: text/html to view an interactive visual dashboard.
    """
    results = check_all_connections()
    healthy_count = sum(1 for r in results.values() if r.healthy)
    total_count = len(results)
    system_status = "ALIVE" if healthy_count == total_count else ("DEGRADED" if healthy_count > 0 else "OFFLINE")

    uptime = time.time() - _START_TIME
    days, rem = divmod(int(uptime), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    checks = {name: result.to_dict() for name, result in results.items()}

    data = {
        "elife": {
            "status": system_status,
            "engine": "eLife Uptime & Heartbeat Guardian v1.0",
            "uptime": uptime_str,
            "uptime_seconds": round(uptime, 2),
            "health_score": f"{healthy_count}/{total_count}",
            "cold_start_prevention": "ACTIVE",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "dependencies": checks,
        }
    }

    if format == "html" or "text/html" in request.headers.get("accept", ""):
        dep_grid_items = "".join([
            f'<div class="dep-card {"fail" if not dep_info["healthy"] else ""}">'
            f'<div style="font-weight:bold;">{"🟢" if dep_info["healthy"] else "🔴"} {dep_name}</div>'
            f'<div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">{dep_info["status"]}</div>'
            f'</div>'
            for dep_name, dep_info in checks.items()
        ])
        status_color = "#10b981" if system_status == "ALIVE" else "#f59e0b"
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Enterprise RAG — eLife Uptime Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; max-width: 800px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
        .status-badge {{ background: {status_color}; color: #fff; padding: 6px 16px; border-radius: 20px; font-weight: bold; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }}
        .metric {{ margin-bottom: 1rem; display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #334155; }}
        .dep-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 1.5rem; }}
        .dep-card {{ background: #0f172a; padding: 12px; border-radius: 8px; border-left: 4px solid #10b981; }}
        .dep-card.fail {{ border-left-color: #ef4444; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div>
                <h1 style="margin:0; font-size: 1.5rem;">⚡ Enterprise RAG eLife Engine</h1>
                <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">24/7 Heartbeat & Anti-Inactivity Guardian</p>
            </div>
            <span class="status-badge">{system_status}</span>
        </div>
        <div class="metric"><span>System Uptime:</span><strong>{uptime_str}</strong></div>
        <div class="metric"><span>Dependency Health Score:</span><strong>{healthy_count}/{total_count}</strong></div>
        <div class="metric"><span>Cold-Start Guard:</span><strong style="color:#10b981;">ACTIVE</strong></div>
        <h3 style="margin-top: 1.5rem; font-size: 1.1rem; color: #cbd5e1;">Connected Microservices & External APIs</h3>
        <div class="dep-grid">
            {dep_grid_items}
        </div>
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_content)

    return JSONResponse(content=data)

