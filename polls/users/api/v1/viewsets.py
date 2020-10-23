import coreapi
import coreschema
from django.utils import timezone
from django.utils.translation import gettext
from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from polls.core.api.permissions import IsAuthenticatedOnRetrieve, NoDeletes, IsOwnerOrReadOnly
from polls.users.api.v1.serializers import (
    UserSerializer,
    VerifySerializer,
    RequestRestoreCodeSerializer,
    RestorePasswordSerializer,
    QuestionSerializer,
    UserSerializer,
    ChoiceSerializer
)
from polls.users.helpers import verify_email, restore_password
from polls.users.models import User, Choice, Question


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOnRetrieve, NoDeletes]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.request.user.pk)  # Only list current user

    def get_object(self):
        if self.kwargs.get("pk", None) == "me":
            self.kwargs["pk"] = self.request.user.id
        return super().get_object()


me = UserViewSet.as_view({"get": "retrieve", "patch": "partial_update"})


class VerifyViewSet(viewsets.ViewSet):
    """Resource to handle the verification of an user's email."""

    schema = ManualSchema(
        encoding="application/json",
        fields=[
            coreapi.Field(
                "verification_code",
                required=True,
                location="body",
                schema=coreschema.String(
                    description=gettext("Verification code for the user.")
                ),
            )
        ],
    )

    def create(self, request):
        serializer = VerifySerializer(data=request.data)
        if serializer.is_valid():
            verification_code = serializer.validated_data["verification_code"]
            verify_email(verification_code)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestRestoreCodeViewSet(viewsets.ViewSet):
    """Resource to handle the request of a restore password code."""

    schema = ManualSchema(
        encoding="application/json",
        fields=[
            coreapi.Field(
                "email",
                required=True,
                location="body",
                schema=coreschema.String(
                    description=gettext(
                        "Email of the user who is requesting a new code for restore his password."
                    )
                ),
            )
        ],
    )

    def create(self, request):
        serializer = RequestRestoreCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)
            user.send_restore_code()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestorePasswordViewSet(viewsets.ViewSet):
    """Resource to handle the restoration of a password."""

    schema = ManualSchema(
        encoding="application/json",
        fields=[
            coreapi.Field(
                "password",
                required=True,
                location="body",
                schema=coreschema.String(description=gettext("New password for the user.")),
            ),
            coreapi.Field(
                "repeat_password",
                required=True,
                location="body",
                schema=coreschema.String(
                    description=gettext("Repetition of the new password for the user.")
                ),
            ),
            coreapi.Field(
                "restore_password_code",
                required=True,
                location="body",
                schema=coreschema.String(
                    description=gettext(
                        "Code generated by the backend to identify the user who is requesting "
                        "the new password."
                    )
                ),
            ),
        ],
    )

    def create(self, request):
        serializer = RestorePasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data["password"]
            restore_password_code = serializer.validated_data["restore_password_code"]
            restore_password(restore_password_code, password)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ResultsViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'questions': reverse('question-list', request=request, format=format),
    })