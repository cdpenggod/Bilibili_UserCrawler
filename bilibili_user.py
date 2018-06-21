# -*-coding:utf8-*-

import requests
import json
import threading
import random
import sys
import os
import csv
import codecs
import datetime
import time
from imp import reload
from multiprocessing.dummy import Pool as ThreadPool

def datetime_to_timestamp_in_milliseconds(d):
    def current_milli_time(): return int(round(time.time() * 1000))

    return current_milli_time()


reload(sys)
sys.setdefaultencoding('utf8')


#判断文件是否存在,不存在则创建
if os.path.exists('bilibiliData.csv') == False:
    with open('bilibiliData.csv','wb+') as csvfile:
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile)
        writer.writerow(["mid","姓名","性别","rank","face","spacesta", \
                         "生日","签名","等级","官方验证类型","官方验证描述","vip类型","vip状态", \
                         "toutu","toutuID","coins","关注数","粉丝数"])


#设置初始默认代理ip
proxies={'http': 'http://120.26.110.59:8080'}


def LoadUserAgents(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1 - 1])
    random.shuffle(uas)
    return uas


#定时更换新ip代理
def getNewIP():
    global proxies
#    try:
#        #可加入请求自己的代理ip设置进行定时更换
#        ipjson = requests.get('http://xxx.json').text
#        ipDic = json.loads(ipjson)
#        ipArr=ipDic['proxy']
#        oneip=random.sample(ipArr,1)[0]
#        theip=str(oneip['ip'])+":"+str(oneip['port'])
#        proxies['http']=theip
#    except:
        oriIPArr=['http://120.26.110.59:8080','http://120.52.32.46:80','http://218.85.133.62:80']
        proxies['http']=random.sample(oriIPArr,1)[0]
#    finally:
        timer = threading.Timer(5,getNewIP)
        timer.start()


#计时器换代理ip
getNewIP()

uas = LoadUserAgents("user_agents.txt")
head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://space.bilibili.com/45388',
    'Origin': 'http://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}


#抓取用户数据(里面会筛选用户粉丝量达标的用户)
def getUserUrl(url):
#    是否打开深度遍历自己修改
#    打开后会加快获取用户数据,但文件里请求到的数据会有重复,所以需要抓取完后根据文件里的用户id进行去重(查看uniq.py)
#    getsource(url,requestFollow=True)
    getsource(url)


def getsource(url,requestFollow=False):
    print("开始抓:"+str(url)+"****ip地址:"+str(proxies))
    payload = {
        '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now()),
        'mid': url.replace('https://space.bilibili.com/', '')
    }
    ua = random.choice(uas)
    head = {
        'User-Agent': ua,
        'Referer': 'https://space.bilibili.com/' + url.replace('https://space.bilibili.com/','') + '?from=search&seid=' + str(random.randint(10000, 50000))
    }
    try:
        jscontent = requests \
            .session() \
            .post('http://space.bilibili.com/ajax/member/GetInfo',
                  headers=head,
                  data=payload,
                  proxies=proxies,
                  timeout=2.5) \
            .text
    except Exception as e:
        print("请求出错"+str(url)+"****ip地址:"+str(proxies)+"****"+str(e))
        return
    try:
        jsDict = json.loads(jscontent)
        statusJson = jsDict['status'] if 'status' in jsDict.keys() else False
        if statusJson == True:
            if 'data' in jsDict.keys():
                jsData = jsDict['data']
                mid = jsData['mid']
                name = jsData['name']
                sex = jsData['sex']
                rank = jsData['rank']
                face = jsData['face']
                spacesta = jsData['spacesta']
                birthday = jsData['birthday'] if 'birthday' in jsData.keys() else 'nobirthday'
                sign = jsData['sign']
                level = jsData['level_info']['current_level']
                OfficialVerifyType = jsData['official_verify']['type']
                OfficialVerifyDesc = jsData['official_verify']['desc']
                vipType = jsData['vip']['vipType']
                vipStatus = jsData['vip']['vipStatus']
                toutu = jsData['toutu']
                toutuId = jsData['toutuId']
                coins = jsData['coins']
                print("Succeed get user info: " + str(mid))
                try:
                    res = requests.get(
                        'https://api.bilibili.com/x/relation/stat?vmid=' + str(mid) + '&jsonp=jsonp',proxies=proxies,timeout=2.5).text
                    js_fans_data = json.loads(res)
                    following = js_fans_data['data']['following']
                    fans = js_fans_data['data']['follower']

                    #深度遍历抓取该用户关注列表用户数据
                    #打开以下注释后会加快获取用户数据,但文件里请求到的数据会有重复,所以需要抓取完后根据文件里的用户id进行去重(查看uniq.py)
                    if requestFollow!=False:
                        getFollowUid(mid)
                    
                    #判断粉丝数是否达标
                    #10000改为0即去除用户粉丝量筛选,保存所有用户数据
                    if fans>=10000:
                        try:
                            with open('bilibiliData.csv','ab+') as csvfile:
                                csvfile.write(codecs.BOM_UTF8)
                                writer = csv.writer(csvfile)
                                writer.writerow([str(mid),str(name),str(sex),str(rank),str(face),str(spacesta), \
                                                 str(birthday),str(sign),str(level),str(OfficialVerifyType),str(OfficialVerifyDesc),str(vipType), str(vipStatus), \
                                                 str(toutu),str(toutuId),str(coins),str(following),str(fans)])
                            print("存入数据 name:"+str(name)+"\t粉丝:"+str(fans))
                        except Exception as e:
                            print("错误"+e)
                    else:
                        print("fans不够:"+str(fans))
                except Exception as a:
                    print("没请求到粉丝数据"+str(a))
                    following = 0
                    fans = 0
            else:
                print("没数据")
        else:
            print("Error: " + url)
    except Exception as e:
        print("解析数据出错"+str(e))
        pass




#深度遍历抓取用户关注列表用户(里面会筛选用户粉丝量达标的用户)
def getFollowUid(mid):
    print("抓取用户最多100页关注列表用户"+str(mid))
    for i in range(1,100):
        url="https://api.bilibili.com/x/relation/followings?vmid="+str(mid)+"&pn="+str(i)+"&ps=20"
        try:
            response = requests.get(url,headers = {'content-type': 'application/json'},proxies=proxies,timeout=2.5)
            jscontent = response.text
        except:
            print("请求关注列表出错"+str(url)+"****ip地址:"+str(proxies))
            return
        else:
            try:
                jsDict = json.loads(jscontent)
                if 'data' in jsDict.keys():
                    jsData = jsDict['data']
                    list=jsData['list']
                    if len(list)==0:
                        return
                    followUrls=[]
                    for dic in list:
                        newMid=dic['mid']
                        followUrls.append('https://space.bilibili.com/' + str(newMid))
                    try:
                        followPool.map(getsource,followUrls)
                    except Exception as e:
                        print(e)
                    print("成功请求用户关注列表"+str(mid))
                else:
                    print('no follow data now')
                    return
            except Exception as e:
                print(e)
                return



if __name__ == "__main__":
    #开启线程池进行抓取
    followPool = ThreadPool(1)
    pool = ThreadPool(2)
    try:
        #设定爬取的用户id范围
        for m in range(0,1000000):
            urls = []
            for i in range(m * 100, (m + 1) * 100):
                url = 'https://space.bilibili.com/' + str(i)
                urls.append(url)
            results = pool.map(getUserUrl,urls)

    except Exception as e:
        print(e)
 
    followPool.close()
    followPool.join()
    pool.close()
    pool.join()
