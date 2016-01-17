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


# to_work: 0 - home to work, 1 - work to home
def add_schedule(uid, month, time, strategy, start_lat, start_long, end_lat, end_long, to_work):
    query = Query(Schedule)
    query.equal_to("uid", uid)
    query.equal_to("month", month)
    query.equal_to("to_work", to_work)
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
        query.equal_to("to_work", to_work)
        schedule.save()
        return True


def del_schedule(uid, month, to_work):
    query = Query(Schedule)
    query.equal_to("uid", uid)
    query.equal_to("month", month)
    query.equal_to("to_work", to_work)
    if query.count == 0:
        return
    else:
        entry = query.first()
        entry.destroy()


def get_coords(uid, to_work):
    now = datetime.datetime.now()
    month = now.year*100 + now.month
    query = Query(Schedule)
    query.equal_to("uid", uid)
    query.equal_to("month", month)
    query.equal_to("to_work", to_work)
    if query.count != 0:
        entry = query.first()
        _str = {
            "start_long": entry.get("start_long"),
            "start_lat": entry.get("start_lat"),
            "end_long": entry.get("end_long"),
            "end_lat": entry.get("end_lat"),
        }
        return json.dumps(_str)
    else:
        return False


def pseudo_schedule():
    _str = [
        {
            "start_time": 0630,
            "start_long": 37.77492950000001,
            "start_lat": -122.31941550000008,
            "end_long": 37.78492950000001,
            "end_lat": -122.30941550000008,
            "strategy": 111110011
        },
        {
            "start_time": 1845,
            "start_long": 37.78492950000001,
            "start_lat": -122.30941550000008,
            "end_long": 37.77492950000001,
            "end_lat": -122.31941550000008,
            "strategy": 111110011
        }
    ]
    return json.dumps(_str)