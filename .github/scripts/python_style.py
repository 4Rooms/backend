import argparse
import subprocess
from pathlib import Path

CURR_DIR = Path(__file__).resolve().parent
PRJ_DIR = CURR_DIR.parent.parent


# Commands to run
def get_commands(check=True):
    black_cmd = ["black", PRJ_DIR]
    if check:
        black_cmd.append("--check")

    isort_cmd = ["isort", PRJ_DIR]
    if check:
        isort_cmd.append("--check-only")

    autoflake_cmd = [
        "autoflake",
        PRJ_DIR,
        "--recursive",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--in-place",
    ]

    cmds = [
        {"name": "Black Format", "cmd": black_cmd},
        {"name": "Isort", "cmd": isort_cmd},
    ]

    if not check:
        cmds.append({"name": "Autoflake", "cmd": autoflake_cmd})

    return cmds


def main():
    parser = argparse.ArgumentParser(description="Run Python Style Checks")
    parser.add_argument("-f", "--fix", action="store_true", default=False, help="Fix style issues")
    args = parser.parse_args()

    for cmd in get_commands(check=not args.fix):
        print(f"Running {cmd['cmd']}")
        subprocess.run(cmd["cmd"], check=True)


if __name__ == "__main__":
    main()
