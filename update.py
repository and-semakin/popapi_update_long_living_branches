#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path
from contextlib import contextmanager

# path to the repo
repo = Path("~/git/popapi").expanduser()

# long-living branch pattern
long_living_branch = re.compile(r"RC_[\w.-]*|SB_[\w.-]*|master|live")


def git(command: str) -> str:
    output = subprocess.check_output(
        f"git {command}", shell=True, cwd=repo
    ).decode()
    return output


@contextmanager
def git_stash():
    print("Stash local changes...")
    result = git("stash push -m \"Update long-living branches\"")
    stashed = result.startswith("Saved working directory")
    try:
        yield
    except Exception:
        raise
    else:
        if stashed:
            print("Unstash local changes...")
            git("stash pop")


# get list of long-living branches
branches = git("branch -a")

long_living_branches = sorted(set(
    re.findall(long_living_branch, branches)
))


# remember checked-out branch
current_branch = git("rev-parse --abbrev-ref HEAD").strip()
print()
print("Current branch:", current_branch)

print("Fetching updates...")
git("fetch")

# update all long-living branches
print("Long-living branches:")
with git_stash():
    for branch in long_living_branches:
        print(" *", branch, end=" ")
        git(f"checkout {branch}")
        git(f"merge origin/{branch}")
        print("OK")

    print()
    print(f"Return previously checked-out branch {current_branch}")
    git(f"checkout {current_branch}")

print("Done!")
