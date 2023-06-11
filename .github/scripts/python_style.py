from pathlib import Path
import subprocess
import argparse

CURR_DIR = Path(__file__).resolve().parent
PRJ_DIR = CURR_DIR.parent.parent / "djangochat"

# Commands to run
def get_commands(check=True):
    cmds = [
    {"name": "Black Format", "cmd": f"black {PRJ_DIR}" + (" --check" if check else "")},
    {"name": "Isort", "cmd": f"isort {PRJ_DIR}" + (" --check-only" if check else "")},
    ]

    if not check:
        cmds.append({"name": "Autoflake", "cmd": f"autoflake {PRJ_DIR} --recursive --remove-all-unused-imports --remove-unused-variables --in-place"},)

    return cmds

def main():
    parser = argparse.ArgumentParser(description="Run Python Style Checks")
    parser.add_argument("-f", "--fix", action="store_true", default=False, help="Fix style issues")
    args = parser.parse_args()

    for cmd in get_commands(check=not args.fix):
        print(f"Running {cmd['cmd']}")
        subprocess.run(cmd["cmd"], shell=True, check=True)

if __name__ == "__main__":
    main()