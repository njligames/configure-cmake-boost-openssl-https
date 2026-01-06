import subprocess
from pathlib import Path

def test_main_cpp_file_exists():
    main_cpp_path = Path("/app/main.cpp")
    assert main_cpp_path.exists(), f"File {main_cpp_path} does not exist"

def test_CMakeLists_txt_file_exists():
    cmakelistst_txt_path = Path("/app/CMakeLists.txt")
    assert cmakelistst_txt_path.exists(), f"File {cmakelistst_txt_path} does not exist"

def test_main_compiles():
    """Test that main.cpp compiles successfully.
    
    This test verifies:
    1. The main.cpp file can be compiled with cmake without errors
    """

    Path("/app/build/https_client").unlink(missing_ok=True)

    result = subprocess.run(
        ["mkdir", "-p", "build", "&&", "cd", "build", "&&", "cmake", "..", "&&", "make"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Compilation failed: {result.stderr}"

def test_runs_and_produces_output():
    """Test that the compiled program runs and produces output.
    
    This test:
    1. Runs the compiled https_client program
    2. Verifies that the HTTP status code was output.
    
    """
    # Run the program
    run_result = subprocess.run(
        ["./https_client"], capture_output=True, text=True, cwd="/app/build"
    )
    
    assert run_result.returncode == 0, f"Program execution failed: {run_result.stderr}"
    assert run_result.stdout.strip() == "HTTP status code: 200"