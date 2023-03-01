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
from twisted.internet.task import LoopingCall
import deluge.component as component

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    'delay': 5,
    'time': 300
}


class Core(CorePluginBase):

    timer = {}

    def update_tracker(self, torrent_id):
        tid = component.get('TorrentManager').torrents[torrent_id]
        tid_status = tid.get_status(['tracker_status','time_added'])
        log.info("[AddTrackerCheck](%s)(%s) : %s", torrent_id, time.time() - tid_status['time_added'], tid_status['tracker_status'])

        if tid_status['tracker_status'].find("Announce OK") != -1:
            Core.timer[torrent_id].stop();
        elif time.time() - tid_status['time_added'] > self.config['time']:
            Core.timer[torrent_id].stop();
        else:
            log.info("[AddTrackerCheck](%s) : Updating Tracker", torrent_id)
            tid.force_reannounce();
         
    def post_torrent_add(self, torrent_id, *from_state):
        if component.get('TorrentManager').get_state() != 'Started':
            return
        log.info("[AddTrackerCheck](%s) : Adding New Torrent", torrent_id)
        Core.timer[torrent_id] = LoopingCall(self.update_tracker, torrent_id)
        Core.timer[torrent_id].start(self.config['delay'], now=False)

    def enable(self):
        self.config = deluge.configmanager.ConfigManager(
            'addtorrentcheck.conf', DEFAULT_PREFS)
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
