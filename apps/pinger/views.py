from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pinger.models import Network
from apps.pinger.serializers import NetworkRequestSerializer, NetworkResponseSerializer
from apps.pinger.services import get_network_list, get_ping_list
from apps.pinger.tasks import ping_task


class Pinger(APIView):
    def post(self, request):
        serializer = NetworkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        ping_task.delay(
            network_id=data.id, ip_address=data.ip_address, subnet_mask=data.subnet_mask
        )
        return Response(
            data=NetworkResponseSerializer(data).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, network_id: int | None = None):
        if network_id:
            return get_ping_list(request=request, network_id=network_id)
        return get_network_list(request=request)

    def delete(self, request, network_id: int):
        try:
            Network.objects.get(id=network_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Network.DoesNotExist:
            raise NotFound("Network Not Found.")
