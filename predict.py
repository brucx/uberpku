# -*- coding: utf-8 -*-

import json
import time
from collections import OrderedDict
from math import radians, cos, sin, asin, sqrt

userHistory = """{
        "offset": 0,
        "limit": 1,
        "count": 5,
        "history": [
            {
                "status":"completed",
                "distance":1.64691465,
                "request_time":1428876188,
                "start_time":1428876374,
                "start_city":{
                "latitude":37.7749295,
                "display_name":"San Francisco",
                "longitude":-122.4194155},
            "end_time":1428876927,
            "request_id":"37d57a99-2647-4114-9dd2-c43bccf4c30b",
            "product_id":"a1111c8c-c720-46c3-8534-2fcdd730040d"
            }
        ]
    }"""

jsonObj = json.loads(userHistory)


# 扩展测试数据(制造多份测试数据)
def expandTestData(userHistoryStr):
    jsonList = []
    for i in range(5):
        jsonObj = json.loads(userHistoryStr)
        if i % 3 is 0:
            jsonObj["history"][0]["start_time"] += 12 * 3600
            jsonObj["history"][0]["end_time"] += 12 * 3600
            jsonObj["history"][0]["start_city"]["longitude"] += 0.1
        jsonList.append(jsonObj)
    return jsonList


jsonList = expandTestData(userHistory)
print(json.dumps(jsonList))

# 经度1，纬度1，经度2，纬度2 （十进制度数）
def haversine(lon1, lat1, lon2, lat2):
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r


# 存在满足限制条件的元素
# 存在满足限制条件的元素则返回元素ID，否则返回None
def IsExistDistanceIsLess(dic, places, edistance):
    for item in dic.items():
        distance = haversine(item[1]["latitude"] / item[1]["time"],
                             item[1]["longitude"] / item[1]["time"],
                             places["start_city"]["latitude"],
                             places["start_city"]["longitude"])
        if distance <= edistance:
            return item[0]
    return None


# add_schedule(uid, month, time, strategy, start, end)
# 根据json的list推测出用户的行程
# 参数：historyJsonList-历史json列表
# 返回值：	[{出发地，目的地，出发时间}...]
def predictionSchedule(historyJsonList):
    if len(historyJsonList) <= 0:
        return None
    scheduleList = []
    places = {}
    id = 1
    for jsonObj in historyJsonList:
        for record in jsonObj["history"]:
            # 多个地点的距离在100m以内则认为是同一个地点
            location = IsExistDistanceIsLess(places, record, 0.1)
            if location is not None:
                places[location]["time"] += 1
                places[location]["start_time"] += record["start_time"]
                places[location]["end_time"] += record["end_time"]
                places[location]["latitude"] += record["start_city"]["latitude"]
                places[location]["longitude"] += record["start_city"]["longitude"]

            else:
                places[id] = {"id": id,
                              "time": 1,
                              "start_time": record["end_time"],
                              "end_time": record["start_time"],
                              "latitude": record["start_city"]["latitude"],
                              "longitude": record["start_city"]["longitude"]}
                id += 1
    places = OrderedDict(sorted(places.items(), key=lambda x: x[1]["time"], reverse=True))
    # 上车频率最高的地点推测为家
    home = places.items()[0]
    places.pop(home[0])
    for item in places.items():
        # 如果与家相聚20KM且每次打车的平均时间误差低于10min，则认为该地为公司
        if haversine(home[1]["latitude"] / home[1]["time"], home[1]["longitude"] / home[1]["time"]
                , item[1]["latitude"] / item[1]["time"], item[1]["longitude"] / item[1]["time"]) < 20 \
                and abs(((home[1]["end_time"] - home[1]["start_time"]) / home[1]["time"])
                                - ((item[1]["end_time"] - item[1]["start_time"]) / item[1]["time"])) < 10 * 60:
            return [{"starting": (home[1]["latitude"] / home[1]["time"],
                                  home[1]["longitude"] / home[1]["time"]),
                     "destination": (item[1]["latitude"] / item[1]["time"],
                                     item[1]["longitude"] / item[1]["time"]),
                     "start_time": item[1]["start_time"] / item[1]["time"]}]

    return [{"starting": (home[1]["latitude"] / home[1]["time"],
                          home[1]["longitude"] / home[1]["time"]),
             "destination": None,
             "start_time": home[1]["start_time"] / home[1]["time"]}]


print(predictionSchedule(expandTestData(userHistory)))
