"""Find Home Assistant from the Hermes host and verify a user-confirmed URL (read-only)."""
import argparse
import getpass
import hashlib
import http.client
import ipaddress
import json
import os
from pathlib import Path
import socket
import sys
import threading
import time
from urllib.parse import urlsplit

SERVICE = "_home-assistant._tcp.local."


def runtime_id():
    # Read only local identifiers. A Linux container may share its host name but use a different network.
    parts = [sys.platform, socket.gethostname()]
    if sys.platform.startswith("linux"):
        parts.extend([Path("/proc/sys/kernel/random/boot_id").read_text().strip(), os.readlink("/proc/self/ns/net")])
    elif sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography",
                            0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            parts.append(winreg.QueryValueEx(key, "MachineGuid")[0])
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()[:24]


def base_url(raw):
    raw = raw.strip()
    if not raw or any(ord(c) < 33 or ord(c) == 127 for c in raw) or "\\" in raw:
        raise ValueError("HA 地址无效")
    url = urlsplit(raw)
    if (url.scheme not in ("http", "https") or not url.hostname or url.username is not None
            or url.password is not None or "?" in raw or "#" in raw or url.port == 0):
        raise ValueError("请使用完整的 HTTP(S) 基础地址")
    return raw.rstrip("/")


def instance(info):
    fields = info.properties
    address = fields.get(b"internal_url") or fields.get(b"base_url")
    if address:
        address = address.decode("utf-8")
    else:
        ips = [ipaddress.ip_address(addr) for addr in info.parsed_addresses()]
        ips = [ip for ip in ips if not (ip.is_link_local or ip.is_loopback or ip.is_unspecified or ip.is_multicast)]
        if not ips or not 0 < info.port < 65536:
            return None
        ip = min(ips, key=lambda item: item.version)
        host = str(ip) if ip.version == 4 else f"[{ip}]"
        address = f"http://{host}:{info.port}"
    address = base_url(address)
    name = info.name[:-len(SERVICE)-1]
    # Service names are shown in a terminal, including names supplied by other machines.
    name = "".join(c for c in name if c.isprintable())
    key = fields.get(b"uuid") or address.encode()
    return key, (name, address)


def discover():
    from zeroconf import ServiceBrowser, Zeroconf
    names = set()
    lock = threading.Lock()

    class Listener:
        def add_service(self, service, kind, name):
            with lock:
                names.add(name)

        update_service = add_service

        def remove_service(self, service, kind, name):
            with lock:
                names.discard(name)

    found = {}
    zc = Zeroconf()
    try:
        browser = ServiceBrowser(zc, SERVICE, Listener())
        try:
            time.sleep(4)
            with lock:
                seen = sorted(names)
        finally:
            browser.cancel()
        deadline = time.monotonic() + 6
        for name in seen:
            timeout = min(1200, int(1000 * (deadline - time.monotonic())))
            if timeout <= 0:
                break
            info = zc.get_service_info(SERVICE, name, timeout=timeout)
            if info:
                try:
                    item = instance(info)
                except ValueError:
                    continue
                if item:
                    found.setdefault(*item)
    finally:
        zc.close()
    return sorted(found.values())


def choose(found, ask=input):
    for index, (name, url) in enumerate(found, 1):
        print(f"{index}. {name}  {url}")
    if len(found) == 1:
        answer = ask("回车确认该地址，或输入其他 HA 基础地址：").strip()
        if not answer:
            return found[0][1]
    else:
        answer = ask("选择序号或手填 HA 基础地址：" if found else "请手填 HA 基础地址：").strip()
    if answer.isdecimal() and 1 <= int(answer) <= len(found):
        return found[int(answer) - 1][1]
    return base_url(answer)


def verify(address, token):
    url = urlsplit(base_url(address))
    if not token or not token.isascii() or not token.isprintable() or any(c.isspace() for c in token):
        raise ValueError("HA 令牌格式无效，请在主机上重新输入")
    cls = http.client.HTTPSConnection if url.scheme == "https" else http.client.HTTPConnection
    conn = cls(url.hostname, url.port, timeout=6)
    try:
        conn.request("GET", url.path.rstrip("/") + "/api/config", headers={"Authorization": "Bearer " + token})
        response = conn.getresponse()
        if response.status != 200:
            raise ValueError(f"HA 验证失败（HTTP {response.status}），请核对地址和授权")
        data = json.loads(response.read(262144))
        if not isinstance(data, dict) or not data.get("version") or "location_name" not in data:
            raise ValueError("该地址没有返回 HA 配置信息")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument("--runtime-id", action="store_true", help="在已确认的 Hermes 主机或容器内读取位置标识，仅使用本机信息")
    options.add_argument("--discover-only", action="store_true", help="只列出实例，供部署者选择")
    options.add_argument("--url", help="验证已确认的 HA 基础地址")
    parser.add_argument("--expect-runtime", metavar="ID", help="前一步在实际 Hermes 运行环境取得的位置标识")
    args = parser.parse_args()
    if args.runtime_id:
        print(runtime_id())
        return
    if not args.expect_runtime:
        parser.error("请先通过目标 Hermes 主机或容器取得 --runtime-id，再用 --expect-runtime ID 运行。尚未查找或连接 HA。")
    if args.expect_runtime != runtime_id():
        parser.error("当前终端与选定的 Hermes 运行环境不符。请在原 Hermes 主机或容器执行。尚未查找或连接 HA。")
    if args.url:
        address = base_url(args.url)
    else:
        try:
            found = discover()
        except (ImportError, OSError) as error:
            print("mDNS 不可用（" + type(error).__name__ + "）；可手填地址或安装 zeroconf 后重试。", file=sys.stderr)
            found = []
        if args.discover_only:
            print(json.dumps([{"name": name, "url": url} for name, url in found], ensure_ascii=False))
            return
        address = choose(found)
    token = ""
    if os.environ.get("HASS_URL", "").strip().rstrip("/") == address:
        token = os.environ.get("HASS_TOKEN", "")
    if not token:
        if not sys.stdin.isatty():
            raise ValueError("请在 Hermes 主机交互终端输入令牌，或加载与已确认地址匹配的 profile 环境变量")
        token = getpass.getpass("该 HA 的长期访问令牌（隐藏输入）：").strip()
    if not token:
        raise ValueError("需要 HA 授权")
    verify(address, token)
    print("HA 地址及授权已从当前主机验证通过：" + address)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, http.client.HTTPException, EOFError) as error:
        sys.exit("HA 验证未完成：" + str(error))
