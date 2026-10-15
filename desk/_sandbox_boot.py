"""Runs inside the sandboxed child process before the generated script. Standard library only at import.

Guards (see DESIGN.md, "Sandbox", for what these do and do not stop):
1. A PEP 578 audit hook that refuses
   - any socket creation or connection (no network),
   - subprocesses, exec, fork, os.system (no escaping to a shell),
   - file opens for writing outside OUTPUT_DIR and the private TMPDIR,
   - file opens for reading outside INPUT_DIR, OUTPUT_DIR, TMPDIR, the script and the Python install.
2. DuckDB connections are opened with DuckDB's own file allowlist (INPUT_DIR, OUTPUT_DIR),
   external access off, extension autoload off, configuration locked.
3. pyarrow/pandas Parquet and CSV entry points check their path arguments against the same allowlist,
   since their C++ I/O does not raise Python audit events.
Violations are printed as "SANDBOX-VIOLATION: ..." on stderr and raised as PermissionError.
"""

import os
import sys

SCRIPT = os.path.realpath(sys.argv[1])
INPUT = os.path.realpath(os.environ["INPUT_DIR"])
OUTPUT = os.path.realpath(os.environ["OUTPUT_DIR"])
TMP = os.path.realpath(os.environ["TMPDIR"])
PY_ROOTS = {os.path.realpath(p) for p in (sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix)}
PY_ROOTS |= {os.path.realpath(p) for p in sys.path if p and os.path.isdir(p)}
SYSTEM_READ = ("/usr/", "/lib", "/etc/", "/proc/", "/sys/", "/dev/", "/opt/")
WRITE_OK = (OUTPUT, TMP)
READ_OK = (INPUT, OUTPUT, TMP, SCRIPT) + tuple(PY_ROOTS)


def _under(path: str, roots) -> bool:
    return any(path == r or path.startswith(r.rstrip("/") + "/") for r in roots)


def _violation(msg: str):
    sys.stderr.write(f"SANDBOX-VIOLATION: {msg}\n")
    sys.stderr.flush()
    raise PermissionError(f"sandbox: {msg}")


def check_path(path, write: bool, what: str = "open"):
    if isinstance(path, int):
        return  # an already-open descriptor
    p = os.fsdecode(path) if isinstance(path, (bytes, os.PathLike)) else str(path)
    if "://" in p:
        _violation(f"{what} of URL {p}")
    rp = os.path.realpath(p)
    if write:
        if not _under(rp, WRITE_OK):
            _violation(f"{what} for writing outside OUTPUT_DIR: {rp}")
    elif not (_under(rp, READ_OK) or rp.startswith(SYSTEM_READ)):
        _violation(f"{what} for reading outside the allowed inputs: {rp}")


BLOCKED_EVENTS = ("socket.", "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.fork",
                  "os.forkpty", "pty.spawn", "os.spawn", "webbrowser.open", "urllib.Request", "ftplib.", "smtplib.",
                  "http.client.connect")


def _hook(event: str, args):
    if event.startswith(BLOCKED_EVENTS):
        _violation(f"blocked operation {event}")
    if event == "open":
        path, mode = args[0], args[1] or "r"
        flags = args[2] if len(args) > 2 else 0
        write = any(c in str(mode) for c in "wax+") or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
        check_path(path, write)
    elif event in ("os.remove", "os.rename", "os.rmdir", "shutil.rmtree", "os.mkdir", "os.chmod", "os.symlink",
                   "os.link", "os.truncate"):
        check_path(args[0], True, event)


def _patch_duckdb():
    import duckdb
    real_connect = duckdb.connect

    def connect(database=":memory:", read_only=False, config=None, **kw):
        if database not in (":memory:", "", None):
            check_path(database, True, "duckdb.connect")
        cfg = dict(config or {})
        cfg.update({"autoinstall_known_extensions": False, "autoload_known_extensions": False})
        con = real_connect(database, read_only=read_only, config=cfg, **kw)
        dirs = ", ".join("'" + d.replace("'", "''") + "/'" for d in (INPUT, OUTPUT, TMP))
        con.execute(f"SET allowed_directories = [{dirs}]")
        con.execute("SET enable_external_access = false")
        con.execute("SET lock_configuration = true")
        return con

    duckdb.connect = connect
    duckdb.default_connection = None  # module-level duckdb.sql() is unavailable; use duckdb.connect()

    def _no_default(*a, **k):
        _violation("module-level duckdb.sql/query is disabled in the sandbox; use duckdb.connect()")
    for name in ("sql", "query", "execute", "read_parquet", "read_csv", "from_parquet", "from_csv_auto"):
        if hasattr(duckdb, name):
            setattr(duckdb, name, _no_default)


def _wrap(mod, name, write, argpos=0, kwname="path"):
    real = getattr(mod, name, None)
    if real is None:
        return

    def wrapper(*a, **k):
        target = a[argpos] if len(a) > argpos else k.get(kwname, k.get("source", k.get("where")))
        if isinstance(target, (str, bytes, os.PathLike)):
            check_path(target, write, f"{mod.__name__}.{name}")
        return real(*a, **k)
    wrapper.__wrapped__ = real
    setattr(mod, name, wrapper)


def _patch_arrow_pandas():
    try:
        import pyarrow.parquet as pq
        import pyarrow.csv as pcsv
        import pyarrow.dataset as pds
        _wrap(pq, "read_table", False, kwname="source")
        _wrap(pq, "ParquetFile", False, kwname="source")
        _wrap(pq, "ParquetDataset", False, kwname="path_or_paths")
        _wrap(pq, "write_table", True, argpos=1, kwname="where")
        _wrap(pcsv, "read_csv", False, kwname="input_file")
        _wrap(pds, "dataset", False, kwname="source")
    except ImportError:
        pass
    try:
        import pandas as pd
        _wrap(pd, "read_parquet", False)
        _wrap(pd, "read_feather", False)
        real_to_parquet = pd.DataFrame.to_parquet

        def to_parquet(self, path=None, *a, **k):
            if isinstance(path, (str, bytes, os.PathLike)):
                check_path(path, True, "DataFrame.to_parquet")
            return real_to_parquet(self, path, *a, **k)
        pd.DataFrame.to_parquet = to_parquet
    except ImportError:
        pass


def main():
    _patch_arrow_pandas()      # import heavy libraries before the hook, so their own imports are not audited
    try:
        _patch_duckdb()
    except ImportError:
        pass
    import runpy
    sys.addaudithook(_hook)
    sys.argv = [SCRIPT] + sys.argv[2:]
    runpy.run_path(SCRIPT, run_name="__main__")


if __name__ == "__main__":
    main()
