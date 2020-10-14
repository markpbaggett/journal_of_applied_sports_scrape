import requests

with open("download.txt", "r") as downloads:
    for download in downloads:
        r = requests.get(download.replace("\n", ""))
        with open(
            f'downloads/{download.replace("https://js.sagamorepub.com/jasm/article/download/", "").replace("/", "_").strip()}.pdf',
            "wb",
        ) as current:
            current.write(r.content)
