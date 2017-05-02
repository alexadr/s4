from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from models import Account, Transaction


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class PrimaryKeyRelatedFieldByNumber(PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            return self.get_queryset().get(number=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class TransactionSerializer(serializers.ModelSerializer):
    # my_field = serializers.SerializerMethodField('is_named_bar')
    #
    # def is_named_bar(self, foo):
    #   return foo.name == "bar"
    # destination = serializers.Se


    source = PrimaryKeyRelatedFieldByNumber(label='SourceAccount', queryset=Account.objects.all(), required=False)
    destination = PrimaryKeyRelatedFieldByNumber(label='DestinationAccount', queryset=Account.objects.all(),
                                                 required=False)

    class Meta:
        model = Transaction
        # depth = 1
        fields = ('source', 'destination', 'comment', 'total')

    def validate(self, attrs):
        try:
            if (attrs.get("source") is None and attrs.get("destination") is None):
                raise serializers.ValidationError('source or destination need to be exists')
        except Exception:
            raise serializers.ValidationError('source or destination need to be exists')

        return attrs


class AccountListSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('number', 'currency')


class AccountSerializer(serializers.ModelSerializer):
    transfers = serializers.SerializerMethodField('is_named_bar')

    def is_named_bar(self, foo):
        income_transfers = list(foo.income_transfers.all())
        outcome_transfers = list(foo.outcome_transfers.all())

        l = []
        l.extend(income_transfers)
        l.extend(outcome_transfers)
        new = []
        for u in l:
            if u.source is None:
                new.append({
                    "type": "External",
                    "acc": u.destination.number,
                    "comment": u.comment,
                    "amount": u.total,
                    "date": u.when,
                    "status": u.state
                })
            elif u.destination is None:
                new.append({
                    "type": "Withdraw",
                    "acc": u.source.number,
                    "comment": u.comment,
                    "amount": u.total,
                    "date": u.when,
                    "status": u.state
                })
            elif u.source.number == foo.number:
                new.append({
                    "type": "W",
                    "acc": u.destination.number,
                    "comment": u.comment,
                    "amount": u.total,
                    "date": u.when,
                    "status": u.state
                })
            elif u.destination.number == foo.number:
                new.append({
                    "type": "D",
                    "acc": u.source.number,
                    "comment": u.comment,
                    "amount": u.total,
                    "date": u.when,
                    "status": u.state
                })
        new = sorted(new, key=lambda k: k['date'])
        return new

    class Meta:
        model = Account
        fields = ('number', 'currency', 'id', 'total_amount', 'transfers')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


# class UserLoginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'username',
#             'email',
#             'password',
#             # 'token',
#
#         ]
#         extra_kwargs = {"password":
#                             {"write_only": True}
#                         }
#
#     def validate(self, data):
#         username = data['username']
#         password = data['password']
#         user_a = User.objects.filter(username__iexact=username)
#         user_b = User.objects.filter(email__iexact=username)
#         user_qs = (user_a | user_b).distinct()
#         if user_qs.exists() and user_qs.count() == 1:
#             user_obj = user_qs.first()  # User.objects.get(id=1)
#             password_passes = user_obj.check_password(password)
#             if not user_obj.is_active:
#                 raise ValidationError("This user is inactive")
#             # HTTPS
#             if password_passes:
#                 # token
#                 data['username'] = user_obj.username
#                 # data['email'] = user_obj.email
#                 data['token'] = token
#                 return data
#         raise ValidationError("Invalid credentials")
