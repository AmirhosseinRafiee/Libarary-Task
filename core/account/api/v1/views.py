from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer

User = get_user_model()


class CustomDiscardAuthToken(APIView):
    """
    API view to discard (delete) the user's authentication token.
    """
    permission_classes = [IsAuthenticated] # Ensure user is authenticated

    def post(self, request, *args, **kwargs):
        # Delete user's auth token
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordApiView(generics.GenericAPIView):
    """
    API view to handle changing the user's password.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated] # Ensure user is authenticated

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj # Get the current user object

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Verify old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Set and save the new password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"detail": "password changed successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
