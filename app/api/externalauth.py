from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework import exceptions, permissions, parsers
from rest_framework.response import Response
from app.auth.backends import get_user_from_external_auth_response
import requests
from webodm import settings

class ExternalTokenAuth(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (parsers.JSONParser, parsers.FormParser,)

    def post(self, request):
        # This should never happen
        if settings.EXTERNAL_AUTH_ENDPOINT == '':
            return Response({'error': 'EXTERNAL_AUTH_ENDPOINT not set'})

        token = request.COOKIES.get('external_access_token', '')
        if token == '':
            return Response({'error': 'external_access_token cookie not set'})

        try:
            r = requests.post(settings.EXTERNAL_AUTH_ENDPOINT, headers={
                'Authorization': "Bearer %s" % token 
            })
            res = r.json()
            if res.get('user_id') is not None:
                user = get_user_from_external_auth_response(res)
                if user is not None:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return Response({'redirect': '/'})
                else:
                    return Response({'error': 'Invalid credentials'})
            else:
                return Response({'error': res.get('message', 'Invalid external server response')})
        except Exception as e:
            return Response({'error': str(e)})

# TODO: move to simple http server
# class TestExternalAuth(APIView):
#     permission_classes = (permissions.AllowAny,)
#     parser_classes = (parsers.JSONParser, parsers.FormParser,)

#     def post(self, request):
#         print("YO!!!")
#         if settings.EXTERNAL_AUTH_ENDPOINT == '':
#             return Response({'message': 'Disabled'})

#         username = request.data.get("username")
#         password = request.data.get("password")

#         print("HERE", username)

#         if username == "extuser1" and password == "test1234":
#             return Response({
#                 'user_id': 100,
#                 'username': 'extuser1',
#                 'maxQuota': 500,
#                 'token': 'test',
#                 'node': {
#                     'hostname': 'localhost',
#                     'port': 4444
#                 }
#             })
#         else:
#             return Response({'message': "Invalid credentials"})