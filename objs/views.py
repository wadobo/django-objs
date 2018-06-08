from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from objs.models import (Iteration, Project, UserDedication,
                         UserDedicationPr, ProjectDedication,
                         Tag, ProjectDedicationTagged)
from objs.models import iteration_from_txt, add_worklog_from_txt, ObjUser
from objs.overtime import all_overtime, user_overtime

from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
import json
import datetime


@login_required
def index(request):
    default_ot = None
    if hasattr(settings, "OVERTIME"):
        default_ot = settings.OVERTIME

    iteration = Iteration.objects.last()
    if not iteration:
        return render(request, 'objs/index.html', {'empty': True})

    try:
        dedication = iteration.userdedication_set.filter(user=request.user)[0]
    except:
        raise Http404
    dedicationpr = dedication.dedicationpr.all()
    dedicated = iteration.projectdedication_set.filter(user=request.user)
    time_dedicated = sum([i.dedicated for i in dedicated])

    # all users
    all_dedicated = iteration.projectdedication_set.all()
    all_time_dedicated = sum([i.dedicated for i in all_dedicated])
    user_dedication = {}
    for i in all_dedicated:
        n = i.user.username
        user_dedication[n] = user_dedication.get(n, 0) + i.dedicated

    all_dedication = iteration.userdedication_set.all()
    all_dedication_hours = sum(i.hours for i in all_dedication)
    all_dedicationpr = ((user_dedication.get(i.user.username, 0), i, i.user, i.dedicationpr.all()) for i in all_dedication)
    obj_user, created = ObjUser.objects.get_or_create(user=request.user)

    projects = Project.objects.all().order_by('name')

    context = {'user': request.user,
               'it': iteration,
               'dedication': dedication,
               'dedicationpr': dedicationpr,
               'dedicated': dedicated,
               'time_dedicated': time_dedicated,
               #all users
               'all_dedication': all_dedication,
               'all_dedication_hours': all_dedication_hours,
               'all_dedicationpr': all_dedicationpr,
               'all_dedicated': all_dedicated,
               'all_time_dedicated': all_time_dedicated,
               'projects': projects,
               'worklog': obj_user.worklog,
               'errors': None,
               'ot': user_overtime(request.user.username, default_ot),
               }

    if request.method == 'POST':
        prname = request.POST['prselect']
        if prname == '--':
            prname = request.POST['pr']
        try:
            time = float(request.POST['spent'])
        except ValueError:
            context['errors'] = _("That's not a number... please, "
                                  "time in hours. You can use dot "
                                  "to fractional time.")

        tags = request.POST['tags']
        tags = [i.strip() for i in tags.split(',') if i]

        if not context['errors']:
            pr = Project.objects.filter(name=prname)
            if not pr.count():
                # create new project
                pr = Project(name=prname)
                pr.save()
            else:
                pr = pr[0]

            pd = ProjectDedication(it=iteration, user=request.user, pr=pr,
                                   dedicated=time)
            pd.time = datetime.datetime.now()
            pd.save()

            # tags
            for tag in tags:
                newtag, created = Tag.objects.get_or_create(name=tag)
                pdt = ProjectDedicationTagged(tag=newtag, project_dedication=pd)
                pdt.save()

            return redirect(index)

    return render(request, 'objs/index.html', context)


@login_required
def report2(request):
    projects = request.GET.getlist('project')
    startdate = request.GET['startdate']
    enddate = request.GET['enddate']

    context = {}
    projects = Project.objects.filter(name__in=projects)
    # magic. Do not touch if you are not a python wizard
    startdate = datetime.datetime(*reversed([int(i) for i in startdate.split("/")]))
    enddate = datetime.datetime(*reversed([int(i) for i in enddate.split("/")]))

    dedications = ProjectDedication.objects.filter(pr__in=projects, time__gt=startdate, time__lt=enddate)
    dedications = dedications.order_by('-time')

    context['projects'] = projects
    context['dedications'] = dedications
    context['total'] = sum(i.dedicated for i in dedications)

    startdate_str = startdate.strftime("%d/%m/%Y")
    enddate_str = enddate.strftime("%d/%m/%Y")
    prs = ", ".join(pr.name for pr in projects)
    header = "'%s' Dedication report from %s to %s" % (prs, startdate_str, enddate_str)
    context['header'] = header

    return render(request, 'objs/report.txt', context)


