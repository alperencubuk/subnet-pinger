from django.conf import settings
from rest_framework import serializers

from apps.pinger.enums import NetworkSort
from apps.pinger.models import Network, Ping
from apps.pinger.utils import get_ip_version


class NetworkRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ("ip_address", "subnet_mask")

    def validate(self, data):
        version = get_ip_version(data["ip_address"])
        if not version:
            raise serializers.ValidationError(
                detail="Ip address should be valid Ipv4 or Ipv6 address."
            )
        subnet_min = {
            4: settings.IPV4_SUBNET_MIN_VALUE,
            6: settings.IPV6_SUBNET_MIN_VALUE,
        }
        subnet_max = {
            4: settings.IPV4_SUBNET_MAX_VALUE,
            6: settings.IPV6_SUBNET_MAX_VALUE,
        }
        if not subnet_max[version] <= data["subnet_mask"] <= subnet_min[version]:
            raise serializers.ValidationError(
                detail="Subnet mask should be between "
                f"{subnet_max[version]} and {subnet_min[version]} "
                f"for Ipv{version} addresses."
            )
        data["ip_version"] = version
        return data


class NetworkResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = "__all__"


class PingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ping
        fields = ("subnet_ip", "status", "checked_at")


class NetworkQueryParamSerializer(serializers.Serializer):
    page_size = serializers.IntegerField(
        required=False, default=50, min_value=1, max_value=1000
    )
    sort = serializers.ChoiceField(
        required=False,
        default=NetworkSort.DESC_REQUESTED_AT,
        choices=NetworkSort.choices,
    )
