import requests
import base64
import re


# ==========================
# 节点来源
# ==========================

SOURCES = [

    # free-nodes
    "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/sub",

    # aiboboxx
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",

    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2raysub",


    # NoMoreWalls
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt",


    # Free servers
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",


    # V2RayAggregator
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",

]


# ==========================
# 下载订阅
# ==========================

def download(url):

    try:

        print("正在抓取:", url)

        r=requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )

        if r.status_code == 200:

            return r.text


    except Exception as e:

        print("失败:",e)


    return ""



# ==========================
# Base64解码
# ==========================

def decode_base64(text):

    try:

        text=text.strip()

        text += "="*((4-len(text)%4)%4)


        return base64.b64decode(
            text
        ).decode(
            "utf-8",
            errors="ignore"
        )


    except:

        return ""



# ==========================
# 提取节点
# ==========================

def extract(text):

    result=[]


    # 尝试解码

    text=text+"\n"+decode_base64(text)


    rules=[

        r"vmess://[^\s]+",

        r"vless://[^\s]+",

        r"trojan://[^\s]+",

        r"ss://[^\s]+"

    ]


    for rule in rules:

        result.extend(
            re.findall(
                rule,
                text
            )
        )


    return result



# ==========================
# 主程序
# ==========================


nodes=[]


for source in SOURCES:

    data=download(source)

    if data:

        nodes.extend(
            extract(data)
        )



# 去重 保留顺序

nodes=list(
    dict.fromkeys(nodes)
)



print("================")
print("节点数量:",len(nodes))
print("================")



# 保存节点

with open(
    "nodes.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(nodes)
    )



# 生成Base64订阅

subscription=base64.b64encode(

    "\n".join(nodes)
    .encode()

).decode()



with open(
    "sub.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(subscription)



print("生成订阅完成")
