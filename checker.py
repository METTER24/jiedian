import socket
import re
import base64
import json
import concurrent.futures


INPUT = "nodes.txt"
OUTPUT = "alive_nodes.txt"



def get_host_port(node):

    try:

        if node.startswith("vmess://"):

            data=node.replace(
                "vmess://",
                ""
            )

            data += "="*((4-len(data)%4)%4)

            info=json.loads(
                base64.b64decode(data).decode()
            )

            return (
                info.get("add"),
                int(info.get("port"))
            )


        match=re.search(
            r"@([^:/]+):(\d+)",
            node
        )

        if match:

            return (
                match.group(1),
                int(match.group(2))
            )


    except:

        return None,None


    return None,None




def check(node):

    host,port=get_host_port(node)


    if not host or not port:

        return None


    try:

        s=socket.socket()

        s.settimeout(3)

        s.connect(
            (host,port)
        )

        s.close()

        return node


    except:

        return None




with open(
    INPUT,
    encoding="utf-8"
) as f:

    nodes=[
        x.strip()
        for x in f
        if x.strip()
    ]



print(
    "检测节点:",
    len(nodes)
)



alive=[]


with concurrent.futures.ThreadPoolExecutor(
    max_workers=100
) as pool:


    for result in pool.map(check,nodes):

        if result:

            alive.append(result)



print(
    "有效节点:",
    len(alive)
)



with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(alive)
    )
