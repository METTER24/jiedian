import requests
import base64
import re
import time


# 多个公开订阅源
SOURCES = [

    # v2rayfree
    "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/sub",

    # 其他公开订阅示例
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",

    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2raysub",

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

        return base64.b64decode(
            text+"==="

        ).decode(
            errors="ignore"
        )

    except:

        return text



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


# 去重

all_nodes=list(
    set(all_nodes)
)


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
