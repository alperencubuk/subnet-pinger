import ipaddress
import logging

from celery import shared_task
from django.conf import settings

from apps.pinger.models import Network, NetworkStatus
from apps.pinger.services import ping_and_save
from apps.pinger.utils import get_ip_version

logger = logging.getLogger(__name__)


@shared_task
def ping_task(network_id: int, ip_address: str, subnet_mask: int) -> None:
    network = Network.objects.get(id=network_id)
    network.status = NetworkStatus.IN_PROGRESS
    network.save()
    try:
        subnet: ipaddress.IPv4Network | ipaddress.IPv6Network
        if get_ip_version(ip_address) == 4:
            subnet = ipaddress.IPv4Network(
                address=f"{ip_address}/{subnet_mask}", strict=False
            )
        else:
            subnet = ipaddress.IPv6Network(
                address=f"{ip_address}/{subnet_mask}", strict=False
            )
        batch: list = []
        for host in subnet.hosts():
            if len(batch) < settings.SAVE_PER_PING_REQUEST:
                batch.append(str(host))
            else:
                ping_and_save(ip_list=batch, network=network)
                batch = []
        if batch:
            ping_and_save(ip_list=batch, network=network)
        network.status = NetworkStatus.COMPLETED
        network.save()
    except Exception as error:
        logger.error(
            f"[ERROR] [PING TASK] [Network: {network_id}]\nDetail: {error}",
        )
        network.status = NetworkStatus.FAILED
        network.save()
