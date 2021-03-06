import os.path

import django.conf as conf
from django.contrib.auth import logout
from django.contrib.auth import login as org_login
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection, connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
# from django.core import serializers
# from .models import ProjectInfo
from tool import models
import json
from .forms import LoginForm
import quesadiya as q
# from quesadiya.django_tool.manage import projectName
from django.http import JsonResponse
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import DEFAULT_DB_ALIAS, load_backend
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
# def create_connection(alias=DEFAULT_DB_ALIAS):
#     database_root = os.path.join(q.get_projects_path(), "admin.db")
#     # connections.ensure_defaults(database_root)
#     # connections.prepare_test_settings(database_root)
#     db = connections.databases[database_root]
#     backend = load_backend(db['ENGINE'])
#     return backend.DatabaseWrapper(db, database_root)
from django.contrib.auth.backends import ModelBackend
from quesadiya.db.hasher import PH
from argon2.exceptions import VerifyMismatchError


def error(request, *args, **argv):
    logout(request)
    return render(request, "registration/login.html")


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        projectName = request.session['projectName']
        try:
            user = User.objects.using(
                projectName).get(username=username)
        except User.DoesNotExist:
            user = None
            print('no user')
            return user
        try:
            check_password = PH.verify(user.password, password)
        except VerifyMismatchError:
            check_password = False
            # if True and self.user_can_authenticate(user):
            # PH.hash(new_password)
        if check_password:
            return user
        return None


def create_connection(project_name):
    """Create new database connection."""
    db = conf.settings.DATABASES["default"].copy()
    db['NAME'] = os.path.join(q.get_projects_path(),
                              project_name, "project.db")
    conf.settings.DATABASES[project_name] = db


def login(request):
    # print("project Name", os.environ.get("projectName"))
    if request.method == "POST":
        project = json.loads(request.POST.get(
            'selected_project').replace("\'", "\""))
        projectName = project.get("project_name")
        projectId = str(project["project_id"])
        userName = request.POST.get('username')
        password = request.POST.get('password')
        request.session['projectName'] = projectName
        request.session['projectId'] = projectId
        request.session['discardedAnchor'] = ""
        create_connection(projectName)
        md = CustomAuthBackend()
        user = md.authenticate(
            request, username=userName, password=password)
        if user is not None:
            org_login(request, user, 'tool.views.CustomAuthBackend')
            user = {'username': user.username,
                    'is_superuser': user.is_superuser}
            request.session['user'] = user
            if user['is_superuser'] == 1:
                print("ap")
                return redirect("ReviewDiscarded")
            else:
                return redirect("home")
    logout(request)
    return render(request, "registration/login.html ")
    # swapDB("t")
    # request.session['projectName'] = "t"
    # return redirect("home")


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# def checkProjectUser(username, projectId):
#     with connections['admin'].cursor() as cursor:
#         cursor.execute(
#             "SELECT * from project_user where username='"+username+"' and projectId='"+projectId+"'")
#         data = cursor.fetchall()
#     return False if not data else True


def swapDB(projectName):
    if(projectName == "admin"):
        path = conf.settings.DATABASES['admin']['NAME']
    else:
        path = os.path.join(q.get_projects_path(), projectName, "project.db")
    print("old db :", conf.settings.DATABASES['project']['NAME'])
    conf.settings.DATABASES['project']['NAME'] = path
    print("new db :", conf.settings.DATABASES['project']['NAME'])


def getUnfinish(p_name, username):
    with connections[p_name].cursor() as cursor:
        cursor.execute(
            "select * from Triplet_Dataset WHERE status='unfinished' and is_active=1 and username='"+username+"' ORDER by time_changed LIMIT 1")
        data = dictfetchall(cursor)
        if(data == []):
            cursor.execute(
                "select * from Triplet_Dataset WHERE status='unfinished' and is_active=0 ORDER by time_changed LIMIT 1")
            data = dictfetchall(cursor)
        if(data != []):
            cursor.execute("UPDATE triplet_dataset SET time_changed=strftime('%Y-%m-%d %H:%M:%S.%f','now'), is_active=1,username='"+username+"' WHERE anchor_sample_id='" +
                           data[0].get("anchor_sample_id")+"'")
        # cursor.execute(
        #     "UPDATE triplet_dataset SET is_active='1',username='"+username+"' WHERE anchor_sample_id='"+data[0].get("anchor_sample_id")+"'")

    return data
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         "select candidate_sample_id, sample_body, sample_title from candidate_groups INNER join sample_text on sample_text.sample_id = candidate_groups.candidate_sample_id where(candidate_group_id='"+candidate_group_id+"')")
    #     datas = dictfetchall(cursor)
    # return datas


