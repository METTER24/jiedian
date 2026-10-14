import requests
import base64
import re
import time


# 多个公开订阅源
SOURCES = [

# free-nodes

"https://raw.githubusercontent.com/free-nodes/v2rayfree/main/sub",


# aiboboxx

"https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",

"https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2raysub",


# nodefree

"https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",


# clash订阅合集

"https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt",


# Pawdroid

"https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",


# 其他公开源

"https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/v2ray",

]

def get_source(url):

    try:

        print("抓取:", url)

        r=requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )

        if r.status_code==200:

            return r.text

    except Exception as e:

        print(e)

    return ""



def decode_base64(text):

    try:

        text=text.strip()

        missing=len(text)%4

        if missing:

            text += "="*(4-missing)


        return base64.b64decode(
            text
        ).decode(
            "utf-8",
            errors="ignore"
        )


    except:

        return ""
这样很多：

vmess://
vless://
ss://
trojan://


def extract_nodes(text):

    nodes=[]


    # 解码可能存在的base64订阅

    text += "\n"+decode_base64(text)



    patterns=[

        r"vmess://\S+",

        r"vless://\S+",

        r"trojan://\S+",

        r"ss://\S+"

    ]


    for p in patterns:

        result=re.findall(
            p,
            text
        )

        nodes.extend(result)



    return nodes



all_nodes=[]


for url in SOURCES:

    data=get_source(url)

    all_nodes.extend(
        extract_nodes(data)
    )


# 去重，保持顺序
all_nodes = list(dict.fromkeys(all_nodes))


print(
    "总节点:",
    len(all_nodes)
)


# 保存原始节点

with open(
    "nodes.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(all_nodes)
    )



# 生成订阅

sub=base64.b64encode(

    "\n".join(all_nodes)
    .encode()

).decode()



with open(
    "sub.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(sub)



print("完成")
