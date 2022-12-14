/** @odoo-module */

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import framework from 'web.framework';
import session from 'web.session';
registry.category("ir.actions.report handlers").add("library_xlsx", async (action) => {
    if (action.report_type === 'library_xlsx') {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/library_xlsx_reports',
            data: action.data,
            success: def.resolve.bind(def),
//            error: (error) => this.call('crash_manager', 'rpc_error', error),
            complete: framework.unblockUI,
        });
        return def;
    }
});





















//odoo.define('library_management_system.action_manager', function (require) {
//"use strict";
//
///**
// * The purpose of this file is to add the actions of type
// * 'ir_actions_xlsx_download' to the ActionManager.
// */
//
//var ActionManager = require('web.ActionManager');
//var framework = require('web.framework');
//var session = require('web.session');
//
//ActionManager.include({
//
//    /**
//     * Executes actions of type 'ir.actions.library.xlsx_download'.
//     *
//     * @private
//     * @param {Object} action the description of the action to execute
//     * @returns {Deferred} resolved when the report has been downloaded ;
//     *   rejected if an error occurred during the report generation
//     */
//    _executeCashXlsxReportDownloadAction: function (action) {
//        framework.blockUI();
//        var def = $.Deferred();
//        session.get_file({
//            url: '/library_xlsx_reports',
//            data: action,
//            success: def.resolve.bind(def),
//            error: (error) => this.call('crash_manager', 'rpc_error', error),
//            complete: framework.unblockUI,
//        });
//        return def;
//    },
//    /**
//     * Overrides to handle the 'ir.actions.library.xlsx_download' actions.
//     *
//     * @override
//     * @private
//     */
//    _handleAction: function (action, options) {
//
//        if (action.type === 'ir.actions.library.xlsx_download') {
//            var state = this._super.apply(this, arguments);
//            action.output_format = 'xlsx'
//            return this._executeCashXlsxReportDownloadAction(action, options);
//        }
//        return this._super.apply(this, arguments);
//    },
//});
//
//});