def getSampleData(p_name, sample_id):
    with connections[p_name].cursor() as cursor:
        cursor.execute(
            "select * from sample_text where sample_id='"+sample_id+"'")
        data = dictfetchall(cursor)

    return data


def getCandidateGroup(p_name, candidate_group_id):
    with connections[p_name].cursor() as cursor:
        cursor.execute(
            "select candidate_sample_id, sample_body, sample_title from candidate_groups INNER join sample_text on sample_text.sample_id = candidate_groups.candidate_sample_id where(candidate_group_id='"+candidate_group_id+"')")
        data = dictfetchall(cursor)
    return data


def getProjectUser(p_name):
    with connections[p_name].cursor() as cursor:
        cursor.execute(
            "SELECT username from auth_user")
        data = [item[0] for item in cursor.fetchall()]
    return data


def getInfo(p_name):
    with connections['admin'].cursor() as cursor:
        cursor.execute(
            "select project_name, project_description from projects where project_name='"+p_name+"'")
        data = dictfetchall(cursor)
    data[0]['finished'] = 0
    data[0]['unfinished'] = 0
    data[0]['discarded'] = 0
    data[0]['total'] = 0
    return data
    # return models.Projects.objects.using(
    #     'admin').filter(project_name=p_name)
    # .only("project_name", "project_description")


def datetimeDefault(dt):
    if isinstance(dt, (datetime.date, datetime.datetime)):
        return dt.isoformat()


def updatePositiveAnchor(p_name, anchor_sample_id, positive_sample_id, username):
    with connections[p_name].cursor() as cursor:
        cursor.execute(
            "UPDATE triplet_dataset SET positive_sample_id='"+positive_sample_id+"', status = 'finished',username='"+username+"',is_active=0 WHERE anchor_sample_id='"+anchor_sample_id+"'")


def getStatus(p_name):
    with connections[p_name].cursor() as cursor:
        cursor.execute(
            "select status, count(*) from Triplet_dataset GROUP by status")
        data = cursor.fetchall()
    # data = json.dumps(data)
    total = 0
    for value in data:
        total += value[1]
    data.append(tuple(('total', total)))
    dict(data)
    return data


@ csrf_exempt
def nextAnchor(request):
    if request.method == 'POST':
        projectName = request.session['projectName']
        anchor_sample_id = request.POST.get('anchor_id')
        with connections[projectName].cursor() as cursor:
            cursor.execute(
                "UPDATE triplet_dataset SET time_changed=strftime('%Y-%m-%d %H:%M:%S.%f','now'), status = 'discarded',is_active=0 WHERE anchor_sample_id='"+anchor_sample_id+"'")
        return ProjectInfo(request)


@ csrf_exempt
def updateAnchor(request):
    if request.method == 'POST':
        projectName = request.session['projectName']
        anchor_id = request.POST.get('anchor_id')
        positive_anchor_id = request.POST.get('positive_anchor_id')
        username = request.session['user']['username']
        # username = user.username
        updatePositiveAnchor(projectName, anchor_id,
                             positive_anchor_id, username)
        return ProjectInfo(request)


