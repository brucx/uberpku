import leancloud
from leancloud import Object
from leancloud import Query
import json
import datetime
import predict

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


def get_activity(uid):
    now = datetime.datetime.now()
    month = now.year*100 + now.month
    query = Query(Activity)
    query.equal_to("uid", uid)
    query.equal_to("start_time", month)
    entry = query.first()
    obj = {
        'budget_money': entry.get("budget_money"),
        'budget_cal': entry.get("budget_cal"),
        'budget_ubers': entry.get("budget_ubers"),
        'curr_money': entry.get("curr_money"),
        'curr_cal': entry.get("curr_cal"),
        'curr_time': entry.get("curr_time"),
        'curr_ubers': entry.get("curr_ubers"),
    }
    return obj


def set_activity(uid, money, calories, est_price):
    now = datetime.datetime.now()
    month = now.year*100 + now.month
    query = Query(Activity)
    query.equal_to("uid", uid)
    query.equal_to("start_time", month)
    if query.count() == 0:
        ubers = money/est_price
        entry = Activity()
        entry.set("uid", uid)
        entry.set("start_time", month)
        entry.set("duration", 30)
        entry.set("budget_money", money)
        entry.set("budget_ubers", ubers)
        entry.set("budget_cal", calories)
        entry.set("curr_money", 0)
        entry.set("curr_cal", 0)
        entry.set("curr_time", 0)
        entry.set("curr_ubers", 0)
        # todo: duration, time!
        entry.save()
    else:
        ubers = money/est_price
        entry = query.first()
        entry.set("budget_money", money)
        entry.set("budget_cal", calories)
        entry.set("budget_ubers", ubers)
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


def set_schedule_from_history(uid, history=0):
    _str = predict.predictionSchedule(predict.expandTestData(predict.userHistory))
    for item in _str:
        start_long = item["start_long"]
        start_lat = item["start_lat"]
        end_long = item["end_long"]
        end_lat = item["end_lat"]
        time = item["start_time"]
        strategy = item["strategy"]
        to_work = item["to_work"]
        now = datetime.datetime.now()
        add_schedule(uid, now.month, time, strategy, start_lat, start_long, end_lat, end_long, to_work)


def get_schedule(uid, days, to_work):
    now = datetime.datetime.now()
    # month = now.month
    query = Query(Schedule)
    print uid
    query.equal_to("uid", uid)
    # query.equal_to("month", month)
    # query.equal_to("to_work", to_work)
    _list = list()
    if query.count != 0:
        entry = query.first()
        strategy = entry.get("strategy")
        days_list = predict.ParseStrategyWhichDay(strategy)
        if predict.ParseStrategyIsAvailable(strategy):
            for i in range(0, days):
                if (now.day % 6 + i) not in days_list:
                    _str = {
                        "start_long": entry.get("start_long"),
                        "start_lat": entry.get("start_lat"),
                        "end_long": entry.get("end_long"),
                        "end_lat": entry.get("end_lat"),
                        "time": entry.get("start_time"),
                        "to_work": entry.get("to_work"),
                        "days_from_now": i,
                        "uber": 0
                    }
                else:
                    _str = {
                        "start_long": entry.get("start_long"),
                        "start_lat": entry.get("start_lat"),
                        "end_long": entry.get("end_long"),
                        "end_lat": entry.get("end_lat"),
                        "time": entry.get("start_time"),
                        "to_work": entry.get("to_work"),
                        "days_from_now": i,
                        "uber": 1
                    }
                _list.append(_str)
    return _list


def get_schedule2(uid):
    result0 = get_schedule(uid, 3, 0)
    result1 = get_schedule(uid, 3, 1)
    _list = list()
    _list.append(result0[0])
    _list.append(result1[0])
    _list.append(result0[1])
    _list.append(result1[1])
    _list.append(result0[2])
    _list.append(result1[2])
    return _list


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
        entry.set("uid", uid)
        obj = {}
    else:
        entry = query.first()
        obj = entry.get("profile")
    for key in profile:
        obj[key] = profile[key]
    entry.set("profile", obj)
    entry.save()


if __name__ == "__main__":
    set_schedule_from_history(uid="62fcbc5b-791d-46b1-b9f3-72f1b456ce84", history=0)