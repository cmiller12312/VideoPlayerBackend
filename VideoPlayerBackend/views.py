from rest_framework.views import APIView
from rest_framework.response import *
from rest_framework import status
from models.models import videoUser, video, tag
from rest_framework import authtoken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
import os
import cv2
import json
import base64

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
            return Response({"message": "username does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if not check_password(password, user.password):
            return Response({"message": "Username or password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": f"{token.key}"
        }, status=status.HTTP_200_OK)

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
        user.pfp = None
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": f"{token.key}"
        }, status=status.HTTP_201_CREATED)

class uploadVideo(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print(user)
        print("Uploaded files:", request.FILES)
        videosPath = os.path.abspath(os.path.join(".", "videos"))
        try:
            os.mkdir(os.path.join(videosPath, user.username))
        except:
            pass
        videosPath = os.path.join(videosPath, user.username)

        file = request.FILES["video"]
        try:
            title = request.data["title"]
        except:
            return Response({"message": "missing title"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            description = request.data["description"]
        except:
            description = None
        temp = 0
        while True:
            if temp == 0:
                videoPath = os.path.join(videosPath, file.name)
            else:
                name, extension = str.split(file.name, ".")
                name = name + f"{temp}"
                newName = name + ".mp4"
                videoPath = os.path.join(videosPath, newName)
            if os.path.exists(videoPath):
                temp += 1
            else:
                break


        with open(videoPath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        data = cv2.VideoCapture(videoPath)
        frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = data.get(cv2.CAP_PROP_FPS)
        seconds = round(frames / fps)
        print(f"duration in seconds: {seconds}")


        createdVideo = video.objects.create(author=user, title=title, description=description, video=videoPath, videoLength=seconds)
        tags = json.loads(request.data["tags"])

        for tagName in tags:
            temp, created = tag.objects.get_or_create(tagName=tagName)
            temp.videos.add(createdVideo)

        request.user.videos.add(createdVideo)
        return Response({
            "message": "posted"
        }, status=status.HTTP_200_OK)

class userSettings(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = [v.title for v in request.user.videos.all()]
        pfp_data = None
        pfp_path = request.user.pfp
        if pfp_path and os.path.exists(pfp_path):
            with open(pfp_path, 'rb') as file:
                pfp_data = base64.b64encode(file.read()).decode('utf-8')
        return Response({
            "username": request.user.username,
            "followerCount": request.user.followCount,
            "videos": videos,
            "pfp": pfp_data, 
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            file = request.FILES["image"]
            user = request.user
            userFolder = os.path.join(os.path.abspath(os.path.join(".", "profilePictures")), user.username)
            os.makedirs(userFolder, exist_ok=True)  # This will create the folder if it doesn't exist

            filePath = os.path.join(userFolder, file.name)
            with open(filePath, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            print("Profile picture saved to:", filePath)
            user.pfp = filePath
            user.save()
        except Exception as e:
            print("Error saving profile picture:", e)
            return Response({"message": "error uploading image"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "ok"}, status=status.HTTP_202_ACCEPTED)
            
        


def getIP(request):
    forwardedFor = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwardedFor:
        ip = forwardedFor.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip