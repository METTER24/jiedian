
import socket
import re
import base64
import json
import concurrent.futures
from urllib.parse import urlsplit, unquote

INPUT = "nodes.txt"
OUTPUT = "alive_nodes.txt"
TIMEOUT = 3
MAX_WORKERS = 50


def get_host_port(node):
    """解析节点的服务器地址和端口。"""
    try:
        if node.startswith("vmess://"):
            encoded = node[len("vmess://"):].strip()
            encoded += "=" * ((4 - len(encoded) % 4) % 4)

            raw = base64.urlsafe_b64decode(encoded)
            info = json.loads(raw.decode("utf-8"))

            host = info.get("add")
            port = int(info.get("port"))

            if host and 1 <= port <= 65535:
                return host.strip(), port

            return None, None

        if node.startswith(("vless://", "trojan://", "ss://")):
            # SS 可能使用多种 URL 编码格式，下面只处理可识别的常见形式。
            if node.startswith("ss://"):
                return get_ss_host_port(node)

            parsed = urlsplit(node)
            host = parsed.hostname
            port = parsed.port

            if host and port and 1 <= port <= 65535:
                return host, port

    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    except Exception:
        pass

    return None, None


def get_ss_host_port(node):
    """解析常见 Shadowsocks URI 格式。"""
    try:
        body = node[len("ss://"):].split("#", 1)[0].split("?", 1)[0]

        # SIP002: ss://base64(method:password)@host:port
        if "@" in body:
            userinfo, server = body.rsplit("@", 1)
            server_parsed = urlsplit("//" + server)
            if server_parsed.hostname and server_parsed.port:
                return server_parsed.hostname, server_parsed.port

            # 兼容 URL 中编码的用户名信息
            userinfo = unquote(userinfo)
            if userinfo:
                return None, None

        # 旧格式: ss://base64(method:password@host:port)
        decoded = base64.urlsafe_b64decode(
            body + "=" * ((4 - len(body) % 4) % 4)
        ).decode("utf-8")

        match = re.search(r"@(\[[^\]]+\]|[^:]+):(\d+)$", decoded)
        if match:
            host = match.group(1).strip("[]")
            port = int(match.group(2))
            if 1 <= port <= 65535:
                return host, port

    except Exception:
        pass

    return None, None


def check(node):
    host, port = get_host_port(node)

    if not host or not port:
        return "unparsed", node

    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return "tcp_open", node
    except (socket.timeout, TimeoutError):
        return "timeout", node
    except OSError:
        return "closed", node


def main():
    try:
        with open(INPUT, "r", encoding="utf-8") as f:
            nodes = list(dict.fromkeys(
                line.strip() for line in f if line.strip()
            ))
    except FileNotFoundError:
        print(f"错误：找不到 {INPUT}")
        return

    print("待检测节点：", len(nodes))

    results = {
        "tcp_open": [],
        "timeout": 0,
        "closed": 0,
        "unparsed": 0,
    }

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as pool:
        for status, node in pool.map(check, nodes):
            if status == "tcp_open":
                results["tcp_open"].append(node)
            else:
                results[status] += 1

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(results["tcp_open"]))
        if results["tcp_open"]:
            f.write("\n")

    print("TCP 端口可连接：", len(results["tcp_open"]))
    print("连接超时：", results["timeout"])
    print("连接失败：", results["closed"])
    print("无法解析：", results["unparsed"])
    print(f"结果已写入 {OUTPUT}")
    print("注意：端口可连接不代表代理协议或 TLS 验证成功。")


if __name__ == "__main__":
    main()
```
