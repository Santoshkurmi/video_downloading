import requests as req 
import os
import tqdm
from Crypto.Cipher import AES   #pip install pycryptodome
from Crypto.Util.Padding import unpad
import base64
import re
import time
import os
import base64
import hashlib
from base64 import b64decode
from Crypto.Cipher import AES
import m3u8
import requests
import os
import threading
import re
import json
import mmap
import sys


user_id = "74312"
authorization = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6Ijc0MzEyIiwiZW1haWwiOiJraHVtYXBva2hhcmVsMjA3OEBnbWFpbC5jb20iLCJ0aW1lc3RhbXAiOjE3MzI2NDIyNzR9.Wz2iUOpyMzmuo_bi0PV-eu7JgnVVHFXj3PS4SagtmYQ"

host = "https://harkiratapi.classx.co.in"




headers = {
    "Authorization":authorization,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36",
    "Origin": "https://harkirat.classx.co.in",
    "Host": "harkiratapi.classx.co.in",
    "Sec-Ch-Ua-Platform": "Linux",
    "Referer": "https://harkirat.classx.co.in/",
    "Auth-Key": "appxapi"
}

def get_all_purchases():
    res = req.get(host+f"/get/get_all_purchases?userid={user_id}&item_type=10",headers=headers).json()
    res = res["data"]
    return res

def get_titles(id,pid=-1):
    res = req.get(host+f"/get/folder_contentsv2?course_id={id}&parent_id={pid}",headers=headers).json()
    res = res["data"]
    return res

def get_video_token(cid,vid):
    res = req.get(host+f"/get/fetchVideoDetailsById?course_id={cid}&video_id={vid}&ytflag=0&folder_wise_course=1",headers=headers).json()
    token = res["data"]["video_player_token"]
    # cookie = res["data"]["cookie_value"]
    return token

def get_video_enc_links(cid,vid):
    res = req.get(host+f"/get/fetchVideoDetailsById?course_id={cid}&video_id={vid}&ytflag=0&folder_wise_course=1",headers=headers).json()
    res = res["data"]["encrypted_links"]
    # cookie = res["data"]["cookie_value"]
    return res

def get_video_html(token):

    res = req.get(f"https://player.akamai.net.in/secure-player?token={token}&watermark=").text
    return res

# for downloading video in real one



def start():
    courses = get_all_purchases()
    print("\n\n")

    c = 1
    for course in courses:
        name =  course["coursedt"][0]["course_name"]
        # id = course["itemid"]
        print(f"{c}. {name}")
        c = c + 1
    
    choice = input("\n\nEnter the course: ")
    c_title = "courses/"+courses[int(choice)-1]["coursedt"][0]["course_name"]
    cid = courses[int(choice)-1]["itemid"]

    

    os.makedirs(c_title, exist_ok=True)

    titles = get_titles(cid)
    c=1
    if len(titles) !=1:
        for title in titles:
            print(f"{c}. {title['Title']} | {title['material_type']}")
            c = c + 1
    
        choice = input("\nEnter the choice: ")
    else:
        choice = "1"

    pid = titles[int(choice)-1]["id"]

    titles = get_titles(cid,pid)


    choice= input("Choose Download options: \n1. Links only\n2. Download Links and Videos both\n=>")

    


    if True:

        c=1
        for title in titles:
            print(f"\n{c}. Downloading link of '{title['Title']} | {title['material_type']}'")
            vid = title["id"]
            if title['material_type'] !="VIDEO":
                print("Ignoring this file as it is not video")
                continue
            c = c + 1

            if os.path.exists(c_title+"/"+title["Title"]+".html"):
                print("Already downloaded link for "+"'"+title["Title"]+"'\n")
                continue

            # exit()
        
            # choice = input("Enter the choice: ")
            # vid = titles[int(choice)-1]["id"]

            vtoken = get_video_token(cid,vid)
            # print(vtoken)
            # print(cookie)

            html = get_video_html(vtoken)
            html = html.replace('src="/','src="https://player.akamai.net.in/')
            html = html.replace('href="/','href="https://player.akamai.net.in/')
            html = html.replace('"quality":"360p","isPremier":','"quality":"720p","isPremier":')

            # print(c_title)
            if "Token Expired" in html:
                print("This one is expired...\n")
                print("Waiting for 30 seconds to prevent rate limiting\n")
                time.sleep(30)
                continue

            with open(c_title+"/"+title["Title"]+".html","w") as e:
                e.write(html)

            print("Waiting for 30 seconds to prevent rate limiting\n")
            time.sleep(30)


start()