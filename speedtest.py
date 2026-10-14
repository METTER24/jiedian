import socket
import time
import base64
import json
import concurrent.futures
from urllib.parse import urlsplit, unquote


INPUT = "alive_nodes.txt"
OUTPUT = "best_nodes.txt"

TIMEOUT = 3
MAX_WORKERS = 100

# 保留最快多少个节点
MAX_RESULTS = 200



def get_host_port(node):

    try:

        node = unquote(node)


        # =====================
        # VMess
        # =====================

        if node.startswith("vmess://"):

            data = node.replace(
                "vmess://",
                ""
            )

            data += "=" * (
                (4 - len(data) % 4) % 4
            )


            raw = base64.urlsafe_b64decode(
                data
            )


            info = json.loads(
                raw.decode(
                    "utf-8",
                    errors="ignore"
                )
            )


            host = (
                info.get("add")
                or info.get("host")
            )


            port = info.get("port")


            if host and port:

                return (
                    host,
                    int(port)
                )



        # =====================
        # VLESS / Trojan
        # =====================

        if node.startswith(
            (
                "vless://",
                "trojan://"
            )
        ):

            parsed = urlsplit(node)


            if parsed.hostname and parsed.port:

                return (
                    parsed.hostname,
                    parsed.port
                )



        # =====================
        # Shadowsocks
        # =====================

        if node.startswith("ss://"):

            return parse_ss(node)



    except Exception:

        pass



    return None, None




def parse_ss(node):

    try:

        body = (
            node[5:]
            .split("#")[0]
            .split("?")[0]
        )


        # 新格式

        if "@" in body:


            server = body.rsplit(
                "@",
                1
            )[1]


            parsed = urlsplit(
                "//" + server
            )


            if parsed.hostname and parsed.port:

                return (
                    parsed.hostname,
                    parsed.port
                )



        # 老格式

        body += "=" * (
            (4 - len(body) % 4) % 4
        )


        decoded = base64.urlsafe_b64decode(
            body
        ).decode(
            "utf-8",
            errors="ignore"
        )


        if "@" in decoded:


            server = decoded.rsplit(
                "@",
                1
            )[1]


            host, port = server.rsplit(
                ":",
                1
            )


            return (
                host,
                int(port)
            )



    except Exception:

        pass



    return None, None




def test_node(node):

    host, port = get_host_port(node)


    if not host or not port:

        return None



    try:


        start = time.time()


        sock = socket.create_connection(
            (
                host,
                port
            ),
            timeout=TIMEOUT
        )


        sock.close()


        delay = int(
            (time.time() - start)
            * 1000
        )


        return (
            delay,
            node
        )



    except Exception:

        return None





def main():


    try:

        with open(
            INPUT,
            encoding="utf-8"
        ) as f:


            nodes = list(
                dict.fromkeys(
                    line.strip()
                    for line in f
                    if line.strip()
                )
            )


    except FileNotFoundError:


        print(
            "找不到",
            INPUT
        )


        open(
            OUTPUT,
            "w"
        ).close()


        return




    print(
        "测速节点:",
        len(nodes)
    )



    results = []



    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as pool:


        for result in pool.map(
            test_node,
            nodes
        ):


            if result:

                results.append(
                    result
                )




    # 延迟排序

    results.sort(
        key=lambda x:x[0]
    )



    # 保留最快节点

    results = results[
        :MAX_RESULTS
    ]



    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        for delay,node in results:

            f.write(
                node + "\n"
            )




    print(
        "测速完成"
    )


    print(
        "有效节点:",
        len(results)
    )



    if results:

        print(
            "最快延迟:",
            results[0][0],
            "ms"
        )

    else:

        print(
            "没有找到可用节点"
        )





if __name__ == "__main__":

    main()
