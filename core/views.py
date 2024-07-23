from .serializers import IdeaSerializer
from .models import Idea
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .serializers import UserSerializer, IdeaSerializer, LoginSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser as User,  Idea
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets
from mistralai.models.chat_completion import ChatMessage
from mistralai.client import MistralClient
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import environ
env = environ.Env()
environ.Env.read_env()
# Create your views here.


class ContentGeneration(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        # serializer = IdeaSerializer(data=request.data)
        # if serializer.is_valid():
        details = request.data.get('details')
        target_audience = request.data.get('target_audience')
        print(f'{details} and {target_audience}')
        user = request.user

        if not details and target_audience:
            return Response({'error': 'Business description and targe audience should be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_generated = generate_content(details, target_audience)

            idea = Idea.objects.create(
                details=details, target_audience=target_audience, content_generated=content_generated, creator=user)
            idea.save()

            return Response(content_generated, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_content(details: str, target_audience: str):

    api_key = env('MistralAPIKEY')
    model = "mistral-tiny"

    client = MistralClient(api_key=api_key)

    result = {}

    headline_message = [
        ChatMessage(
            role="user",
            content=f"Generate a headline for a business named that {details} and is targeted at {target_audience}, not more than 7 words"
        )
    ]

    subheadline_message = [
        ChatMessage(
            role="user",
            content=f"Generate a subheadline for the landing page of a business that {details} and is targeted at {target_audience}, not more than 15 words. No emoji!!!"
        )
    ]

    cta_message = [
        ChatMessage(
            role="user",
            content=f"Generate a CTA button copy for the landing page of a business that {details} and is targeted at {target_audience}. 4 words maximum, An example is 'Start your free trial'. No emoji!!!"
        )
    ]

    features_message = [
        ChatMessage(
            role="user",
            content=f"Generate a features section for the landing page of a business that {details} and is targeted at {target_audience}, start with a tagline for the section, a subheadline and then 3 features with 3 lines of explanation. No emoji!!!"
        )
    ]

    benefits_message = [
        ChatMessage(
            role="user",
            content=f"Generate a benefits section for the landing page of a business that {details} and is targeted at {target_audience}, start with a tagline for the section, a subheadline and then 3 benefit with 2 lines of explanation. No emoji!!!"
        )
    ]

    # offer_message = [
    #     ChatMessage(
    #         role="user",
    #         content=f"Generate a superb offer breakdown pitch for the landing page of a business that {details} and is targeted at {target_audience}. No emoji!!!"
    #     )
    # ]

    # urgency_message = [
    #     ChatMessage(
    #         role="user",
    #         content=f"Generate a message that creates urgency to visitors for the landing page of a business that {details} and is targeted at {target_audience}. No emoji!!!"
    #     )
    # ]

    faqs_message = [
        ChatMessage(
            role="user",
            content=f"Generate a FAQs section for the landing page of a business that {details} and is targeted at {target_audience}, 3 questions and answers. No emoji!!"
        )
    ]

    sections = {
        'headline': headline_message,
        'subheadline': subheadline_message,
        'cta': cta_message,
        'features': features_message,
        'benefits': benefits_message,
        # 'offer': offer_message,
        # 'urgency': urgency_message,
        'faqs': faqs_message,

    }

    result = {}

    for key, message in sections.items():
        chat_response = client.chat(
            model=model,
            messages=message,
        )

        result[key] = chat_response.choices[0].message.content

    return result


class CreateUserView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.select_related().all()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():  
            email = request.data.get('email')
            password = request.data.get('password')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'detail': 'User already exists!'}, status=status.HTTP_400_BAD_REQUEST)

            if not password:
                return JsonResponse({'detail': 'Password not provided!'}, status=status.HTTP_400_BAD_REQUEST)

            # If validation passes, create the user
            user = User.objects.create_user(
                password=password, email=email)
            user.is_active = True
            user.save()

            # Return the created user's data
            return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
        else:
            # If the serializer is not valid, return the errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    serializer_class = LoginSerializer
    queryset = User.objects.select_related().all()
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():  # Correctly call the method here
            email = request.data.get('email')
            password = request.data.get('password')

            if not User.objects.filter(email=email).exists():
                return JsonResponse({'detail': 'User does not exists!'}, status=status.HTTP_400_BAD_REQUEST)

            if not password:
                return JsonResponse({'detail': 'Password not provided!'}, status=status.HTTP_400_BAD_REQUEST)

            user = auth.authenticate(request, email=email, password=password)

            if user is not None:
                auth.login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                response_data = UserSerializer(user).data
                response_data['access_token'] = access_token
                response_data['refresh_token'] = str(refresh)
                print(response_data)
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'detail': 'Invalid credentials!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If the serializer is not valid, return the errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth.logout(request)
            return Response({'detail': 'User logged out successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No user is logged in!'}, status=status.HTTP_400_BAD_REQUEST)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            user = request.user
            print(user)

            ideas = Idea.objects.filter(creator=user)
            serializer = IdeaSerializer(ideas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Idea.DoesNotExist:
            return Response({'detail': 'Content not found.'}, status=status.HTTP_404_NOT_FOUND)



class ContentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, idea_id):
        try:
            user = request.user
            idea = Idea.objects.get(creator=user, id=idea_id)
            data = {
                'details': idea.details,
                'target_audience': idea.target_audience,
                'generatedData': idea.content_generated
                # Add more fields as needed
            }
            return Response(data, status=status.HTTP_200_OK)
        except Idea.DoesNotExist:
            return Response({'detail': 'Content not found.'}, status=status.HTTP_404_NOT_FOUND)


class IdeaViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Idea ViewSet"""

    serializer_class = IdeaSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"

    def get_queryset(self, request):
        user = self.request.user
        user_id = request.headers.get('User-ID')

        return Idea.objects.get(creator=user, id=user_id)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Idea.DoesNotExist:
            return Response({'detail': 'Content not found.'}, status=status.HTTP_404_NOT_FOUND)



