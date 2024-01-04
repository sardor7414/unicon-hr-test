from rest_framework.views import APIView
from rest_framework.response import Response
from user.models import User
from .serializers import UserRegisterSerializer
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.authtoken.models import Token


# Create your views here.
class UserRegisterAPI(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserLoginAPI(APIView):

    def post(self, request):
        data = request.data
        password = data.get('password')
        phone = data.get('phone')
        if not password or not phone:
            return Response({
                'error': 'Password or phone number not given'
            }, status=HTTP_400_BAD_REQUEST)
        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({
                'error': 'User not found'
            }, status=HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({
                'error': 'Password not match'
            }, status=HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key
        })
