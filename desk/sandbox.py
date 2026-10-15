"""Run generated code in a constrained child process.

What the sandbox enforces (tested in tests/test_sandbox.py):
- a fresh environment: no API keys, no proxies that work (HTTP(S)_PROXY points at a closed port),
  HOME and TMPDIR inside the run directory, PYTHONHASHSEED=0, two BLAS threads;
- ``python -I -B``: no user site-packages, no PYTHONPATH, no current directory on sys.path;
- resource limits: CPU seconds, address space, largest file written, open files; a wall-clock timeout
  that kills the whole process group;
- the audit-hook, DuckDB and Arrow guards in ``_sandbox_boot.py`` (no network, no subprocesses,
  reads only from the inputs, writes only to the output directory);
- inputs are made read-only and their sha256 checked after the run.

What it does not do: it is not a security boundary against deliberately hostile code. A script can
still use ctypes, or C-extension I/O we have not wrapped. Kernel isolation (bubblewrap, user
namespaces, containers) is not available on this machine: ``unshare -rn`` and ``bwrap`` both fail
with "uid map: permission denied". The threat model is careless or confused model code, which the
guards above catch, and every script is also read by a critic before its numbers are used.
"""

from __future__ import annotations

import os
import resource
import shutil
import signal
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import PKG, sha256_file

BOOT = PKG / "_sandbox_boot.py"


@dataclass
class Limits:
    wall_s: int = 900
    cpu_s: int = 1800
    mem_mb: int = 6144          # address space; DuckDB and numpy reserve more than they touch
    file_mb: int = 512
    nofile: int = 512


@dataclass
class SandboxResult:
    returncode: int
    duration_s: float
    stdout: str
    stderr: str
    violations: list[str] = field(default_factory=list)
    timed_out: bool = False
    inputs_unchanged: bool = True

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.violations and not self.timed_out and self.inputs_unchanged

    def summary(self) -> dict:
        return {"ok": self.ok, "returncode": self.returncode, "duration_s": round(self.duration_s, 2),
                "timed_out": self.timed_out, "violations": self.violations, "inputs_unchanged": self.inputs_unchanged,
                "stderr_tail": self.stderr[-2000:]}


def _limits(lim: Limits):
    def apply():
        os.setsid()
        mb = 1024 * 1024
        resource.setrlimit(resource.RLIMIT_CPU, (lim.cpu_s, lim.cpu_s))
        resource.setrlimit(resource.RLIMIT_AS, (lim.mem_mb * mb, lim.mem_mb * mb))
        resource.setrlimit(resource.RLIMIT_FSIZE, (lim.file_mb * mb, lim.file_mb * mb))
        resource.setrlimit(resource.RLIMIT_NOFILE, (lim.nofile, lim.nofile))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    return apply


def freeze_inputs(input_dir: Path) -> dict[str, str]:
    """Make every input file read-only; return their hashes."""
    hashes = {}
    for p in sorted(input_dir.iterdir()):
        if p.is_file():
            p.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            hashes[p.name] = sha256_file(p)
    return hashes


def run_python(script: Path, input_dir: Path, output_dir: Path, limits: Limits | None = None,
               extra_args: list[str] | None = None) -> SandboxResult:
    lim = limits or Limits()
    script, input_dir, output_dir = Path(script).resolve(), Path(input_dir).resolve(), Path(output_dir).resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    tmp = output_dir / ".tmp"
    tmp.mkdir()
    before = freeze_inputs(input_dir)
    env = {
        "PATH": "/usr/bin:/bin", "HOME": str(tmp), "TMPDIR": str(tmp), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
        "INPUT_DIR": str(input_dir), "OUTPUT_DIR": str(output_dir), "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2", "MPLBACKEND": "Agg", "NO_PROXY": "", "no_proxy": "",
        "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
        "http_proxy": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9",
    }
    cmd = [sys.executable, "-I", "-B", str(BOOT), str(script), *(extra_args or [])]
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=output_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            preexec_fn=_limits(lim), text=True)
    timed_out = False
    try:
        out, err = proc.communicate(timeout=lim.wall_s)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
    dur = time.monotonic() - t0
    shutil.rmtree(tmp, ignore_errors=True)
    after = {p.name: sha256_file(p) for p in sorted(input_dir.iterdir()) if p.is_file()}
    violations = [ln.split("SANDBOX-VIOLATION: ", 1)[1] for ln in err.splitlines() if "SANDBOX-VIOLATION: " in ln]
    return SandboxResult(proc.returncode, dur, out[-20000:], err[-20000:], violations, timed_out, before == after)
