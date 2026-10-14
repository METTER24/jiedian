import requests
import os


url = "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/sub"


os.makedirs(
    "output",
    exist_ok=True
)


try:

    r = requests.get(
        url,
        timeout=30
    )

    r.raise_for_status()


    open(
        "output/raw.txt",
        "w",
        encoding="utf-8"
    ).write(
        r.text
    )


    print(
        "download success"
    )


except Exception as e:

    print(e)
