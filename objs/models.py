# -*- coding: utf-8 -*-
import re
import datetime, time
from django.db import models

from django.contrib.auth.models import User


class Iteration(models.Model):
    end = models.DateField()

    def __str__(self):
        return self.end.ctime()


class Project(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class UserDedication(models.Model):
    it = models.ForeignKey(Iteration, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hours = models.FloatField()

    def __str__(self):
        return u"%s, %s" % (self.it, self.user)


class UserDedicationPr(models.Model):
    userd = models.ForeignKey(UserDedication, related_name="dedicationpr", on_delete=models.CASCADE)
    percentage = models.FloatField()
    pr = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s, %s, %s" % (self.userd, self.percentage, self.pr)

    def hours(self):
        return self.percentage * self.userd.hours / 100

    def dedicated(self):
        return sum([i.dedicated for i in self.userd.it.projectdedication_set.filter(pr=self.pr, user=self.userd.user)])


class ProjectDedication(models.Model):
    it = models.ForeignKey(Iteration, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pr = models.ForeignKey(Project, on_delete=models.CASCADE)
    dedicated = models.FloatField()
    time = models.DateTimeField()
    commentary = models.CharField(max_length=1024, default='')

    def __str__(self):
        return u"%s, %s, %s, %s" % (self.it, self.user, self.pr, self.dedicated)

    def tags(self):
        return ", ".join(i.tag.name.strip() for i in self.projectdedicationtagged_set.all())

    def taglist(self):
        return [i.tag.name.strip() for i in self.projectdedicationtagged_set.all()]

    def commentlines(self):
        return self.commentary.split('\n')

    class Meta:
        ordering = ['-time']


class ObjUser(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    worklog = models.TextField()
    worklog_lastmodified = models.DateTimeField(auto_now_add=True, editable=True)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    last_used = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.name


class ProjectDedicationTagged(models.Model):
    project_dedication = models.ForeignKey(ProjectDedication, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


def iteration_from_txt(txt):
    endre = re.compile(r'^END (?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)')
    userre = re.compile(r'\s*\*\s*(?P<username>\w+):\s*(?P<hours>\d+)h?')
    prre = re.compile(r'\s*\*\s*(?P<prname>[a-zA-Z0-9áéíóúñÑ\-._ ]+)\s+(?P<hours>\d+)(h|\%)')

    itend = datetime.datetime.now() + datetime.timedelta(7)
    # users = [(USERNAME, HOURS, [(PR1, PERCENTAGE), ...]), ...]
    users = []

    current_user = None

    for line in txt.split("\r\n"):
        match = endre.match(line)
        if match:
            itend = datetime.datetime.strptime("%s/%s/%s" % match.groups(), "%d/%m/%Y")

        match = userre.match(line)
        if match:
            g = match.groups()
            current_user = [g[0], int(g[1]), []]
            users.append(current_user)

        match = prre.match(line)
        if match:
            g = match.groups()
            prname = g[0]
            if g[2] == "h":
                percentage = float(g[1]) * 100.0 / float(current_user[1])
            else:
                percentage = float(g[1])
            pr = [prname, percentage]
            current_user[2].append(pr)

    # creating iteration
    it = Iteration()
    it.end = itend
    it.save()

    # creating user dedication
    for u in users:
        ud = UserDedication()
        ud.it = it
        ud.user = User.objects.get(username=u[0])
        ud.hours = u[1]
        ud.save()

        projects = u[2]
        # creating user dedication project
        for p in projects:
            pd = UserDedicationPr()
            pd.userd = ud
            pd.percentage = p[1]
            obj, created = Project.objects.get_or_create(name=p[0])
            pd.pr = obj
            pd.save()


def add_worklog_from_txt(txt, request):
    datere = re.compile(r'^==\s*(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)\s*==')
    startre = re.compile(r'^(?P<time>\d?\d:\d\d)\s* start (?P<prname>[^,]+)(,*(?P<tags>.+))?')
    stopre = re.compile(r'^(?P<time>\d?\d:\d\d)\s* stop')

    iteration = Iteration.objects.all().order_by('-end')[0]
    current_date = tuple(datetime.datetime.now().strftime("%d/%m/%Y").split("/"))
    last_time = None
    last_project = None

    tags = []
    commentary = None

    ud=UserDedication.objects.filter(it=iteration,user=request.user)[0]
    it_project_ids = [ud.pr.id for ud in ud.dedicationpr.all()]

    for line in txt.split("\r\n"):
        match_date = datere.match(line)
        match_start = startre.match(line)
        match_stop = stopre.match(line)

        if match_date:
            current_date = match_date.groups()
        elif match_start or match_stop:
            if match_start:
                start_time2 = datetime.datetime.strptime("%s/%s/%s %s" % (current_date + (match_start.groups()[0],)), "%d/%m/%Y %H:%M")
                project_name2 = match_start.groups()[1].strip()
                tags2 = []
                if match_start.groups()[3]:
                    tags2 = match_start.groups()[3]
                    tags2 = [i.strip() for i in tags2.split(',')]
            else:
                stop_time = datetime.datetime.strptime("%s/%s/%s %s" % (current_date + (match_stop.groups()[0],)), "%d/%m/%Y %H:%M")

            if last_time or match_stop:
                if match_start:
                    stop_time = start_time2
                start_time = last_time
                project_name = last_project


                dedication = (stop_time - start_time).seconds / 3600.0

                # Get or create project
                project_list = Project.objects.filter(name=project_name)
                if not project_list.count():
                    # create new project
                    pr = Project(name=project_name)
                    pr.save()
                else:
                    pr = project_list[0]
                    # try to select first the projects of this iteration
                    for project_i in project_list:
                        if project_i.id in it_project_ids:
                            pr = project_i
                            break

                pd = ProjectDedication(it=iteration, user=request.user, pr=pr,
                            commentary=commentary, dedicated=dedication)
                pd.time = start_time
                pd.save()

                # tags
                for tag in tags:
                    newtag, created = Tag.objects.get_or_create(name=tag)
                    newtag.save() # modify last_used
                    pdt = ProjectDedicationTagged(tag=newtag, project_dedication=pd)
                    pdt.save()

            if match_start:
                last_time = start_time2
                last_project = project_name2
                tags = tags2
                commentary = ''
            else:
                last_time = None
        elif line.startswith('#'):
            if not commentary:
                commentary = line[1:]
            else:
                commentary += '\n' + line[1:]
        else:
            tags += [i.strip() for i in line.split(',')]
