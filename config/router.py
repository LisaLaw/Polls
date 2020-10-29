from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from polls.users.api.v1.viewsets import (
    UserViewSet,
    RequestRestoreCodeViewSet,
    RestorePasswordViewSet,
    VerifyViewSet,
    me
)

from polls.pollsapp.viewsets import QuestionViewSet, ResultsViewSet

app_name = 'api_v1'

router = routers.DefaultRouter()
router.register('request_restore_code', viewset=RequestRestoreCodeViewSet, basename="request_restore_code")
router.register('restore_password', viewset=RestorePasswordViewSet, basename="restore_password")
router.register('verify_email', viewset=VerifyViewSet, basename="verify_email")
router.register('users', viewset=UserViewSet)
#include any api endpoints that are specific to app
router.register('questions', viewset=QuestionViewSet)
router.register('results', viewset=ResultsViewSet)

urlpatterns = [
    path('users/me/', me, kwargs={'pk': 'me'}),
    path('', include(router.urls)),
]
