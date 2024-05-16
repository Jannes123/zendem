# urls.py
import logging
from django.urls import path, include
from django.urls.resolvers import URLResolver
from .views import ClientCollectionSetView, CustomUserCreate, Login, Logout
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

LOGGER = logging.getLogger('coasterx.request')
app_name = 'sendemauth'
urlpatterns = [
    path('contact-list/', ClientCollectionSetView.as_view(), name='contactlist'),
    path('login/', Login.as_view(), name='local_login'),
    path('logout/', Logout.as_view(), name='local_logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/custom-user-create/', CustomUserCreate.as_view(), name='custom_user_create')
]

LOGGER.debug('urlpatterns:')
LOGGER.debug(urlpatterns)
for x in urlpatterns:
    if type(x) == URLResolver:
        LOGGER.debug(x.url_patterns)
    else:
        LOGGER.debug(x)
