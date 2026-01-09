import subprocess
from pathlib import Path
import os
import re

ROOT = Path("/app")
BUILD_DIR = ROOT / "build"


def build_project():
    BUILD_DIR.mkdir(exist_ok=True)

    if (ROOT / "CMakeLists.txt").exists():
        r = subprocess.run(
            ["cmake", ".."],
            cwd=BUILD_DIR,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"CMake configure failed:\n{r.stderr}"

        r = subprocess.run(
            ["cmake", "--build", "."],
            cwd=BUILD_DIR,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"CMake build failed:\n{r.stderr}"
    else:
        build_script = ROOT / "build.sh"
        assert build_script.exists(), "No CMakeLists.txt or build.sh found"

        r = subprocess.run(
            ["sh", str(build_script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Build script failed:\n{r.stderr}"


def find_executable():
    executables = [
        p for p in BUILD_DIR.iterdir()
        if p.is_file() and os.access(p, os.X_OK)
    ]
    assert executables, "No executable produced by the build"
    return executables[0]


def extract_http_status(output: str):
    match = re.search(r"\b\d{3}\b", output)
    return int(match.group()) if match else None


def test_build_and_basic_https_success():
    """
    Baseline test: program builds, runs, and prints an HTTP status code.
    """
    build_project()
    exe = find_executable()

    r = subprocess.run(
        [str(exe)],
        cwd=BUILD_DIR,
        capture_output=True,
        text=True,
        timeout=15,
    )
    print(r.stdout)

    assert r.returncode == 0, f"Program failed:\n{r.stderr}"

    status = extract_http_status(r.stdout)
    assert status is not None, "No HTTP status code printed"
    assert 100 <= status < 600


def test_requires_example_dot_com():
    """
    Verifies the program truly targets example.com by breaking its DNS.
    """
    build_project()
    exe = find_executable()

    env = os.environ.copy()
    env["RES_OPTIONS"] = "attempts:0 timeout:1"

    r = subprocess.run(
        [str(exe)],
        cwd=BUILD_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Program must NOT be able to produce a valid status code
    status = extract_http_status(r.stdout)
    assert status is None or r.returncode != 0, (
        "Program still produced a status code without resolving example.com"
    )


# def test_https_connection_to_example_dot_com():
#     """
#     Verifies the program:
#       - Resolves example.com
#       - Connects to TCP port 443
#     """
#     build_project()
#     exe = find_executable()
#
#     r = subprocess.run(
#         [
#             "strace",
#             "-f",
#             "-e", "trace=network",
#             str(exe),
#         ],
#         cwd=BUILD_DIR,
#         capture_output=True,
#         text=True,
#         timeout=15,
#     )
#
#     trace = r.stderr
#
#     assert "example.com" in trace, "No DNS lookup for example.com detected"
#     assert ":443" in trace, "No connection attempt to port 443 detected"
#
