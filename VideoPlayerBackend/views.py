from rest_framework.views import APIView
from rest_framework.response import *
from rest_framework import status
from models.models import videoUser, video
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

        filler = os.path.join(os.path.dirname(__file__), "resources", "defaultUser.jpg")
        user.pfp = filler
        user.save()

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": f"{token.key}"
        }, status=status.HTTP_201_CREATED)

class uploadVideo(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        videosPath = os.path.abspath(os.path.join(".", "videos"))
        try:
            os.mkdir(os.path.join(videosPath, user.username))
        except:
            pass
        videosPath = os.path.join(videosPath, user.username)

        file = request.FILES["video"]
        try:
            title = request.data["title"]
            if video.objects.filter(author=request.user, title=title).exists():
                return Response({"message": "Already have a video titled that"}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(title) > 18:
                return Response({"message": "Title must be 18 characters or shorter"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "missing title"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            description = request.data["description"]
        except:
            description = None
        temp = 0
        videoPath = os.path.join(videosPath, (title + ".mp4"))


        with open(videoPath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        data = cv2.VideoCapture(videoPath)
        frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = data.get(cv2.CAP_PROP_FPS)
        seconds = round(frames / fps)
        print(f"duration in seconds: {seconds}")

        cover_b64 = request.data.get("cover")
        coverPath = None
        if cover_b64:
            cover_folder = os.path.abspath(os.path.join(".", "covers", user.username))
            os.makedirs(cover_folder, exist_ok=True)
            coverPath = os.path.join(cover_folder, f"{title}Cover.png")
            try:
                with open(coverPath, "wb") as f:
                    f.write(base64.b64decode(cover_b64))
            except Exception as e:
                print("Error saving cover image:", e)
                coverPath = None

        createdVideo = video.objects.create(
            author=user,
            title=title,
            description=description,
            video=videoPath,
            videoLength=seconds,
            cover=coverPath
        )

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
            file = request.data.get("pfp")
            if file != None:
                oldPath = request.user.pfp
                if oldPath and os.path.exists(oldPath) and oldPath != os.path.join(os.path.dirname(__file__), "resources", "defaultUser.jpg"):
                    try:
                        os.remove(oldPath)
                        print("Old profile picture deleted:", oldPath)
                    except Exception as delete_err:
                        print("Failed to delete old profile picture:", delete_err)
                userFolder = os.path.join(os.path.abspath(os.path.join(".", "profilePictures")), request.user.username)
                os.makedirs(userFolder, exist_ok=True)
                base64_string = file
                

                imageData = base64.b64decode(base64_string)
                with open(f"{userFolder}/{request.user.username}.png", "wb") as f:
                    f.write(imageData)
                print("Profile picture saved to:", f"{userFolder}/{request.user.username}.png")
                request.user.pfp = f"{userFolder}/{request.user.username}.png"
            request.user.save()
        except Exception as e:
            print("Error saving profile picture:", e)
            return Response({"message": "error uploading image"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "ok"}, status=status.HTTP_202_ACCEPTED)
    

class getVideoBatch(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        result = []

        for followed in user.following.all():
            videos = followed.videos.all()
            for v in videos:
                result.append({
                    "username": followed.username,
                    "title": v.title
                })

        unfollowedVideos = video.objects.exclude(author__in=user.following.all()).order_by('-views')[:20]
        for v in unfollowedVideos:
            result.append({
                "username": v.author.username,
                "title": v.title,
            })

        return Response({
            "Titles": result,
            "Unfollowed": result
        }, status=status.HTTP_200_OK)

class followSettings(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        username = request.data["username"]
        try:
            for i in user.following.all():
                if i.username == username:
                    return Response({"message":"already follwing user"}, status=status.HTTP_400_BAD_REQUEST)
            userToFollow = videoUser.objects.get(username=username)
            request.user.following.add(userToFollow)
            userToFollow.followCount += 1
            userToFollow.save()
            user.save()
            return Response({"message": f"followed {username}"}, status=status.HTTP_202_ACCEPTED)
        except videoUser.DoesNotExist:
            return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        
class getVideo(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        title = request.data.get("title")
        if not username or not title:
            return Response({"message": "username and title required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = videoUser.objects.get(username=username)
            vid = video.objects.get(author=user, title=title)
            try:
                with open(vid.cover, 'rb') as file:
                    thumbnail = base64.b64encode(file.read()).decode('utf-8')
            except:
                filler_path = os.path.join(os.path.dirname(__file__), "resources", "FillerCover.jpg")
                with open(filler_path, 'rb') as file:
                    thumbnail = base64.b64encode(file.read()).decode('utf-8')

            if user.pfp and os.path.exists(user.pfp):
                with open(user.pfp, 'rb') as file:
                    pfp = base64.b64encode(file.read()).decode('utf-8')
            else:
                pfp = None

        except videoUser.DoesNotExist:
            return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        except video.DoesNotExist:
            return Response({"message": "video not found"}, status=status.HTTP_404_NOT_FOUND)

        vid.views += 1
        vid.save()
        return Response({
            "username": user.username,
            "title": vid.title,
            "thumbnail": thumbnail,
            "videoLength": vid.videoLength,
            "userPfp": pfp,
            "description": vid.description,
            "views": vid.views,
            "date": vid.date,
        }, status=status.HTTP_200_OK)