def ProjectInfo(request):
    # print(request.session['projectName'])
    print(request.user.is_authenticated)
    print(request.user)
    if 'user' in request.session and request.session['user']['is_superuser'] == 0:
        #     print("yess")
        # if(request.user.is_authenticated):
        user = request.session['user']
        username = request.session['user']['username']
        projectName = request.session['projectName']
        projectId = request.session['projectId']
        status = getStatus(projectName)
        projectUser = {"participants": getProjectUser(projectName)}
        infos = getInfo(projectName)
        infos[0].update(status)
        infos[0].update(projectUser)
        if(infos[0]["unfinished"] <= 0):
            return render(request, "home.html", {"infos": infos})
        unfinish_anchor = getUnfinish(projectName, username)
        if(unfinish_anchor == []):
            return render(request, "home.html", {"infos": infos})
        anchor_data = getSampleData(projectName,
                                    unfinish_anchor[0].get("anchor_sample_id"))
        candidate_groups = getCandidateGroup(projectName,
                                             unfinish_anchor[0].get("candidate_group_id"))
        context_dict = {'user': user, 'infos': infos, 'anchor_data': anchor_data,
                        'candidate_groups': candidate_groups}
        return render(request, "home.html", context_dict)
    logout(request)
    return render(request, "registration/login.html")


@ csrf_exempt
def ReviewDiscarded(request):
    if 'user' in request.session and request.session['user']['is_superuser'] == 1:
        if request.method == 'POST':
            anchor_id = request.POST.get('anchor_id')
            request.session['discardedAnchor'] = anchor_id
        discardedAnchor = request.session['discardedAnchor']
        user = request.session['user']
        discardedAnchor = request.session['discardedAnchor']
        projectName = request.session['projectName']
        discarded_anchor = []
        with connections[projectName].cursor() as cursor:
            if discardedAnchor != "":
                cursor.execute(
                    "SELECT anchor_sample_id, status, username,candidate_group_id from triplet_dataset where status='discarded' and anchor_sample_id='"+discardedAnchor+"'")
                discarded_anchor = dictfetchall(cursor)
                print(discarded_anchor, "discarded_anchor")
            if not discarded_anchor:
                print(discarded_anchor, "he ist")
                cursor.execute(
                    "SELECT anchor_sample_id, status, username,candidate_group_id from triplet_dataset where status='discarded' ORDER by anchor_sample_id LIMIT 1")
                discarded_anchor = dictfetchall(cursor)
            cursor.execute(
                "SELECT anchor_sample_id, status, username from triplet_dataset where status='discarded' ORDER by anchor_sample_id ")
            anchors = dictfetchall(cursor)
            # if(discarded_anchor != []):
            #     cursor.execute("UPDATE triplet_dataset SET time_changed=strftime('%Y-%m-%d %H:%M:%S.%f','now') WHERE anchor_sample_id='" +
            #                    discarded_anchor[0].get("anchor_sample_id")+"'")
            # print(discarded_anchor)
        # context_dict = {'anchors': anchors}
        if(discarded_anchor != []):
            anchor_data = getSampleData(projectName,
                                        discarded_anchor[0].get("anchor_sample_id"))
            candidate_groups = getCandidateGroup(projectName,
                                                 discarded_anchor[0].get("candidate_group_id"))

            context_dict = {'anchor_data': anchor_data,
                            'candidate_groups': candidate_groups, 'anchors': anchors}
        else:
            context_dict = {'anchor_data': [],
                            'candidate_groups': []}
        return render(request, "review_discarded.html", context_dict)
    logout(request)
    return render(request, "registration/login.html")


@ csrf_exempt
def UpdateReviewDiscarded(request):
    if request.method == 'POST':
        projectName = request.session['projectName']
        anchor_id = request.POST.get('anchor_id')
        with connections[projectName].cursor() as cursor:
            cursor.execute(
                "UPDATE triplet_dataset SET status='unfinished', username='-1', is_active=0 WHERE anchor_sample_id='"+anchor_id + "'")
        return ReviewDiscarded(request)


