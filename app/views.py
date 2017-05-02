import rest_framework.status  as status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.validators import ValidationError

try:
    from urllib import quote_plus  # python 2
except:
    pass

try:
    from urllib.parse import quote_plus  # python 3
except:
    pass

from django.shortcuts import render
from rest_framework.decorators import *

from .models import *

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from serializers import UserSerializer, AccountSerializer, TransactionSerializer, \
    AccountListSerialiser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class AccountListViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = AccountListSerialiser


class AccountViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = [IsAuthenticated, ]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_acc = Account(currency=request.data.get("currency"), user=request.user)
            new_acc.save()
            r = {
                'error': False,
                'data': {"accountId": new_acc.number}
            }
            return Response(r, status=status.HTTP_201_CREATED)
        except Exception, e:
            r = {
                'error': True,
                'message': e.message
            }
            return Response(r, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Account.objects.all()
        user = self.request.user
        if user is not None:
            queryset = queryset.filter(user=user)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    renderer_classes = (JSONRenderer,)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = self.transfer(serializer.validated_data.get("source"),
                                     serializer.validated_data.get("destination"),
                                     serializer.validated_data.get("total"),
                                     description=serializer.validated_data.get("comment"))

            headers = self.get_success_headers(serializer.validated_data)
            r = {
                'error': False,
                'data': {
                    'TransactionId': instance.id
                }
            }
            st = status.HTTP_201_CREATED
        except ValidationError, e:
            r = {
                'error': True,
                'message': str(e.detail)
            }
            st = status.HTTP_400_BAD_REQUEST
        except Exception, e:
            r = {
                'error': True,
                'message': e.message
            }
            st = status.HTTP_400_BAD_REQUEST
        finally:
            return Response(r, status=st)

    def perform_create(self, serializer):
        return serializer.save()

    def transfer(self, source, destination, amount,
                 description=None):

        if source is None:
            msg = "Transfer of %.2f to account #%d".format(
                    amount, destination.id)
        elif destination is None:
            msg = "Transfer of %.2f from account #%d ".format(amount, source.id)
        else:
            msg = "Transfer of %.2f from account #%d to account #%d".format(amount, source.id, destination.id)

        if description:
            msg += " '%s'" % description
        try:
            transfer = Transaction.objects.create(
                    source, destination, amount, description)
        except Exception, e:
            raise
        else:
            return transfer


class ExampleView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        from rest_framework.authtoken.models import Token
        # from rest_framework.authentication import
        token = Token.objects.get_or_create(user=request.user)

        content = {
            'user': unicode(request.user),
            'auth': unicode(request.auth),
            'token': unicode(token.key)
        }
        return Response(content)
