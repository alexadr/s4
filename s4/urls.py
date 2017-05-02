"""s4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from app.views import *

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'', TemplateView.as_view(template_name='home.html')),
    # url(r'^createaccount', account_list, name='list'),
    # url(r'^$', account_list, name='list'),
    # url(r'^$(?P<format>[a-z0-9]+)', account_view, name='account_view'),
]


from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.authtoken import views
router = routers.DefaultRouter()
router.register(r'users/', UserViewSet)
router.register(r'accountlist', AccountListViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transactions', TransactionViewSet)

# router.register(r'example', ExampleView.as_view())

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns += [
    url(r'^api/', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    # url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns+=[
    # url(r'^example/',ExampleView.as_view())
    url(r'^api-token-auth/', views.obtain_auth_token)
]

urlpatterns +=[
     url(r'',  TemplateView.as_view(template_name='index.html')),
]


# urlpatterns +=[
#     url(r'^api/login/$', UserLoginAPIView.as_view(), name='login'),
#     # url(r'^api/register/$', UserCreateAPIView.as_view(), name='register'),
# ]


