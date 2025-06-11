from rest_framework.views import APIView
from rest_framework.response import *
from rest_framework import status
from models.models import videoUser
from rest_framework import authtoken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

class login(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        #retrieves user data
        return Response({"type": "test"})
    
    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]
        user = None
        
        try:
            user = videoUser.objects.get(username=username)
        except:
            return Response({"message": "username does not exist"}, status=status.HTTP_204_NO_CONTENT)
        
        if not check_password(password, user.password):
            return Response({"message": "incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": f"{token.key}"}, status=status.HTTP_200_OK)

class signup(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]
        print("testing1")
        if videoUser.objects.filter(username=username).exists():
            print(videoUser.objects.filter(username=username).exists())
            return Response({"message": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        print("testing2")
        user = videoUser.objects.createUser(username=username, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": f"{token.key}"}, status=status.HTTP_201_CREATED)

class uploadVideo(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        title = request
        return Response({"message":"posted"}, status=status.HTTP_200_OK)