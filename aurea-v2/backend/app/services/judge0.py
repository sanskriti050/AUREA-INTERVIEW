"""Code execution — Judge0 (production) with local Python fallback (dev)."""
from __future__ import annotations
import asyncio
import base64
import subprocess
import sys
import tempfile
import os
import httpx
from app.core.config import settings

LANGUAGE_IDS = {
    "Python": 71,
    "Java": 62,
    "JavaScript": 63,
    "C++": 54,
}

# ── Local Python sandbox (dev fallback) ───────────────────────────────────────
async def _execute_python_locally(code: str, stdin: str = "") -> dict:
    """Run Python code in a subprocess with timeout. DEV ONLY — not sandboxed."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp = f.name

        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [sys.executable, tmp],
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            ),
            timeout=12,
        )
        os.unlink(tmp)
        return {
            "stdout": result.stdout[:4000],
            "stderr": result.stderr[:2000],
            "compile_output": "",
            "status": "Accepted" if result.returncode == 0 else "Runtime Error",
            "time": None,
            "memory": None,
            "note": "⚠️ Local execution (dev mode). Add JUDGE0_API_KEY for production.",
        }
    except asyncio.TimeoutError:
        return {"stdout": "", "stderr": "Time Limit Exceeded (10s)", "compile_output": "", "status": "Time Limit Exceeded", "time": "10+", "memory": None}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "compile_output": "", "status": "Internal Error", "time": None, "memory": None}


# ── Judge0 (production) ───────────────────────────────────────────────────────
async def _execute_judge0(language: str, code: str, stdin: str = "") -> dict:
    lang_id = LANGUAGE_IDS.get(language)
    if not lang_id:
        return {"stdout": "", "stderr": f"Unsupported language: {language}", "compile_output": "", "status": "Error", "time": None, "memory": None}

    headers = {
        "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "Content-Type": "application/json",
    }
    payload = {
        "language_id": lang_id,
        "source_code": base64.b64encode(code.encode()).decode(),
        "stdin": base64.b64encode(stdin.encode()).decode() if stdin else "",
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            url = f"{settings.JUDGE0_BASE_URL}/submissions?base64_encoded=true&wait=true"
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException:
        return {"stdout": "", "stderr": "Judge0 request timed out.", "compile_output": "", "status": "Timeout", "time": None, "memory": None}
    except httpx.HTTPStatusError as e:
        return {"stdout": "", "stderr": f"Judge0 error: {e.response.status_code}", "compile_output": "", "status": "API Error", "time": None, "memory": None}

    def _decode(val: str | None) -> str:
        if not val:
            return ""
        try:
            return base64.b64decode(val).decode("utf-8", errors="replace")
        except Exception:
            return val

    return {
        "stdout": _decode(data.get("stdout")),
        "stderr": _decode(data.get("stderr")),
        "compile_output": _decode(data.get("compile_output")),
        "status": data.get("status", {}).get("description", "Unknown"),
        "time": data.get("time"),
        "memory": data.get("memory"),
    }


# ── Public interface ──────────────────────────────────────────────────────────
async def execute_code(language: str, code: str, stdin: str = "") -> dict:
    """
    Execute code:
    - If JUDGE0_API_KEY is set → use Judge0 (all languages, sandboxed)
    - Otherwise → local Python fallback (Python only, dev mode)
    """
    if settings.JUDGE0_API_KEY:
        return await _execute_judge0(language, code, stdin)

    if language == "Python":
        return await _execute_python_locally(code, stdin)

    return {
        "stdout": "",
        "stderr": "",
        "compile_output": "",
        "status": f"Configure JUDGE0_API_KEY in .env to run {language} code.",
        "time": None,
        "memory": None,
        "note": "Add your free Judge0 key from rapidapi.com/judge0-official/api/judge0-ce",
    }
