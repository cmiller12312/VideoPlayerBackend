from rest_framework.views import APIView
from rest_framework.response import *
from rest_framework import status
from models.models import videoUser
from rest_framework import authtoken
from rest_framework.authtoken.models import Token

class login(APIView):
    def get(self, request):
        #retrieves user data
        return Response({"type": "test"})
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = None
        
        try:
            user = videoUser.objects.get(username=username)
        except:
            return Response({"message": "username does not exist"}, status=status.HTTP_204_NO_CONTENT)
        
        if user.password != password:
            return Response({"message": "incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({"message": "login successful"}, status=status.HTTP_200_OK)

class signup(APIView):
    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]
        print("testing1")
        if videoUser.objects.filter(username=username).exists():
            print(videoUser.objects.filter(username=username).exists())
            return Response({"message": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        print("testing2")
        user = videoUser.objects.createUser(username=username, password=password)
        token = Token.objects.get_or_create(user=user)
        print(token.key)
        return Response({"message": "user created successfully"}, status=status.HTTP_201_CREATED)
