import base64


INPUT="best_nodes.txt"



with open(
    INPUT,
    encoding="utf-8"
) as f:

    nodes=[
        x.strip()
        for x in f
        if x.strip()
    ]



def save(name,data):

    with open(
        name,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(data)
        )



# 全部订阅

save(
    "sub.txt",
    nodes
)



regions={


"hk.txt":[
"HK",
"HKG",
"Hong",
"香港"
],


"tw.txt":[
"TW",
"TWN",
"Taiwan",
"台湾"
],


"us.txt":[
"US",
"USA",
"America",
"美国"
]

}



for filename,keys in regions.items():


    result=[]


    for node in nodes:


        for key in keys:


            if key.lower() in node.lower():

                result.append(node)

                break



    save(
        filename,
        result
    )


    print(
        filename,
        len(result)
    )



print(
    "订阅生成完成"
)
