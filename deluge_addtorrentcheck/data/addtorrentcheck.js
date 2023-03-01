/**
 * Script: addtorrentcheck.js
 *     The client-side javascript code for the AddTorrentCheck plugin.
 *
 * Copyright:
 *     (C) idiocrazy 2023 <yourname@example.com>
 *
 *     This file is part of AddTorrentCheck and is licensed under GNU GPL 3.0, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

AddTorrentCheckPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: 'AddTorrentCheck'
        }, config);
        AddTorrentCheckPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.AddTorrentCheckPage());
    }
});
new AddTorrentCheckPlugin();
