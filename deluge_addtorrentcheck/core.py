# -*- coding: utf-8 -*-
# Copyright (C) 2023 idiocrazy <yourname@example.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of AddTorrentCheck and is licensed under GNU GPL 3.0, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

import logging

import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.plugins.pluginbase import CorePluginBase
import time
import math
from twisted.internet.task import LoopingCall
import deluge.component as component

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    'delay': 15,
    'time': 300
}


class Core(CorePluginBase):

    timer = {}

    def update_tracker(self, torrent_id):
        torrent = component.get("TorrentManager").torrents[torrent_id]
        torrent_status = torrent.get_status(["tracker_status", "time_added"])
        torrent_total_time = time.time() - torrent_status["time_added"]

        if torrent_total_time > self.config["time"]:
            Core.timer[torrent_id].stop()
            return
        
        tracker_status = torrent_status["tracker_status"]
        log.info("[AddTrackerCheck](%s)(%s): %s", torrent_id, torrent_total_time, tracker_status)

        if "Announce OK" in tracker_status:
            peers = len(torrent.get_peers())
            progress = torrent.get_progress()

            if progress and peers >= 3:
                Core.timer[torrent_id].stop()
                return

            total_retries = math.floor(torrent_total_time / self.config["delay"])
            retries_per_half_minute = math.floor(30 / self.config["delay"])
            if total_retries % retries_per_half_minute == 0:
                log.info("[AddTrackerCheck](%s): Re-starting torrent", torrent_id)
                torrent.pause()
                time.sleep(1)
                torrent.resume()
                time.sleep(2)
        
        torrent.handle.force_reannounce(0, -1, 1)
        log.info("[AddTrackerCheck](%s): Re-announced trackers", torrent_id)
         
    def post_torrent_add(self, torrent_id, *from_state):
        if component.get('TorrentManager').get_state() != 'Started':
            return
        
        log.info("[AddTrackerCheck](%s): Adding New Torrent", torrent_id)
        Core.timer[torrent_id] = LoopingCall(self.update_tracker, torrent_id)
        Core.timer[torrent_id].start(self.config['delay'], now=False)

    def enable(self):
        self.config = deluge.configmanager.ConfigManager('addtorrentcheck.conf', DEFAULT_PREFS)
        self.config.save()
        component.get("EventManager").register_event_handler("TorrentAddedEvent", self.post_torrent_add)

    def disable(self):
        pass

    def update(self):
        pass

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config:
            if self.config[key] != config[key]:
                self.config[key] = config[key]
                self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
