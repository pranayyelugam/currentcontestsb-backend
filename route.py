import os
from flask import Flask,jsonify
from time import strptime,strftime,mktime,gmtime,localtime
import json
from urllib2 import urlopen,Request
import threading
from flask.ext.cache import Cache
app = Flask(__name__)
app.cache = Cache(app)

posts= {"ongoing":[] , "upcoming":[]}
hackerrank_contests = {"urls":[]}

def get_duration(duration):
    days = duration/(60*24)
    duration %= 60*24
    hours = duration/60
    duration %= 60
    minutes = duration
    ans=""
    if days==1: ans+=str(days)+" day "
    elif days!=0: ans+=str(days)+" days "
    if hours!=0:ans+=str(hours)+"h "
    if minutes!=0:ans+=str(minutes)+"m"
    return ans.strip()


def fetch_codeforces():
    page = urlopen("http://codeforces.com/api/contest.list")
    data = json.load(page)["result"]
    for item in data:
        
        if item["phase"]=="FINISHED": break
        
        start_time = strftime("%a, %d %b %Y %H:%M",gmtime(item["startTimeSeconds"]+19800))
        end_time   = strftime("%a, %d %b %Y %H:%M",gmtime(item["durationSeconds"]+item["startTimeSeconds"]+19800))
        duration = get_duration( item["durationSeconds"]/60 )
        
        if item["phase"].strip()=="BEFORE":  
            posts["upcoming"].append({ "Name" :  item["name"] , "url" : "http://codeforces.com/contest/"+str(item["id"]) , "StartTime" :  start_time,"EndTime" : end_time,"Platform":"CODEFORCES"  })
        else:
            posts["ongoing"].append({  "Name" :  item["name"] , "url" : "http://codeforces.com/contest/"+str(item["id"])  , "EndTime"   : end_time  ,"Platform":"CODEFORCES"  })


def fetch_hackerearth():
    page = urlopen("https://www.hackerearth.com/chrome-extension/events/")
    data = json.load(page)["response"]

    for item in data:

        start_time = strptime(item["start_tz"].strip()[:19], "%Y-%m-%d %H:%M:%S")
        end_time = strptime(item["end_tz"].strip()[:19], "%Y-%m-%d %H:%M:%S")
        if item["status"]=='ONGOING':
            posts["ongoing"].append({  "Name" :  item["title"] , "url" : item["url"]  , "EndTime"   : strftime("%a, %d %b %Y %H:%M", end_time)  ,"Platform":"Hackerearth","Challenge Type" : item["challenge_type"]  })
        else:
            posts["upcoming"].append({ "Name" :  item["title"] , "url" : item["url"] , "StartTime" :  strftime("%a, %d %b %Y %H:%M", start_time) ,"EndTime" : strftime("%a, %d %b %Y %H:%M", end_time) ,"Platform":"Hackerearth","Challenge Type" : item["challenge_type"]  })

def fetch():
    posts["upcoming"]=[]
    posts["ongoing"]=[]
    fetch_codeforces()
    fetch_hackerearth()
    posts["upcoming"] = sorted(posts["upcoming"], key=lambda k: strptime(k['StartTime'], "%a, %d %b %Y %H:%M"))
    posts["ongoing"] = sorted(posts["ongoing"], key=lambda k: strptime(k['EndTime'], "%a, %d %b %Y %H:%M"))
    posts["timestamp"] = strftime("%a, %d %b %Y %H:%M:%S", localtime())


@app.route("/")
@app.route("/index")

def index():
    
    fetch()
    resp = jsonify(result=posts)
    resp.status_code = 200
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)