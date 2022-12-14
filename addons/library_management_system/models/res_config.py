# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    return_in_days = fields.Integer(string="Return in")
    daily_due_amount = fields.Integer(string="Daily due")
    auto_calc_return = fields.Boolean(string="Automatic return date")
    member_id_prefix = fields.Char(string="Prefix",
                                   help="Prefix fro generating member id")
    member_id_suffix = fields.Char(string="Suffix",
                                   help="Suffix for generating member id")

    due_journal_type = fields.Many2one('account.journal',
                                       string="Due Journal", required=True)

    membership_journal_type = fields.Many2one('account.journal',
                                              string="Membership Journal",
                                              required=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        return_in_days = params.get_param('return_in_days')
        auto_calc_return = params.get_param('auto_calc_return', default=False)
        daily_due_amount = params.get_param('daily_due_amount', default=0)
        member_id_prefix = params.get_param('member_id_prefix', default=False)
        member_id_suffix = params.get_param('member_id_suffix', default=False)
        due_journal_type = params.get_param('due_journal_type', default=False)
        membership_journal_type = params.get_param('membership_journal_type',
                                                   default=False)
        res.update(
            return_in_days=int(return_in_days),
            auto_calc_return=auto_calc_return,
            member_id_prefix=member_id_prefix,
            member_id_suffix=member_id_suffix,
            daily_due_amount=int(daily_due_amount),
            due_journal_type=int(due_journal_type),
            membership_journal_type=int(membership_journal_type),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_sequence = self.env["ir.sequence"].search(
            [('code', '=', 'res.partner.member')])
        ir_sequence.update({'prefix': self.member_id_prefix,
                            'suffix': self.member_id_suffix})
        self.env['ir.config_parameter'].sudo(). \
            set_param("return_in_days", int(self.return_in_days))
        self.env['ir.config_parameter'].sudo(). \
            set_param("daily_due_amount", int(self.daily_due_amount))
        self.env['ir.config_parameter'].sudo().set_param("auto_calc_return",
                                                         self.auto_calc_return)
        self.env['ir.config_parameter'].sudo().set_param("member_id_prefix",
                                                         self.member_id_prefix)
        self.env['ir.config_parameter'].sudo().set_param("member_id_suffix",
                                                         self.member_id_suffix)

        self.env['ir.config_parameter'].sudo().set_param("due_journal_type",
                                                         self.due_journal_type.id)

        self.env['ir.config_parameter'].sudo().set_param(
            "membership_journal_type",
            self.membership_journal_type.id)
