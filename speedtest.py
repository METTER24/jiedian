import os
import json
import time
import base64
import subprocess
import requests
import concurrent.futures


INPUT = "alive_nodes.txt"
OUTPUT = "best_nodes.txt"

TEST_URL = "https://www.gstatic.com/generate_204"

TIMEOUT = 8

MAX_RESULTS = 200



def decode_vmess(node):

    try:

        raw = node.replace(
            "vmess://",
            ""
        )

        raw += "="*((4-len(raw)%4)%4)

        return json.loads(
            base64.b64decode(raw).decode()
        )

    except:

        return None



def make_config(node, port):

    """
    生成 sing-box 配置
    """

    outbound = None


    if node.startswith("vmess://"):

        v = decode_vmess(node)

        if not v:
            return None


        outbound = {

            "type":"vmess",

            "server":v["add"],

            "server_port":int(v["port"]),

            "uuid":v["id"],

            "security":"auto"

        }



    elif node.startswith("vless://"):

        outbound = {

            "type":"vless",

            "server":node.split("@")[1].split(":")[0],

            "server_port":443

        }


    else:

        return None



    return {

        "log":{

            "level":"error"

        },


        "inbounds":[

            {

            "type":"socks",

            "listen":"127.0.0.1",

            "listen_port":port

            }

        ],


        "outbounds":[

            outbound

        ]

    }



def test(node):

    port=20800


    config=make_config(
        node,
        port
    )


    if not config:

        return None



    filename="test.json"


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            config,
            f
        )



    try:

        process=subprocess.Popen(

            [
                "sing-box",
                "run",
                "-c",
                filename
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )


        time.sleep(2)



        start=time.time()


        r=requests.get(

            TEST_URL,

            proxies={

                "http":
                f"socks5://127.0.0.1:{port}",

                "https":
                f"socks5://127.0.0.1:{port}"

            },

            timeout=TIMEOUT

        )


        delay=int(

            (time.time()-start)*1000

        )


        process.kill()



        if r.status_code in [200,204]:

            return delay,node



    except:

        pass



    return None





def main():


    if not os.path.exists(INPUT):

        open(
            OUTPUT,
            "w"
        ).close()

        return



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
        "真实检测节点:",
        len(nodes)
    )



    results=[]



    with concurrent.futures.ThreadPoolExecutor(

        max_workers=10

    ) as pool:


        for r in pool.map(test,nodes):

            if r:

                results.append(r)



    results.sort(
        key=lambda x:x[0]
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        for delay,node in results[:MAX_RESULTS]:

            f.write(
                node+"\n"
            )



    print(
        "真实可用:",
        len(results)
    )


    if results:

        print(
            "最低延迟:",
            results[0][0],
            "ms"
        )



if __name__=="__main__":

    main()
