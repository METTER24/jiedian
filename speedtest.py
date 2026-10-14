import socket
import time
import concurrent.futures


INPUT = "alive_nodes.txt"
OUTPUT = "best_nodes.txt"

TIMEOUT = 3
MAX_WORKERS = 100


def get_host_port(node):

    try:

        if node.startswith("vmess://"):

            return None, None


        # vless / trojan
        if node.startswith(
            (
                "vless://",
                "trojan://"
            )
        ):

            from urllib.parse import urlsplit

            p=urlsplit(node)

            return (
                p.hostname,
                p.port
            )


        # ss
        if node.startswith("ss://"):

            return None,None


    except:

        pass


    return None,None



def test(node):

    host,port=get_host_port(node)


    if not host or not port:
        return None


    try:

        start=time.time()


        s=socket.create_connection(
            (
                host,
                port
            ),
            timeout=TIMEOUT
        )


        s.close()


        delay=int(
            (time.time()-start)*1000
        )


        return (
            delay,
            node
        )


    except:

        return None



def main():


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
        "测速节点:",
        len(nodes)
    )


    result=[]


    with concurrent.futures.ThreadPoolExecutor(
        MAX_WORKERS
    ) as pool:


        for r in pool.map(
            test,
            nodes
        ):

            if r:
                result.append(r)



    # 按延迟排序

    result.sort(
        key=lambda x:x[0]
    )


    # 保留前200

    result=result[:200]


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        for delay,node in result:

            f.write(
                node+"\n"
            )



    print(
        "优质节点:",
        len(result)
    )


    if result:

        print(
            "最快:",
            result[0][0],
            "ms"
        )



if __name__=="__main__":

    main()
