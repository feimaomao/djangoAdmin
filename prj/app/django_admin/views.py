#coding:utf-8
from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login,)
from forms import (AuthenticationForm,)
from django.shortcuts import render,render_to_response,HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.views import deprecate_current_app
import json
from django_admin.models import Department,profileUser,Departclass,Company
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import six, timezone
import json
# Create your views here.

#查找depart
def departFind(request):
    id_company = request.GET.get("id_company")
    id_departclass = int(request.GET.get("id_departclass"))-1
    departmentQuery = Department.objects.filter( Q(departclass__level__lt=id_departclass) & Q(company=id_company))
    departList = []
    if departmentQuery:
        for department in departmentQuery:
            departList.append({"value":department.id,"name":department.departName})
    else:
        departList.append({"value": "", "name": ""})
    return HttpResponse(json.dumps(departList))


# 自定义登录界面
@deprecate_current_app
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='admin/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
#批量创建公司
def createDepartment(request):
    if request.user.is_active:
        company_list = Company.objects.all()
        departclass_list = Departclass.objects.all()
        company_list = serializers.serialize('json',company_list)
        departclass_list = serializers.serialize('json',departclass_list)
        return render_to_response('sp/importspinfo.html',{'company_list':json.dumps(company_list),
                                                          'departclass_list':json.dumps(departclass_list)})
    else:
        return HttpResponse('请先登录')
@csrf_exempt
def uploadDepartment(request):
    company_id = request.POST.get('company_id')
    departclass_id = request.POST.get('departclass_id')
    spdatas =json.loads(request.POST.get('spdatas'))

#创建公司
    for spinfo in spdatas:
        department = Department.objects.filter(Q(departCode=int(spinfo["departCode"]))&Q(company_id=company_id))
        departFather = Department.objects.filter(departCode = spinfo['departFather'])
        if (len(department)==0) and (len(departFather)!=0):
            proDepartment = Department.objects.create(
                departCode=int(spinfo["departCode"]),
                departName=spinfo["departName"],
                departFather_id = int(departFather[0].id),
                company_id=int(company_id),
                departclass_id=int(departclass_id),
                address = spinfo["address"],
                email=spinfo["email"],
                lng=float(spinfo["lng"]),
                lat=float(spinfo["lat"]),
                contactor=spinfo["contactor"],
                datejoined = timezone.now(),
                phone="95105888",
            )
            spinfo["tag"] = "创建公司成功"
            # print por_company.code
            proUser = profileUser.objects.create(
                password = make_password(proDepartment.departCode),
                username = proDepartment.departCode,
                first_name = proDepartment.departName+'_admin',
                last_name='gl',
                userna = str(proDepartment.departCode)+str(proDepartment.id),
                department_id = proDepartment.id,
                is_superuser = True,
                is_staff = True,
                email = proDepartment.email,
                date_joined = timezone.now(),
                userType = 'gl',
            )
            proUser.save()
            # proDepartment.save()
    #更新公司数据
        else:
            por_company = Department.objects.filter(Q(departCode=int(spinfo["departCode"])) &Q(company_id=company_id)).update(
                departCode=int(spinfo["departCode"]),
                departName=spinfo["departName"],
                departFather_id=int(departFather[0].id),
                company_id=int(company_id),
                departclass_id=int(departclass_id),
                address=spinfo["address"],
                email=spinfo["email"],
                lng=float(spinfo["lng"]),
                lat=float(spinfo["lat"]),
                contactor=spinfo["contactor"],
                departDateJoined=timezone.now(),
                departPhone="95105888",
            )
            spinfo["tag"] = "更新公司数据成功"
    return HttpResponse(json.dumps(spdatas), content_type="application/json")

# 批量创建用户
def batchCreateUser(request):
    if request.user.is_authenticated():
        department_list = Department.objects.filter(Q(departclass__level__gte=request.user.department.departclass.level) & Q(company=request.user.department.company))
        department_list = serializers.serialize('json',department_list)
        return render_to_response('sp/create_user.html',{'department_list':json.dumps(department_list),})
    else:
        return HttpResponse('请先登录')
@csrf_exempt
def upload_user(request):
    department_id = request.POST.get('department_id')
    spdatas =json.loads(request.POST.get('spdatas'))

    #创建用户
    for spinfo in spdatas:
        pro_user = profileUser.objects.filter(Q(username=spinfo["username"])& Q(department_id=department_id))
        if (len(pro_user)==0):
            print 123
            pro_user = profileUser.objects.create(
                username=spinfo["username"],
                password=make_password(str(spinfo['username'])),
                first_name = spinfo["first_name"],
                last_name = 'md',
                userna=spinfo["username"]+str(department_id),
                department_id = department_id,
                is_staff = True
            )
            pro_user.save()
            spinfo["tag"] = "创建用户成功"
#更新用户数据
        else:
            print 222
            profileUser.objects.filter(Q(username=spinfo["username"])& Q(department_id=department_id)).update(
                username=spinfo["username"],
                first_name=spinfo["first_name"],
                last_name='md',
                userna=spinfo["username"] + str(department_id),
                department_id=department_id,
            )
            spinfo["tag"] = "更新用户数据成功"
    return HttpResponse(json.dumps(spdatas), content_type="application/json")