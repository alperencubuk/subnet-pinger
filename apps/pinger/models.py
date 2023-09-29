from django.db import models

from apps.pinger.enums import IpVersion, NetworkStatus, PingStatus


class Network(models.Model):
    ip_address = models.CharField(max_length=40)
    subnet_mask = models.IntegerField()
    status = models.CharField(
        max_length=20, choices=NetworkStatus.choices, default=NetworkStatus.IN_QUEUE
    )
    ip_version = models.IntegerField(choices=IpVersion.choices)
    requested_at = models.DateTimeField(db_index=True, auto_now_add=True)


class Ping(models.Model):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    subnet_ip = models.CharField(max_length=40)
    status = models.CharField(max_length=20, choices=PingStatus.choices)
    checked_at = models.DateTimeField(db_index=True, auto_now=True)
