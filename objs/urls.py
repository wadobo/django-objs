from django.conf.urls import *
from django.conf import settings

from .views import SaveWorklogView, SearchTags

from . import views

urlpatterns = [
    url(r'^$', views.index, name="objs"),
    url(r'^newit$', views.newit, name="objs_newit"),
    url(r'^add_worklog$', views.add_worklog, name="objs_add_worklog"),
    url(r'^save_worklog$', SaveWorklogView.as_view(), name="objs_save_worklog"),
    url(r'^ot$', views.overtime, name="overtime"),
    url(r'^view$', views.view, name="view"),
    url(r'^report$', views.report, name="objs_report"),
    url(r'^report2$', views.report2, name="objs_report2"),
    url(r'^search_tags$', SearchTags.as_view(), name="search_tags"),
]
