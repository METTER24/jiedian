import socket
import re
import base64
import json
import concurrent.futures
import time
from urllib.parse import urlsplit, unquote


INPUT = "nodes.txt"
OUTPUT = "alive_nodes.txt"

TIMEOUT = 3
MAX_WORKERS = 100


def get_host_port(node):

    try:

        node = unquote(node)

        if node.startswith("vmess://"):

            data = node.replace(
                "vmess://",
                ""
            )

            data += "=" * (
                (4 - len(data) % 4) % 4
            )

            raw = base64.urlsafe_b64decode(data)

            info = json.loads(
                raw.decode("utf-8-sig")
            )

            host = (
                info.get("add")
                or info.get("host")
            )

            port = int(
                str(info.get("port"))
            )


            if host and port:
                return host, port


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


        if node.startswith("ss://"):

            return get_ss(node)


    except Exception:
        pass


    return None, None



def get_ss(node):

    try:

        body = (
            node[5:]
            .split("#")[0]
            .split("?")[0]
        )


        if "@" in body:

            server = body.rsplit(
                "@",
                1
            )[1]


            p = urlsplit(
                "//"+server
            )


            return (
                p.hostname,
                p.port
            )


        body += "="*((4-len(body)%4)%4)

        text = base64.urlsafe_b64decode(
            body
        ).decode()


        m = re.search(
            r"@(.+):(\d+)",
            text
        )


        if m:

            return (
                m.group(1),
                int(m.group(2))
            )


    except Exception:
        pass


    return None,None




def check(node):

    host,port=get_host_port(node)


    if not host:
        return None


    try:

        start=time.time()


        with socket.create_connection(
            (
                host,
                port
            ),
            timeout=TIMEOUT
        ):

            delay=int(
                (time.time()-start)*1000
            )


            return (
                delay,
                node
            )


    except Exception:

        return None





def main():

    with open(
        INPUT,
        encoding="utf-8"
    ) as f:

        nodes=list(
            dict.fromkeys(
                x.strip()
                for x in f
                if x.strip()
            )
        )


    print(
        "检测数量:",
        len(nodes)
    )


    alive=[]


    with concurrent.futures.ThreadPoolExecutor(
        MAX_WORKERS
    ) as pool:


        for result in pool.map(
            check,
            nodes
        ):

            if result:
                alive.append(result)



    alive.sort(
        key=lambda x:x[0]
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        for delay,node in alive:

            f.write(
                f"{node}\n"
            )



    print(
        "可用:",
        len(alive)
    )


    if alive:

        print(
            "最快:",
            alive[0][0],
            "ms"
        )



if __name__=="__main__":

    main()
