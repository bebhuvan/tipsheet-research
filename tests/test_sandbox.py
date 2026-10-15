import os
import textwrap

import pandas as pd
import pytest

from desk.sandbox import Limits, run_python


@pytest.fixture
def dirs(tmp_path):
    inp = tmp_path / "inputs"
    inp.mkdir()
    pd.DataFrame({"x": [1, 2, 3]}).to_parquet(inp / "t.parquet")
    secret = tmp_path / "secret.txt"
    secret.write_text("KEY=abc")
    return inp, tmp_path / "out", secret


def run(tmp_path, dirs, body, **kw):
    inp, out, _ = dirs
    script = tmp_path / "s.py"
    script.write_text(textwrap.dedent(body))
    return run_python(script, inp, out, **kw)


def test_ok_script_reads_inputs_and_writes_outputs(tmp_path, dirs):
    r = run(tmp_path, dirs, """
        import os, json, pandas as pd, duckdb
        df = pd.read_parquet(os.environ["INPUT_DIR"] + "/t.parquet")
        n = duckdb.connect().execute(f"select count(*) from read_parquet('{os.environ['INPUT_DIR']}/t.parquet')").fetchone()[0]
        open(os.environ["OUTPUT_DIR"] + "/results.json", "w").write(json.dumps({"n": int(n), "s": int(df.x.sum())}))
    """)
    assert r.ok, r.stderr
    assert (dirs[1] / "results.json").read_text() == '{"n": 3, "s": 6}'


@pytest.mark.parametrize("body,needle", [
    ("import socket; socket.create_connection(('1.1.1.1', 80), timeout=1)", "socket"),
    ("import urllib.request; urllib.request.urlopen('http://example.com', timeout=1)", ""),
    ("import subprocess; subprocess.run(['ls'])", "subprocess"),
    ("import os; os.system('ls')", "os.system"),
    ("open('/tmp/sbx_escape_test.txt', 'w').write('x')", "writing outside"),
    ("import os; open(os.environ['INPUT_DIR'] + '/t.parquet', 'ab').write(b'x')", "writing outside"),
    ("import pandas as pd; pd.read_parquet('{secret_dir}/../x.parquet')", "reading outside"),
    ("open('{secret}').read()", "reading outside"),
    ("import duckdb; duckdb.connect().execute(\"select * from read_csv('{secret}')\").fetchall()", ""),
])
def test_guards_block(tmp_path, dirs, body, needle):
    secret = dirs[2]
    r = run(tmp_path, dirs, body.format(secret=secret, secret_dir=secret.parent))
    assert not r.ok
    assert r.returncode != 0
    if needle:
        assert any(needle in v for v in r.violations), (r.violations, r.stderr[-500:])
    assert not os.path.exists("/tmp/sbx_escape_test.txt")
    assert r.inputs_unchanged


def test_environment_has_no_keys(tmp_path, dirs, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-should-not-leak")
    r = run(tmp_path, dirs, """
        import os, json
        open(os.environ["OUTPUT_DIR"] + "/env.json", "w").write(json.dumps(sorted(os.environ)))
    """)
    assert r.ok
    env = (dirs[1] / "env.json").read_text()
    assert "DEEPSEEK" not in env and "sk-should" not in env


def test_timeout_kills(tmp_path, dirs):
    r = run(tmp_path, dirs, "while True: pass", limits=Limits(wall_s=2, cpu_s=30))
    assert r.timed_out and not r.ok
