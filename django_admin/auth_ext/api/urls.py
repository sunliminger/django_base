from django.urls import re_path
from . import views


urlpatterns = [
    # ========================= 系统用户 ===========================================
    re_path(r'^own/$', views.UserOwn.as_view()),
    re_path(r'^own/has_perm/$', views.UserHasPerm.as_view()),
    re_path(r'^own/menu/$', views.UserOwnMenu.as_view()),
    re_path(r'^logout/$', views.LogoutView.as_view()),

    # jwt
    re_path(r'^token/obtain/$', views.JSONWebTokenObtain.as_view()),

    # ========================= 外部用户 ===========================================
    re_path(r'^external_users/$', views.ExternalUserList.as_view()),
    re_path(r'^external_users/(?P<pk>\d+)/$', views.ExternalUserDetail.as_view()),
    re_path(r'^external_users/(?P<pk>\d+)/refresh/$', views.ExternalUserRefresh.as_view()),

    # ========================= 权限配置 ==========================================
    re_path(r'^permissions/$', views.PermissionListView.as_view()),
    re_path(r'^permissions/(?P<pk>\d+)/$', views.PermissionDetailView.as_view()),

    # ========================= 用户配置 =========================================
    re_path(r'^users/$', views.UserListView.as_view()),
    re_path(r'^users/(?P<pk>\d+)/$', views.UserDetailView.as_view()),

    # ========================== 角色配置 ========================================
    re_path(r'^roles/$', views.RoleListView.as_view()),
    re_path(r'^roles/(?P<pk>\d+)/$', views.RoleDetailView.as_view()),

]