@login_required
def report(request):
    if request.method != 'POST':
        raise Http404

    projects = request.POST.getlist('project')
    startdate = request.POST['startdate']
    enddate = request.POST['enddate']

    if request.POST.get('button', '') == 'report2':
        args = '?startdate='+startdate+'&enddate='+enddate
        for pr in projects:
            args += '&project='+pr
        return HttpResponseRedirect(reverse('objs_report2') + args)

    #project = "i+d"
    #startdate = "01/07/2011"
    #enddate = "30/07/2011"

    project = Project.objects.get(name=projects[0])

    # magic. Do not touch if you are not a python wizard
    startdate = datetime.datetime(*reversed([int(i) for i in startdate.split("/")]))
    enddate = datetime.datetime(*reversed([int(i) for i in enddate.split("/")]))

    dedication_per_day = {}

    for d in ProjectDedication.objects.filter(pr=project, time__gt=startdate, time__lt=enddate):
        key = d.time.strftime("%Y/%m/%d")

        if key in dedication_per_day:
            dedication_per_day[key].append(d)
        else:
            dedication_per_day[key] = [d]

    startdate_str = startdate.strftime("%d/%m/%Y")
    enddate_str = enddate.strftime("%d/%m/%Y")
    ret = "'%s' Dedication report from %s to %s" % (project.name, startdate_str, enddate_str)
    # underline
    ret += "\n" + "=" * len(ret) + "\n\n"

    days_sorted = sorted(dedication_per_day.keys())

    dedications_per_sorted_days = {}

    total = 0

    def rnd(max_num):
        from binascii import hexlify
        from os import urandom
        return int(hexlify(urandom(3)), 16) % max_num

    for k in days_sorted:
        last_data = {"username": "", "dedicated": 0.0, "tags": []}

        daytotal = 0
        dedications_per_sorted_days[k] = {"daytotal": 0, "dedications": []}
        for d in sorted(dedication_per_day[k], key=lambda x: x.user.username):
            total += d.dedicated
            daytotal += d.dedicated
            if last_data["username"] == d.user.username:
                last_data["dedicated"] += d.dedicated
                last_data["tags"] += d.taglist()
            else:
                if last_data["username"] != "":
                    dedications_per_sorted_days[k]["dedications"].append(last_data)
                last_data = {"username": d.user.username, "dedicated": d.dedicated, "tags": d.taglist()}
        if last_data["username"] != "":
            dedications_per_sorted_days[k]["dedications"].append(last_data)
        dedications_per_sorted_days[k]["daytotal"] = daytotal

    if total != int(total):
        diff = 1 - (total - int(total))
        dedications = list(dedications_per_sorted_days.values())
        k = rnd(len(dedications))
        dedications[k]["daytotal"] += diff
        total += diff
        r = rnd(len(dedications[k]["dedications"]))
        dedications[k]["dedications"][r]["dedicated"] += diff

    for k in days_sorted:
        date = datetime.datetime(*[int(i) for i in k.split("/")])
        date_str = date.strftime("%d/%m/%Y, %A")
        ret += "* %s" % date_str
        ret += "\n" + "-" * (len(date_str)+2) + "\n"

        for d in dedications_per_sorted_days[k]["dedications"]:
            tags = ", ".join(set(d["tags"]))
            ret += "   * %s, %.2f hours, (%s)\n" % (d["username"], d["dedicated"], tags)

        ret += "\n total in day: %.2f hours\n" % dedications_per_sorted_days[k]["daytotal"]
        ret += "\n"

    ret += "\nTotal: %d hours\n" % total

    return HttpResponse(ret, content_type="text/plain")


@login_required
def newit(request):
    if request.method != 'POST':
        context = { 'error': None, 'data': '' }
        return render(request, 'objs/newit.html', context)
    else:
        data = request.POST['input']
        try:
            iteration_from_txt(data)
        except Exception as e:
            context = { 'error': e, 'data': data }
            return render(request, 'objs/newit.html', context)

        return redirect(index)

@login_required
def add_worklog(request):
    if request.method != 'POST':
        messages.add_message(request, messages.ERROR, _('You tried to '
            'save worklog improperly via GET.'))
    else:
        data = request.POST['worklog']
        try:
            add_worklog_from_txt(data, request)
            obj_user, created = ObjUser.objects.get_or_create(user=request.user)
            obj_user.worklog = ''
            obj_user.worklog_lastmodified = datetime.datetime.now()
            obj_user.save()
        except Exception as e:
            messages.add_message(request, messages.ERROR, _('Error saving worklog: %s') % e.message)
            return redirect(index)

    return redirect(index)


@login_required
def overtime(request):
    default_ot = None
    if hasattr(settings, "OVERTIME"):
        default_ot = settings.OVERTIME

    its = [i.end.strftime("%d/%m/%Y") for i in Iteration.objects.all().order_by("-end")]

    if request.method != 'POST':
        all_ot = all_overtime(default_ot)
        context = { 'error': None, 'all_ot': all_ot, 'def': default_ot, 'its': its }
        return render(request, 'objs/overtime.html', context)
    else:
        data = request.POST['date']
        try:
            all_ot = all_overtime(start_date=data)
        except Exception as e:
            context = { 'error': e, 'all_ot': None, 'def': data, 'its': its }
            return render(request, 'objs/overtime.html', context)

        context = { 'error': None, 'all_ot': all_ot, 'def': data, 'its': its }
        return render(request, 'objs/overtime.html', context)


@login_required
def view(request):
    tags = request.GET.getlist('tag')
    projects = request.GET.getlist('project')

    objs = []
    for tag in tags:
        t = ProjectDedicationTagged.objects.filter(tag__name=tag)
        objs += [i.project_dedication for i in t]

    for project in projects:
        objs += list(ProjectDedication.objects.filter(pr__name=project))

    total = sum(d.dedicated for d in objs)

    context = { 'name': ', '.join(tags + projects), 'objs': objs, 'total': total }
    return render(request, 'objs/view.html', context)

class SearchTags(View):
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            data = []
        else:
            time_threshold = datetime.datetime.now() - datetime.timedelta(days=30)
            tags = Tag.objects.filter(name__icontains=query, last_used__gt=time_threshold)
            data = [t.name for t in tags]
        return HttpResponse(json.dumps(data), content_type='application/json')


class SaveWorklogView(View):
    def post(self, request):
        worklog = request.POST.get('worklog', '')
        obj_user, created = ObjUser.objects.get_or_create(user=self.request.user)
        obj_user.worklog = worklog
        obj_user.worklog_lastmodified = datetime.datetime.now()
        obj_user.save()
        return HttpResponse(json.dumps({}), content_type='application/json')


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SaveWorklogView, self).dispatch(*args, **kwargs)
