import socket
import re
import concurrent.futures


INPUT = "nodes.txt"

OUTPUT = "alive_nodes.txt"



# 提取服务器地址和端口

def parse_node(node):

    try:

        # vmess base64解码

        if node.startswith("vmess://"):

            import base64
            import json

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


        # vless trojan ss 简单解析

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

        pass


    return None,None




def check(host,port):

    try:

        s=socket.socket()

        s.settimeout(3)

        s.connect(
            (host,port)
        )

        s.close()

        return True


    except:

        return False




# 读取节点


with open(
    INPUT,
    "r",
    encoding="utf-8"
) as f:

    nodes=[
        x.strip()
        for x in f.readlines()
        if x.strip()
    ]



alive=[]



print(
    "开始检测节点:",
    len(nodes)
)



def worker(node):

    host,port=parse_node(node)


    if host and port:

        if check(host,port):

            return node


    return None




with concurrent.futures.ThreadPoolExecutor(
    max_workers=100
) as executor:


    results=executor.map(
        worker,
        nodes
    )


    for r in results:

        if r:

            alive.append(r)



print(
    "可用节点:",
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
