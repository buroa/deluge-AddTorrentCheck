#
# core.py
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
#    The Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor
#    Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

import time
import logging
from twisted.internet.task import LoopingCall

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.ui.client import client

DEFAULT_PREFS = {
    "test":"NiNiNi"
}

class Core(CorePluginBase):

    timer = {}

    def update_tracker(self, torrent_id):
        tid = component.get('TorrentManager').torrents[torrent_id]
        tid_status = tid.get_status(['tracker_status','time_added'])
        log.info("[AddTrackerCheck](%s)(%s) : %s", torrent_id, time.time() - tid_status['time_added'], tid_status['tracker_status'])

        if tid_status['tracker_status'].find("Announce OK") != -1:
            Core.timer[torrent_id].stop();
        elif time.time() - tid_status['time_added'] > 300:
            Core.timer[torrent_id].stop();
        else:
            log.info("[AddTrackerCheck](%s) : Updating Tracker", torrent_id)
            tid.force_reannounce();
         
    def post_torrent_add(self, torrent_id, *from_state):
        if component.get('TorrentManager').get_state() != 'Started':
            return
        log.info("[AddTrackerCheck](%s) : Adding New Torrent", torrent_id)
        Core.timer[torrent_id] = LoopingCall(self.update_tracker, torrent_id)
        Core.timer[torrent_id].start(5, now=False)

    def enable(self):
        # Go through the commands list and register event handlers
        component.get("EventManager").register_event_handler("TorrentAddedEvent", self.post_torrent_add)

    def disable(self):
        pass

    def update(self):
        pass
