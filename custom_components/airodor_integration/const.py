"""Constants for airodor_integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "airodor_integration"
ATTRIBUTION = "Data provided by Limodor Airodor WiFi"
CONF_IP_ADDRESS = "ip_address"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_GROUP_A_NAME = "group_a_name"
CONF_GROUP_B_NAME = "group_b_name"
CONF_DEVICE_NAME = "device_name"
CONF_AREA = "area"
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_GROUP_A_NAME = "Group A"
DEFAULT_GROUP_B_NAME = "Group B"
DEFAULT_DEVICE_NAME = "Airodor WiFi"
