"""
Support for Lutron lights.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.lutron/
"""
import logging

from homeassistant.components.lutron import (
    LutronDevice, LUTRON_DEVICES, LUTRON_CONTROLLER)
from homeassistant.const import STATE_UNKNOWN
from homeassistant.components.binary_sensor import BinarySensorDevice

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['lutron']

EVENT_NAME = "lutron_occupancy"

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Lutron lights."""
    devs = []
    for (area_name, sensor) in hass.data[LUTRON_DEVICES]['binary_sensor']:
        dev = LutronMotionSensor(area_name, sensor, hass.data[LUTRON_CONTROLLER])
        devs.append(dev)

    add_devices(devs, True)
    return True


class LutronMotionSensor(LutronDevice, BinarySensorDevice):
    """Representation of a Lutron motion sensor."""

    @property
    def device_class(self):
        return 'occupancy'

    @property
    def is_on(self):
        """Return true if space if occupied."""
        return bool(self._lutron_device.state)
        
    def _update_callback(self, _device):
        """Run when invoked by pylutron when the device state changes."""
        super(LutronMotionSensor, self)._update_callback(_device)
        
        # Some types of Lutron motion sensors only notify vacancy, not
        # occupancy. As a result their HA "state" never changes since
        # we only ever see falling egdes. This means that we also need
        # to send events since users can't use state change triggers
        # for automations.

        self._hass.bus.fire(EVENT_NAME, {
            "area": self._area_name,
            "sensor": self._lutron_device._name,
            "state": "occupied" if self._lutron_device.state else "vacant"})
        
