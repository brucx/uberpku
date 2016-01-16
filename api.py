import leancloud
from leancloud import Object
from leancloud import Query

leancloud.init('APP_ID', 'APP_KEY')

User = Object.extend("user")

def get_token(uid):
    user = User()
    query = Query(user)
    query.equal_to("uid", uid)
    temp_user = query.find()
    return temp_user.get("token")


def set_token(uid, token):
    user = User()
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
