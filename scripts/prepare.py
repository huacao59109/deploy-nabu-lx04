"""Verify the release or stage the Windows flash tool. No device I/O."""
import argparse
import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import time
import urllib.request
from http.client import HTTPException
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"
HASHES = {
    "Nabu-LX04.apk": "3401C03ECAA4BD93F37DED7659935AFF964F30DC64DA6D53F18F5D572E910936",
    "lx04-flashtool.zip": "6135D30E12B511C81A6DEAA276DCA64F8A233FD7BDE23DE23D84864A5405BCF0",
    "mtk-driver.zip": "D76375C7BF4917AA70A4127B4369A7A2E82271B64B8CED39E58C36A6A8E8504B",
    "sp5.5-image.zip": "2ACDCFA7E4FDD113A49ADDB16590E3A854C580AC6225F8D8F15A6441A43C1D0F",
}
APK = "Nabu-LX04.apk"
MATERIALS = {
    "firmware": ("sp5.5-image.zip", "/lx04/rom/官改/sp5.5-image.zip", 812625438),
    "tool": ("lx04-flashtool.zip", "/tools/Lx04官方刷机工具.zip", 60267735),
    "driver": ("mtk-driver.zip", "/driver/驱动.zip", 10050066),
}
CACHE = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".cache")) / "Nabu-LX04" / "downloads"
USER_AGENT = "Mozilla/5.0 (Nabu LX04 deployment)"


def check(path, expected):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest().upper() != expected:
        raise ValueError(f"Unexpected SHA-256: {path}")
    print(f"OK {path.name}")


def unique(folder, name):
    paths = list(folder.rglob(name))
    if len(paths) != 1:
        raise ValueError(f"Expected one {name} under {folder}, found {len(paths)}")
    return paths[0]


def download_url(remote, size):
    request = urllib.request.Request(
        "https://xiaoai.qgmzmy.me/api/fs/get", data=json.dumps({"path": remote}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        info = json.load(response)
    data = info.get("data") or {}
    if info.get("code") != 200 or data.get("size") != size:
        raise ValueError(f"Material unavailable or size changed: {remote}")
    url = data.get("raw_url", "")
    if not url.startswith("https://"):
        raise ValueError(f"Missing HTTPS download for {remote}")
    return url


def transfer(remote, size, output):
    url = None
    offset = 0
    failures = 0
    while offset < size:
        end = min(offset + 8 * 1024 * 1024, size) - 1
        try:
            if not url:
                url = download_url(remote, size)
            request = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT, "Range": f"bytes={offset}-{end}"})
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status == 206:
                    if response.headers.get("Content-Range") != f"bytes {offset}-{end}/{size}":
                        raise ValueError("Unexpected download range")
                elif response.status == 200 and offset == 0:
                    end = size - 1
                else:
                    raise ValueError("Server did not honor download range")
                output.seek(offset)
                remaining = end - offset + 1
                while remaining:
                    block = response.read(min(1024 * 1024, remaining))
                    if not block:
                        raise OSError("Incomplete transfer")
                    output.write(block)
                    remaining -= len(block)
                if response.read(1):
                    raise ValueError("Oversized response")
            offset = end + 1
            failures = 0
        except (OSError, HTTPException) as error:
            failures += 1
            if failures == 3:
                raise OSError(f"Download failed for {remote} at byte {offset} ({type(error).__name__})") from None
            url = None
            time.sleep(failures)


def fetch(kind, cache):
    name, remote, size = MATERIALS[kind]
    target = cache / name
    if target.exists():
        check(target, HASHES[name])
        return target
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=cache, prefix=name + ".", suffix=".part", delete=False) as temp:
        partial = Path(temp.name)
    try:
        with partial.open("wb") as output:
            transfer(remote, size, output)
        check(partial, HASHES[name])
        partial.replace(target)
        return target
    finally:
        partial.unlink(missing_ok=True)


def check_gpt(path):
    # MT8167 eMMC uses 512-byte logical sectors. Accept a primary-GPT readback.
    with path.open("rb") as stream:
        stream.seek(512)
        header = bytearray(stream.read(512))
        if len(header) != 512 or header[:8] != b"EFI PART":
            raise ValueError("Primary GPT header missing")
        size, checksum = struct.unpack_from("<II", header, 12)
        if not 92 <= size <= 512:
            raise ValueError("Invalid GPT header length")
        struct.pack_into("<I", header, 16, 0)
        if zlib.crc32(header[:size]) != checksum:
            raise ValueError("GPT header CRC mismatch")
        sector, count, stride, array_crc = struct.unpack_from("<QIII", header, 72)
        if sector < 2 or not (1 <= count <= 4096 and 128 <= stride <= 4096):
            raise ValueError("Unexpected GPT entry layout")
        end = sector * 512 + count * stride
        if end > path.stat().st_size:
            raise ValueError(f"Need at least {end} bytes of readback")
        stream.seek(sector * 512)
        entries = stream.read(count * stride)
    if zlib.crc32(entries) != array_crc:
        raise ValueError("GPT entry array CRC mismatch")
    for offset in range(0, len(entries), stride):
        if any(entries[offset:offset + 16]):
            start, last = struct.unpack_from("<QQ", entries, offset + 32)
            name = entries[offset + 56:offset + 128].decode("utf-16-le", "replace").split("\0")[0]
            print(f"{name}: start=0x{start*512:x} bytes=0x{(last-start+1)*512:x}")
    print("Primary GPT header and entry CRCs valid. This does not authorize writing.")


