from django.conf import settings
from django.core.cache import cache
from multiping import MultiPing
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.pinger.enums import PingStatus
from apps.pinger.models import Network, Ping
from apps.pinger.serializers import (
    NetworkQueryParamSerializer,
    NetworkResponseSerializer,
    PingSerializer,
)


def get_network_list(request) -> Response:
    serializer = NetworkQueryParamSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    paginator = PageNumberPagination()
    paginator.page_size = serializer.validated_data.get("page_size")
    networks = Network.objects.all().order_by(serializer.validated_data.get("sort"))
    page = paginator.paginate_queryset(networks, request)
    serializer = NetworkResponseSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


def get_ping_list(request, network_id: int) -> Response:
    try:
        network = Network.objects.get(id=network_id)
    except Network.DoesNotExist:
        raise NotFound("Network Not Found.")
    network_data = NetworkResponseSerializer(network).data
    if cache_data := cache.get(network_id):
        network_data["ping_count"] = len(cache_data)
        network_data["ping_list"] = cache_data
    else:
        pings = network.ping_set.all().order_by("checked_at")
        network_data["ping_count"] = pings.count()
        network_data["ping_list"] = PingSerializer(pings, many=True).data
    return Response(network_data)


def ping_ip_list(ip_list: list) -> tuple:
    mp = MultiPing(ip_list)
    mp.send()
    actives, inactives = mp.receive(settings.PING_RESPONSE_TIMEOUT_SEC)
    return list(actives.keys()), inactives


def ping_and_save(ip_list: list, network: Network):
    batch_to_save = []
    actives, inactives = ping_ip_list(ip_list)
    for ip in actives:
        ping = Ping(network=network, subnet_ip=ip, status=PingStatus.ACTIVE)
        batch_to_save.append(ping)
    for ip in inactives:
        ping = Ping(network=network, subnet_ip=ip, status=PingStatus.INACTIVE)
        batch_to_save.append(ping)
    pings = Ping.objects.bulk_create(batch_to_save)
    ping_list = PingSerializer(pings, many=True).data
    if cache_data := cache.get(network.id):
        cache.set(network.id, cache_data + ping_list)
    else:
        cache.set(network.id, ping_list)
