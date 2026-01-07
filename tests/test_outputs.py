import subprocess
from pathlib import Path
import time

def test_main_compiles():
    """Test that main.cpp compiles successfully.

    This test verifies:
    1. The main.cpp file can be compiled with cmake without errors
    """

    Path("/app/build/main").unlink(missing_ok=True)

    result = subprocess.run(
        ["mkdir", "-p", "build", "&&", "cd", "build", "&&", "cmake", "..", "&&", "make"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Compilation failed: {result.stderr}"

def test_runs_and_produces_output():
    """Test that the compiled program runs and produces output.

    This test:
    1. Runs the compiled main program
    2. Verifies that the HTTP status code was output.

    """
    # Run the program
    run_result = subprocess.run(
        ["./main"], capture_output=True, text=True, cwd="/app/build"
    )

    assert run_result.returncode == 0, f"Program execution failed: {run_result.stderr}"
    assert run_result.stdout.strip() == "200"

def test_links_openssl_and_boost():
    out = subprocess.check_output(["ldd", "./main"], text=True)

    assert "libssl" in out, "OpenSSL (libssl) not linked"
    assert "libcrypto" in out, "OpenSSL (libcrypto) not linked"
    assert "boost_system" in out or "libboost_system" in out, "Boost.System not linked"

def test_real_tls_handshake():
    proc = subprocess.Popen(
        ["./main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = proc.communicate(timeout=10)

    assert proc.returncode == 0
    assert "200" in stdout

    # OpenSSL error strings only appear if TLS stack is active
    assert "SSL" not in stderr.upper(), f"TLS error occurred:\n{stderr}"

def test_fails_without_network():
    result = subprocess.run(
        ["unshare", "-n", "./main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    assert result.returncode != 0

def test_requires_example_dot_com():
    env = dict(**{"RES_OPTIONS": "attempts:0 timeout:1"})

    result = subprocess.run(
        ["./main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    assert result.returncode != 0 or "200" not in result.stdout

def test_uses_openssl_symbols():
    out = subprocess.check_output(["nm", "-D", "./main"], text=True)

    assert "SSL_connect" in out or "SSL_CTX_new" in out, \
        "No OpenSSL symbols referenced"

