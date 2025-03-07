import requests as req 
import os
import base64
import re
import time
import os
import base64
import hashlib
from base64 import b64decode
from Crypto.Cipher import AES
import requests
import os
import threading
import re
import json
import mmap
import sys


user_id = "582457"
authorization = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjU4MjQ1NyIsImVtYWlsIjoidmlza3VtYXJiaXQwMDFAZ21haWwuY29tIiwidGltZXN0YW1wIjoxNzQxMzMwMDcxLCJ0ZW5hbnRUeXBlIjoidXNlciIsInRlbmFudE5hbWUiOiIiLCJ0ZW5hbnRJZCI6IiIsImRpc3Bvc2FibGUiOmZhbHNlfQ.86oVW0qvAg2bd65MYlhwBVEwu4r96iqiBtotif3w68k"

host = "https://parmaracademyapi.classx.co.in"

headers = {
    "Authorization": authorization,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Origin": "https://www.parmaracademy.in",
    "Referer": "https://www.parmaracademy.in/",
    "Sec-Ch-Ua-Platform": "Windows",
    "Auth-Key": "appxapi",
    "Client-Service": "Appx",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

def get_all_purchases():
    # res = req.get(host+f"/get/get_all_purchasesv2?userid={user_id}&item_type=1",headers=headers).json()
    res = req.get(host+f"/get/courselist?exam_name=&start=0",headers=headers).json()
    res = res["data"]
    return res

def get_titles(id,pid=-1):
    res = req.get(host+f"/get/allsubjectfrmlivecourseclass?courseid={id}&start={pid}",headers=headers).json() 
    res = res["data"]
    return res

def get_titles_of_toipic(id,pid):
    res = req.get(host+f"/get/alltopicfrmlivecourseclass?courseid={id}&subjectid={pid}&start=-1",headers=headers).json() 
    res = res["data"]
    return res

def get_all_video_links(id,pid, tid):
    res = req.get(host+f"/get/livecourseclassbycoursesubtopconceptapiv3?courseid={id}&subjectid={pid}&topicid={tid}&conceptid=&windowsapp=false&start=-1",headers=headers).json()
    res = res["data"]
    return res
  
def get_video_token(cid,vid):
    res = req.get(host+f"/get/fetchVideoDetailsById?course_id={cid}&video_id={vid}&ytflag=0&folder_wise_course=0",headers=headers).json()
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


course_name = ""
subject_name = ""
topic_name = ""
video_name = ""

def start():
    courses = get_all_purchases()
    print("\n\n")

    c = 1
    for course in courses:
        name =  course["course_name"]
        # id = course["itemid"]
        print(f"{c}. {name}")
        c = c + 1
    
    choice = input("\n\nEnter the course: ")
    course_name = "courses/" + courses[int(choice)-1]["course_name"]
    cid = courses[int(choice)-1]["id"] # CourseID
 

    os.makedirs(course_name, exist_ok=True)

    titles = get_titles(cid) # get all subject of that course
    c=1
    if len(titles) !=1:
        for title in titles:
            print(f"{c}. {title['subject_name']}")
            c = c + 1
    
        choice = input("\nEnter the subject choice: ")
    else:
        choice = "1"
      
    pid = titles[int(choice)-1]["subjectid"] # SubjectID
    subject_name = course_name + "/" + titles[int(choice)-1]["subject_name"] 

    titles = get_titles_of_toipic(cid, pid) # get all topic of that subject

    # topicID
    c=1
    if len(titles) !=1:
        for title in titles:
            print(f"{c}. {title['topic_name']}")
            c = c + 1
    
        choice = input("\nEnter the toipc choice: ")
    else:
        choice = "1"

    tid = titles[int(choice)-1]["topicid"] # toipcID
    topic_name = subject_name + "/" + titles[int(choice)-1]["topic_name"]



    videos = get_all_video_links(cid, pid, tid)

    os.makedirs(topic_name, exist_ok=True)

    for idx, video in enumerate(videos):
        print(f"{idx+1}: {video['Title']} - {video['id']}")
        new_video_title = re.sub(r'\W', '', video['Title'])
        token = get_video_token(cid, video['id'])
        video_name = topic_name  + "/" +  new_video_title + ".html"
    
        if os.path.exists(video_name):
          print("Already downloaded link for "+"'"+new_video_title+"'\n")
          continue

        video_html = get_video_html(token)
        video_html = video_html.replace('src="/','src="https://www.parmaracademy.in/')
        video_html = video_html.replace('href="/','href="https://www.parmaracademy.in/')
        video_html = video_html.replace('"quality":"360p","isPremier":','"quality":"720p","isPremier":')

        if "Token Expired" in video_html:
            print("This one is expired...\n")
            # print("Waiting for 30 seconds to prevent rate limiting\n")
            # time.sleep(30)
            continue
        
        with open(video_name,"w") as e:
            e.write(video_html)

        # print("Waiting for 30 seconds to prevent rate limiting\n")
        # time.sleep(30)

start()
