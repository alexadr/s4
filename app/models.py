from __future__ import unicode_literals

import json
import uuid
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import transaction
from django.db.models.signals import pre_save

HTTP_API_FIXER_IO_LATEST = 'http://api.fixer.io/latest'


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    number = models.UUIDField(max_length=120, null=True)

    CURRENCIES_TYPES = {
        'RUB': 'RUB',
        'EUR': 'EUR',
        'GBP': 'GBP',
        'CHF': 'CHF',
        'USD': 'USD'
    }

    CURRENCIES_TYPE_CHOICES = [
        (CURRENCIES_TYPES['RUB'], 'RUB'),
        (CURRENCIES_TYPES['EUR'], 'EUR'),
        (CURRENCIES_TYPES['GBP'], 'GBP'),
        (CURRENCIES_TYPES['CHF'], 'CHF'),
        (CURRENCIES_TYPES['USD'], 'USD'),

    ]

    currency = models.CharField(
            max_length=3,
            choices=CURRENCIES_TYPE_CHOICES,
            verbose_name='currency',
    )

    total_amount = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0,
            verbose_name='Total amount',
    )

    CURRENCIES = [
        'USD', 'EUR', 'GBP', 'CHF', 'RUB'
    ]

    def __unicode__(self):
        return unicode(self.number)

    def __str__(self):
        return unicode(self.number)

    class Meta:
        pass

    def change_balance(self, operation, amount):

        if (operation == "W"):
            self.total_amount -= amount
        else:
            self.total_amount += amount

    def save(self, *args, **kwargs):

        return super(Account, self).save(*args, **kwargs)

    def is_debit_permitted(self, amount):
        return amount <= self.total_amount


class TransactionManager(models.Manager):
    def create(self, source, destination, amount, description=None):

        self.verify_transfer(source, amount)
        with transaction.atomic():
            transfer = self.get_queryset().create(
                    source=source,
                    destination=destination,
                    total=amount,
                    comment=description)
            sounce_amount, destination_amount = self.check_exchange(source, destination, amount)

            if source is not None:
                source.change_balance(operation="W", amount=sounce_amount)
                source.save()
            if destination is not None:
                destination.change_balance(operation="D", amount=destination_amount)
                destination.save()
            return self._wrap(transfer)

    def check_exchange(self, source, destination, amount):
        amount_source = amount
        amount_destination = amount
        import requests
        if source is not None and destination is not None:
            if source.currency != destination.currency:
                url = HTTP_API_FIXER_IO_LATEST
                data = {"symbols": destination.currency, "base": source.currency}
                serialized_data = requests.get(url, params=data)
                data = json.loads(serialized_data.text)

                amount_source = amount
                amount_destination = amount * Decimal(data["rates"][destination.currency])

        return amount_source, amount_destination

    def _wrap(self, obj):
        return obj

    def verify_transfer(self, source, amount):

        if amount <= 0:
            raise Exception("Debits must use a positive amount")

        if source is not None and not source.is_debit_permitted(amount):
            msg = "Unable to debit {0} from account {1}:"
            raise Exception(
                    msg.format(amount, source.number))


class Transaction(models.Model):
    TRANSACTION_TYPES = {
        'withdrawal': 'w',
        'deposit': 'd',
    }

    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPES['withdrawal'], 'withdrawal'),
        (TRANSACTION_TYPES['deposit'], 'deposit'),
    ]

    transaction_type = models.CharField(
            max_length=1,
            choices=TRANSACTION_TYPE_CHOICES,
            verbose_name='Transaction type',
    )
    source = models.ForeignKey(Account, related_name='outcome_transfers', verbose_name="SourceAccount", null=True)
    destination = models.ForeignKey(Account, related_name='income_transfers', verbose_name="DestinationAccount",
                                    null=True)
    when = models.DateTimeField(verbose_name="Time")
    total = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Summ")
    comment = models.CharField(max_length=255, verbose_name="Comment")
    state = models.BooleanField()

    objects = TransactionManager()


def pre_save_account_receiver(sender, instance, *args, **kwargs):
    if not instance.number:
        instance.number = (uuid.uuid4())


def pre_save_transaction_receiver(sender, instance, *args, **kwargs):
    if not instance.when:
        instance.when = datetime.now()

    if instance.source:
        if instance.source.total_amount - instance.total > 0:
            instance.state = True
        else:
            instance.state = False
    else:
        instance.state = True


pre_save.connect(pre_save_account_receiver, sender=Account)
pre_save.connect(pre_save_transaction_receiver, sender=Transaction)