@ csrf_exempt
def GetReviewDiscarded(request):
    if 'user' in request.session and request.session['user']['is_superuser'] == 1:
        anchor_id = request.POST.get('anchor_id')
        projectName = request.session['projectName']
        print("getReviewDiscarded", anchor_id)
        with connections[projectName].cursor() as cursor:
            cursor.execute(
                "SELECT anchor_sample_id, status, username,candidate_group_id from triplet_dataset where status='discarded' and anchor_sample_id='"+anchor_id+"'")
            discarded_anchor = dictfetchall(cursor)
            cursor.execute(
                "SELECT anchor_sample_id, status, username from triplet_dataset where status='discarded'")
            anchors = dictfetchall(cursor)
        # context_dict = {'anchors': anchors}
        print(discarded_anchor[0].get("anchor_sample_id"))
        anchor_data = getSampleData(projectName,
                                    discarded_anchor[0].get("anchor_sample_id"))
        candidate_groups = getCandidateGroup(projectName,
                                             discarded_anchor[0].get("candidate_group_id"))
        print(discarded_anchor[0].get("candidate_group_id"))
        context_dict = {'anchor_data': anchor_data,
                        'candidate_groups': candidate_groups, 'anchors': anchors}
        return render(request, "review_discarded.html", context_dict)
    logout(request)
    return render(request, "registration/login.html")


def ViewStatus(request):
    print("welcome from CooperatorStatus")
    if 'user' in request.session and request.session['user']['is_superuser'] == 1:
        user = request.session['user']
        projectName = request.session['projectName']
        # projectId = request.session['projectId']
        with connections[projectName].cursor() as cursor:
            cursor.execute(
                "SELECT au.username,(SELECT count(status) from triplet_dataset where username=au.username and status='discarded') as discarded,(SELECT count(status) from triplet_dataset where username=au.username and status='finished') as finished,count(td.anchor_sample_id) as assigned from auth_user as au left outer join triplet_dataset as td on au.username = td.username where au.is_superuser = 0 GROUP by au.username,discarded,finished")
            statuses = dictfetchall(cursor)
        # context_dict = {'user': user, 'infos': infos, 'anchor_data': anchor_data,
        #                 'candidate_groups': candidate_groups}
        context_dict = {'statuses': statuses}
        return render(request, "view_status.html", context_dict)
    logout(request)
    return render(request, "registration/login.html")


def EditCollaborator(request):
    if 'user' in request.session and request.session['user']['is_superuser'] == 1:
        user = request.session['user']
        print(user)
        projectName = request.session['projectName']
        # projectId = request.session['projectId']
        with connections[projectName].cursor() as cursor:
            cursor.execute(
                "select id,username,is_superuser as status,last_login from auth_user")
            users = dictfetchall(cursor)
        # context_dict = {'user': user, 'infos': infos, 'anchor_data': anchor_data,
        #                 'candidate_groups': candidate_groups}
        context_dict = {'users': users}
        return render(request, "edit_collaborator.html", context_dict)
    logout(request)
    return render(request, "registration/login.html")


@ csrf_exempt
def updateUser(request):
    if request.method == 'POST':
        projectName = request.session['projectName']
        id = request.POST.get('id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        status = request.POST.get('status')
        act = request.POST.get('act')
        # print(id, " ", username, " ", password, " ", status)
        password = PH.hash(password)
        # status = 0 if status.lower() == 'cooperator' else 1
        status = 0
        if act == "0":
            with connections[projectName].cursor() as cursor:
                cursor.execute("UPDATE auth_user SET username='"+username+"',password='" +
                               str(password)+"',is_superuser='"+str(status)+"' WHERE id='"+id+"'")
        elif act == "1":
            with connections[projectName].cursor() as cursor:
                cursor.execute("INSERT INTO auth_user (id, password, is_superuser, username, last_name, email, is_staff, is_active,date_joined, first_name) VALUES ('" +
                               str(id)+"', '"+password+"', '"+str(status)+"', '"+username+"', ' ', ' ', '1', '0', strftime('%Y-%m-%d %H:%M:%S.%f','now'), ' ')")
        return EditCollaborator(request)


@ csrf_exempt
def deleteUser(request):
    if request.method == 'POST':
        projectName = request.session['projectName']
        id = request.POST.get('id')
        username = request.POST.get('username')
        with connections[projectName].cursor() as cursor:
            cursor.execute(
                "DELETE FROM auth_user WHERE username='"+username+"' and id='"+id+"'")
            cursor.execute(
                "UPDATE triplet_dataset SET username=-1, is_active=0 WHERE username='"+username+"' and status='unfinished' and is_active=1 ")
        return EditCollaborator(request)
