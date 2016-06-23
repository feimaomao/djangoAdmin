#coding:utf-8
from __future__ import unicode_literals
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.db.models.manager import EmptyManager
from django.utils import six, timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import Permission,Group,UserManager,PermissionsMixin
from django.contrib.auth.models import _user_get_all_permissions,_user_has_perm,_user_has_module_perms


# Create your models here.
#自定义用户
class CompanyManager(models.Manager):
    use_in_migrations = True
    def get_by_natural_key(self, code):
        return self.get(companyCode=code)

@python_2_unicode_compatible
class Company(models.Model):
    companyCode = models.CharField(max_length=80, unique=True,verbose_name='客户代码')
    companyName = models.CharField( max_length=80, unique=True,verbose_name='客户名称')
    isvalue = models.BooleanField(default=True,verbose_name='当前是否有效')
    email = models.EmailField(verbose_name='邮箱', blank=True, null=True)
    contactor = models.CharField(max_length=30, verbose_name='联系人', blank=True, null=True)
    phone = models.CharField(max_length=30, verbose_name='联系电话', blank=True, null=True)
    datestart = models.DateTimeField(default=timezone.now, verbose_name='服务开始时间', blank=True, null=True)
    datefinish = models.DateTimeField(verbose_name='服务结束时间', blank=True, null=True)
    objects = CompanyManager()

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        db_table = 'auth_company'
    def __str__(self):
        return self.companyName
    def natural_key(self):
        return (self.id)

#自定义级别
class DepartclassManager(models.Manager):
    """
    The manager for the auth's Group model.
    """
    use_in_migrations = True
    def get_by_natural_key(self, code):
        return self.get(departclassLevel=code)
@python_2_unicode_compatible
class Departclass(models.Model):
    level = models.DecimalField(max_digits=10, decimal_places=1, unique=True,verbose_name='级别')
    name = models.CharField(max_length=80, unique=True,verbose_name='级别名称')
    objects = DepartclassManager()
    class Meta:
        verbose_name ='级别'
        verbose_name_plural = verbose_name
        db_table = 'auth_departclass'
    def __str__(self):
        return self.name
    #待修改

    def natural_key(self):
        return (self.id)

#自定义单位
class DepartmentManager(models.Manager):
    """
    The manager for the auth's Group model.
    """
    use_in_migrations = True

    def get_by_natural_key(self, code):
        return self.get(departCode=code)

@python_2_unicode_compatible
class Department(models.Model):
    departFather = models.ForeignKey('self',blank=True,null=True,default=None,verbose_name='上级单位')
    departCode = models.CharField( max_length=80,verbose_name='单位代码')
    departName = models.CharField(max_length=80,verbose_name='单位名称')
    company = models.ForeignKey(Company, default=1, verbose_name='客户名称')
    departclass = models.ForeignKey(Departclass, default=10, verbose_name='单位级别')
    objects = DepartmentManager()

    lng = models.DecimalField(max_digits=15, decimal_places=8, verbose_name='经度',blank=True,null=True)
    lat = models.DecimalField(max_digits=15, decimal_places=8, verbose_name='纬度',blank=True,null=True)

    address = models.CharField( max_length=100, verbose_name='单位地址',blank=True,null=True)
    email = models.EmailField(verbose_name='邮箱')
    contactor = models.CharField( max_length=30, verbose_name='联系人',blank=True,null=True)
    phone = models.CharField( max_length=30, verbose_name='联系电话',blank=True,null=True)
    datejoined = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    class Meta:
        verbose_name ='单位'
        verbose_name_plural = verbose_name
        db_table = 'auth_department'
        unique_together = (("departCode", "company"),)
    def __str__(self):
        return self.departName

    def natural_key(self):
        return (self.id)

#在调用create_superuser方法中添加了UserIsSuper =True
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        #添加的
        extra_fields.setdefault('UserIsSuper', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, email, password, **extra_fields)
#自定义用户：添加单位字段,userna作为主键字段,将原先USERNAME_FIELD改为userna,因为这里需要一个唯一字段
# REQUIRED_FIELDS添加username
# department与username字段组合唯一
#表名设置和未更改前一致 auth_user
# is_super判断是否是系统管理员
# usertype判断用户是否是管理员

class profileUser(AbstractBaseUser, PermissionsMixin):
    """
        An abstract base class implementing a fully featured User model with
        admin-compliant permissions.

        Username and password are required. Other fields are optional.
        """
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=False,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()
    # 添加的
    department = models.ForeignKey(Department, default=2, verbose_name='单位名称')
    userType = models.CharField(max_length=2,
                                choices=(
                                    ('gl', '管理员'),
                                    ('md', '普通用户'),
                                ),default='md', verbose_name='用户类型')
    userna = models.CharField(max_length=100, unique=True, default='first', verbose_name='作为主键的字段')
    UserIsSuper = models.BooleanField(default=False, verbose_name='是否是超级用户')
    USERNAME_FIELD = 'userna'
    REQUIRED_FIELDS = ['email','username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        # abstract = True  不设为抽象的，不然会报错
        unique_together = (("username", "department"),)
        db_table = 'auth_user'
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)