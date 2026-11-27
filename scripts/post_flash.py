"""SP5.5 post-install tasks. Only disable-mijia changes a device."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request


MIJIA = "com.xiaomi.smarthome"
SSH_APK = "org.galexander.sshd_27.apk"
SSH_SHA256 = "a2a8f7941a9ec2d04aeff68b871bfa8810219d023b20f835011111fba06d7628"
CACHE = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".cache")) / "Nabu-LX04" / "downloads"


def verify_apk(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != SSH_SHA256:
        raise ValueError(f"Unexpected SHA-256: {path}")


def fetch_ssh(cache):
    cache.mkdir(exist_ok=True, parents=True)
    target = cache / SSH_APK
    if target.exists():
        verify_apk(target)
        return target
    with tempfile.NamedTemporaryFile(dir=cache, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        url = "https://f-droid.org/repo/" + SSH_APK
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read(3271856)
        if len(data) != 3271855:
            raise ValueError("Unexpected SimpleSSHD APK length")
        temporary.write_bytes(data)
        verify_apk(temporary)
        os.replace(temporary, target)
        return target
    finally:
        temporary.unlink(missing_ok=True)


def mijia(shell, disable):
    for prop, expected in [("ro.product.device", "mi_lx04"), ("ro.build.version.sdk", "27"),
                           ("sys.boot_completed", "1")]:
        if shell("getprop", prop).strip() != expected:
            raise ValueError(f"Unexpected {prop}. Check the selected device and ROM.")

    def listed(*options):
        lines = shell("pm", "list", "packages", *options, "--user", "0").splitlines()
        if "package:com.xiaomi.micolauncher" not in lines and not options:
            raise ValueError("Missing expected launcher in user 0 package inventory")
        if any(line and not line.startswith("package:") for line in lines):
            raise ValueError("Unexpected package manager response")
        return "package:" + MIJIA in lines

    if not listed():
        print("Mi Home absent for user 0")
        return
    def enabled_state():
        details = shell("dumpsys", "package", MIJIA)
        state = re.search(r"(?m)^\s*User 0:[^\r\n]*?\benabled=(\d+)\b", details)
        if not state or state[1] not in ("0", "1", "2", "3", "4"):
            raise ValueError("Cannot verify Mi Home user 0 state")
        return state[1]

    initial = enabled_state()
    print(f"Mi Home initial user 0 enabled={initial}")
    if disable:
        if initial not in ("2", "3"):
            print(shell("pm", "disable-user", "--user", "0", MIJIA))
        shell("am", "force-stop", "--user", "0", MIJIA)
    if not listed("-d") or enabled_state() not in ("2", "3"):
        raise ValueError("Mi Home is not persistently disabled for user 0")
    names = shell("ps", "-A", "-o", "NAME").split()
    if "NAME" not in names or not any(p in names for p in ("init", "/init")):
        raise ValueError("Cannot verify Android process list")
    if any(p == MIJIA or p.startswith(MIJIA + ":") for p in names):
        raise ValueError("Mi Home still has a running process")
    print("Mi Home disabled for user 0; no Mi Home process")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("fetch-ssh").add_argument("--cache", type=Path, default=CACHE)
    for name in ("disable-mijia", "check-mijia"):
        commands.add_parser(name).add_argument("--serial", required=True)
    args = parser.parse_args()
    try:
        if args.command == "fetch-ssh":
            print(fetch_ssh(args.cache).resolve())
        else:
            def shell(*words):
                return subprocess.check_output(["adb", "-s", args.serial, "shell", *words],
                                               text=True, encoding="utf-8", errors="replace", timeout=30)
            mijia(shell, args.command == "disable-mijia")
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
