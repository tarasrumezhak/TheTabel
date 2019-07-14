
# RUN THIS FILE TO QUICKLY TEST IF THE MODEL HAS CRASHED
import requests
import time
if __name__ == "__main__":
    now = time.time()
    url = 'http://104.248.140.247:80/'
    files = {"image": open(r"D:\Max\Projects\TheTabel\atestats\Usachova.jpg", "rb")}
    r = requests.post(url, files=files)
    print("Time: " + str(now - time.time()))
    print(r)
    print(r.json())
    print(r.json().keys())
    print(r.json()['words'])