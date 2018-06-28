"""
Support for Petpointer - A Swissmade Pet-Tracker

For more details about this platform, please refer to the documentation
TODO
"""

"""
javascript: 
var t=document.documentElement.innerHTML;var r=new RegExp(/inc\/pp-get-positions\.php\?lang=de&key=([^&]+)&sec=([^&]+)&id=([^&]+)/);var m=r.exec(t);console.log('key: '+m[1]+'\nsec: '+m[2]);
"""

import datetime
import voluptuous as vol
import logging
import requests
from datetime import timedelta

from homeassistant.helpers.event import track_time_interval
from homeassistant.components.device_tracker import PLATFORM_SCHEMA, SOURCE_TYPE_GPS
from homeassistant.const import ATTR_ID
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType


_LOGGER = logging.getLogger(__name__)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=15)

CONF_NAME = 'name'
CONF_KEY = 'key'
CONF_SEC = 'sec'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_KEY): cv.string,
    vol.Required(CONF_SEC): cv.string
})

ATTR_LAST_SEEN = 'last_seen'
ATTR_INTERVAL = 'interval'

def setup_scanner(hass, config: ConfigType, see, discovery_info=None):
    scanner = PetpointerScanner(hass, config, see)
    return scanner.success_init

class PetpointerScanner(object):
    
    def __init__(self, hass, config: ConfigType, see):
        self.name = config[CONF_NAME]
        self.key = config[CONF_KEY]
        self.sec = config[CONF_SEC]
        self.see = see

        self._update_info()
        track_time_interval(hass, self._update_info, MIN_TIME_BETWEEN_SCANS)
        self.success_init = True

        _LOGGER.info('Scanner initialized')

    @Throttle(MIN_TIME_BETWEEN_SCANS)
    def _update_info(self, now=None):
        position = self.get_petpointer_position(self.key, self.sec)
        detail = self.get_petpointer_details(self.key, self.sec)

        attrs = {
          ATTR_ID: self.sec,
          ATTR_LAST_SEEN: datetime.datetime.fromtimestamp(position['properties']['marker_ts']),
          ATTR_INTERVAL: detail['trackerintervalid']
        }

        self.see(
            dev_id=self.name,
            gps=[position['geometry']['coordinates'][1], position['geometry']['coordinates'][0]],
            gps_accuracy=position['properties']['circle_radius'],
            source_type=SOURCE_TYPE_GPS,
            battery=detail['battery'],
            attributes=attrs,
        )

        return True

    def get_petpointer_position(self, key, sec, **kwargs):
        url = 'https://www.petpointer.ch/inc/pp-get-positions.php?key={}&sec={}&limit=1'
        url = url.format(key, sec)

        try:
            res = requests.get(url, timeout=5, **kwargs)
        except requests.exceptions.Timeout:
            _LOGGER.exception(
                "Connection to the api timed out at URL %s", url)
            return

        if res.status_code != 200:
            _LOGGER.exception(
                "Connection failed with http code %s", res.status_code)
            return

        try:
            result = res.json()
            return result['features'][0]
        except ValueError:
            _LOGGER.exception("Failed to parse response from petpointer")
            return

    def get_petpointer_details(self, key, sec, **kwargs):
        url = 'https://www.petpointer.ch/inc/pp-get-details.php'

        try:
            payload = {'key': key, 'sec': sec}
            res = requests.post(url, data=payload, timeout=5, **kwargs)
        except requests.exceptions.Timeout:
            _LOGGER.exception(
                "Connection to the api timed out at URL %s", url)
            return
        
        if res.status_code != 200:
            _LOGGER.exception(
                "Connection failed with http code %s", res.status_code)
            return

        try:
            result = res.json()
            return result
        except ValueError:
            _LOGGER.exception("Failed to parse response from petpointer")
            return