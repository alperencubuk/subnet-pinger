from django.db import models


class NetworkStatus(models.TextChoices):
    IN_QUEUE = "in queue"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PingStatus(models.TextChoices):
    ACTIVE = "active"
    INACTIVE = "inactive"


class IpVersion(models.IntegerChoices):
    IPv4 = 4
    IPv6 = 6


class NetworkSort(models.TextChoices):
    REQUESTED_AT = "requested_at"
    DESC_REQUESTED_AT = "-requested_at"
    STATUS = "status"
    DESC_STATUS = "-status"
