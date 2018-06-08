from datetime import datetime

from objs.models import Iteration, UserDedication, ProjectDedication
from django.contrib.auth.models import User


def user_overtime(username, start_date=None):
    if not start_date:
        it = Iteration.objects.all().order_by('-end')[0]
        querydate = it.end
    else:
        querydate = datetime.strptime(start_date, "%d/%m/%Y")

    its = Iteration.objects.filter(end__gte=querydate)

    # getting the user
    user = User.objects.get(username=username)

    # the user should dedicated total hours
    total = 0
    d = 0
    for it in its:
        try:
            ud = UserDedication.objects.get(user=user, it=it)
            total += ud.hours

            pds = ProjectDedication.objects.filter(user=user, it=it)
            for pd in pds:
                d += pd.dedicated
        except:
            continue

    return d - total


def all_overtime(start_date=None):
    ret = {}
    for user in User.objects.all():
        ret[user.username] = user_overtime(user.username, start_date)

    return ret
