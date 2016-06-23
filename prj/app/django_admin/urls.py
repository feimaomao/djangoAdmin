from django.conf.urls import url
from views import login,batchCreateUser,upload_user,createDepartment,uploadDepartment,departFind
urlpatterns = [
    url(r'^admin/login/$', login, name='login'),
    url(r'^admin/django_admin/department/departFind/$', departFind, name='departFind'),
    url(r'^admin/django_admin/department/add/createDepartment/$',createDepartment,name='createDepartment'),
    url(r'^admin/django_admin/department/add/uploadDepartment/$', uploadDepartment, name='uploadDepartment'),
    url(r'^admin/django_admin/profileuser/add/batchCreateUser/$', batchCreateUser, name='batchCreateUser'),
    url(r'^admin/django_admin/profileuser/add/upload_user/$',upload_user, name='upload_user'),
]
