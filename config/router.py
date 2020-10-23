from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from polls.users import views
from polls.users.api.v1.viewsets import (
    UserViewSet,
    RequestRestoreCodeViewSet,
    RestorePasswordViewSet,
    VerifyViewSet,
    QuestionViewSet,
    ResultsViewSet,
    me
)

app_name = 'api_v1'

router = routers.DefaultRouter()
router.register('request_restore_code', viewset=RequestRestoreCodeViewSet, basename="request_restore_code")
router.register('restore_password', viewset=RestorePasswordViewSet, basename="restore_password")
router.register('verify_email', viewset=VerifyViewSet, basename="verify_email")
router.register('users', viewset=UserViewSet)
router.register('questions', viewset=QuestionViewSet)
router.register('results', viewset=ResultsViewSet)

urlpatterns = [
    path('users/me/', me, kwargs={'pk': 'me'}),
    path('', include(router.urls)),
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
