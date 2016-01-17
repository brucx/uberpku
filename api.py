import leancloud
from leancloud import Object
from leancloud import Query
import json
import datetime

leancloud.init('do4K7UeJcyGgwQ5mdeW4ep07-gzGzoHsz', '5bv5WWc0LuplJbEoadg4TmLH')

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
        'home_lat': entry.get("home_lat"),
        'home_long': entry.set("home_long"),
        'work_lat': entry.set("work_lat"),
        'work_long': entry.set("work_long")
    }
    return json.dumps(obj)


def set_activity(uid, money, calories, home_lat, home_long, work_lat, work_long):
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
        entry.set("home_lat", home_lat)
        entry.set("home_long", home_long)
        entry.set("work_lat", work_lat)
        entry.set("work_long", work_long)
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


def add_schedule(uid, month, time, strategy, start_lat, start_long, end_lat, end_long):
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
        schedule.set("start_lat", start_lat)
        schedule.set("start_long", start_long)
        schedule.set("end_lat", end_lat)
        schedule.set("end_long", end_long)
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


Profile = Object.extend("profile")


def get_profile(uid):
    query = Query(Profile)
    query.equal_to("uid", uid)
    entry = query.first()
    obj = entry.get("profile")
    return obj


def set_profile(uid, profile):
    query = Query(Profile)
    query.equal_to("uid", uid)
    if query.count() == 0:
        entry = Profile()
        obj = {}
    else:
        entry = query.first()
        obj = entry.get("profile")
    for key in profile:
        obj[key] = profile[key]
    entry.set("profile",obj)
    entry.set("uid", uid)
    entry.save()


# test
if __name__ == "__main__":
    uid = datetime.datetime.now().isoformat()
    set_profile(uid, {"a":1, "b":2, "c":3})
    obj = get_profile(uid)
    print(obj)
    set_profile(uid, {"a":2, "d":4, "c":3})
    obj = get_profile(uid)
    print(obj)
