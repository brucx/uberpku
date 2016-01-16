import leancloud
from leancloud import Object
from leancloud import Query
import json
import datetime

leancloud.init('APP_ID', 'APP_KEY')

User = Object.extend("user")


def get_token(uid):
    query = Query(User)
    query.equal_to("uid", uid)
    temp_user = query.first()
    return temp_user.get("token")


def set_token(uid, token):
    query = Query(User)
    query.equal_to("uid", uid)
    number = query.count()
    if number == 0:
        temp_user = User()
        temp_user.set("uid", uid)
        temp_user.set("token", token)
        temp_user.save()
    else:
        query.equal_to("uid", uid)
        temp_user = query.first()
        temp_user.set("token", token)
        temp_user.save()


Activity = Object.extend("activity")


def get_activity(uid, month):
    query = Query(Activity)
    query.equal_to("uid", uid)
    query.equal_to("start_time", month)
    entry = query.first()
    obj = {
        'budget_money': entry.get("budget_money"),
        'budget_cal': entry.get("budget_cal"),
        'curr_money': entry.get("curr_money"),
        'curr_cal': entry.get("curr_cal"),
        'curr_time': entry.get("curr_time"),
        'curr_ubers': entry.get("curr_ubers"),
    }
    return json.dumps(obj)


def set_activity(uid, money, calories):
    now = datetime.datetime.now()
    month = now.year*100 + now.month
    query = Query(Activity)
    query.equal_to("uid", uid)
    query.equal_to("start_time", month)
    if query.count() == 0:
        entry = Activity()
        entry.set("uid", uid)
        entry.set("start_time", month)
        entry.set("duration", 30)
        entry.set("budget_money", money)
        entry.set("budget_cal", calories)
        entry.set("curr_money", 0)
        entry.set("curr_cal", 0)
        entry.set("curr_time", 0)
        entry.set("curr_ubers", 0)
        # todo: duration, time!
        entry.save()
    else:
        entry = query.first()
        entry.set("budget_money", money)
        entry.set("budget_cal", calories)
        entry.save()


def update_uber(uid, money, time, calories=0):
    now = datetime.datetime.now()
    month = now.year*100 + now.month
    query = Query(Activity)
    query.equal_to("uid", uid)
    query.equal_to("start_time", month)
    if query.count() == 0:
        return False
    else:
        entry = query.first()
        entry.increment("curr_money", money)
        entry.increment("curr_time", time)
        entry.increment("curr_cal", calories)
        entry.increment("curr_ubers", 1)
        return True


def update_nouber(uid, time, calories, money=0):
    now = datetime.datetime.now()
    month = now.year*100 + now.month
    query = Query(Activity)
    query.equal_to("uid", uid)
    query.equal_to("start_time", month)
    if query.count() == 0:
        return False
    else:
        entry = query.first()
        entry.increment("curr_money", money)
        entry.increment("curr_time", time)
        entry.increment("curr_cal", calories)
        return True

Schedule = Object.extend("schedule")


def add_schedule(uid, month, time, strategy, start, end):
    query = Query(Schedule)
    query.equal_to("uid", uid)
    query.equal_to("month", month)
    query.equal_to("time", time)
    if query.count() != 0:
        return False
    else:
        schedule = Schedule()
        schedule.set("uid", uid)
        schedule.set("month", month)
        schedule.set("time", time)
        schedule.set("strategy", strategy)
        schedule.set("start", start)
        schedule.set("end", end)
        schedule.save()
        return True


def del_schedule(uid, month, time):
    query = Query(Schedule)
    query.equal_to("uid", uid)
    query.equal_to("month", month)
    query.equal_to("time", time)
    if query.count == 0:
        return
    else:
        entry = query.first()
        entry.destroy()