def write_config(work, scatter, da, auth, read_only):
    config = ET.Element("flashtool-config", version="2.0")
    general = ET.SubElement(config, "general")
    for tag, value in [("chip-name", "MT8167"), ("storage-type", "EMMC"),
                       ("download-agent", da), ("scatter", scatter), ("authentication", auth)]:
        ET.SubElement(general, tag).text = str(value)
    ET.SubElement(general, "rom-list")
    ET.SubElement(general, "connection", {"type": "BromUSB", "high-speed": "false",
                  "power": "AutoDetect", "timeout-count": "180000", "com-port": ""})
    commands = ET.SubElement(config, "commands")
    if read_only:
        readback = ET.SubElement(commands, "readback")
        ET.SubElement(readback, "physical-readback", {"is-physical-readback": "false"})
        roms = ET.SubElement(readback, "readback-list")
        ET.SubElement(roms, "readback-rom-item", {"readback-index": "0", "readback-enable": "true",
                      "readback-flag": "NUTL_READ_PAGE_ONLY", "start-address": "0x0",
                      "readback-length": "0x8000", "addr-flag": "NUTL_ADDR_LOGICAL",
                      "part-id": "8"}).text = str(work / "gpt-head.bin")
        name = "read-gpt.xml"
    else:
        upgrade = ET.SubElement(commands, "firmware-upgrade")
        ET.SubElement(upgrade, "scene").text = "FIRMWARE_UPGRADE"
        name = "firmware-upgrade.xml"
    ET.ElementTree(config).write(work / name, encoding="utf-8")


def stage(path, cache, with_driver):
    if not path.is_absolute() or not str(path).isascii() or re.search(r"\s", str(path)):
        raise ValueError("Choose an absolute ASCII directory with no spaces")
    work = path.resolve()
    if work.exists():
        raise ValueError(f"Stage directory already exists: {work}")
    materials = [("tool", "tool"), ("firmware", "rom")]
    if with_driver:
        materials.append(("driver", "driver"))
    archives = [(fetch(kind, cache), dest) for kind, dest in materials]
    work.mkdir(parents=True, exist_ok=False)
    for archive, dest in archives:
        with zipfile.ZipFile(archive) as package:
            package.extractall(work / dest)
    tool = unique(work / "tool", "_SPFT.exe").parent
    # The legacy utility expects ASCII file paths even on Chinese Windows.
    for source, name, expected in [
        ("DA_Mi_Hikaru-resign.bin", "da.bin", "1832CB312EFDDE35634CCF0A100131AC4C182EF9BD22E51C35A0685F9AB3E880"),
        ("auth_sv5.auth", "auth.auth", "84A89C4E7ACD004AFEF3CD9C775980164ECD735C8AAA8566C58CB574EEEE9B3E")]:
        src = unique(tool, source)
        check(src, expected)
        (work / name).write_bytes(src.read_bytes())
    scatter = unique(work / "rom", "Scatter_Mi_Hikaru-resign.txt")
    info = scatter.read_text(encoding="ascii")
    for field, value in [("platform", "MT8167"), ("project", "mi_lx04"), ("storage", "EMMC")]:
        if not re.search(rf"(?m)^\s*{field}:\s*{value}\s*$", info):
            raise ValueError(f"Unexpected scatter {field}")
    selected = re.findall(r"file_name:\s*(\S+)\s+is_download:\s*true", info)
    if len(selected) != 9 or not all((scatter.parent / name).is_file() for name in selected):
        raise ValueError("Incomplete scatter image set")
    for read_only in (True, False):
        write_config(work, scatter, work / "da.bin", work / "auth.auth", read_only)
    print(f"Prepared {work}. No flash tool was started.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify")
    staging = commands.add_parser("stage")
    staging.add_argument("directory", type=Path)
    staging.add_argument("--with-driver", action="store_true")
    staging.add_argument("--cache", type=Path, default=CACHE)
    fetching = commands.add_parser("fetch")
    fetching.add_argument("material", choices=MATERIALS)
    fetching.add_argument("--cache", type=Path, default=CACHE)
    commands.add_parser("check-gpt").add_argument("readback", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "check-gpt":
            check_gpt(args.readback)
        elif args.command == "verify":
            check(ASSETS / APK, HASHES[APK])
        elif args.command == "fetch":
            print(fetch(args.material, args.cache))
        else:
            stage(args.directory, args.cache, args.with_driver)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        sys.exit(str(error))
