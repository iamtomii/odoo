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

import logging
from datetime import date

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class LibraryMembers(models.Model):
    """ Extend res.partners for library management """

    _inherit = 'res.partner'

    sex = fields.Selection([('male', 'Male'),
                            ('female', 'Female'),
                            ('other', 'Other')], string="Gender")

    member_type = fields.Selection([('life_long', 'Life Long'),
                                    ('monthly', 'Monthly Renewal'),
                                    ('visitor', 'Visitor')],
                                   required=True, string="Member Type",
                                   track_visibility=True,
                                   help="Type of library membership")

    is_a_member = fields.Boolean(string="Library Member",
                                 help="User is a member of library")

    member_sequence = fields.Char(string="Member ID", default="New",
                                  copy=False)

    membership_expired = fields.Boolean(string="Membership Status",
                                        default=True, copy=False,
                                        track_visibility=True)
    membership_expiry_date = fields.Date(string="Membership Expiry Date",
                                         default=fields.Date.context_today,
                                         copy=False, track_visibility=True,
                                         help="Current membership expiry date")
    last_renewal_date = fields.Date(string="Last Renewal Date")

    membership_history = fields.One2many("membership.history",
                                         "library_member", readonly=True)

    book_history = fields.One2many("book.history",
                                   "member_book_history", readonly=True)
    due_amount_paid = fields.Integer("Due Amount", default=0)

    membership_type = fields.Many2one("membership.types", "Current Membership",
                                      help="Library Membership Type")
    book_count = fields.Integer(string="Currently holding Books",
                                help="No of books on hand")
    block_status = fields.Boolean(string="Block Status", default=False)
    created_company_id = fields.Many2one('res.company', 'Company',
                                         default=lambda self: self.env[
                                             'res.users'].browse(
                                             self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)

    @api.model
    def create(self, vals):
        try:
            vals['member_sequence'] = self.env['ir.sequence'].with_context(
                force_company=vals['company_id']).next_by_code(
                'res.partner.member') or _('New')
        except Exception as e:
            _logger.info("# company_id not found %s" % e)
            pass
        return super(LibraryMembers, self).create(vals)

    @api.onchange('is_a_member')
    @api.depends('is_a_member')
    def is_a_member_change(self):
        """ generate a member id when is a member is checked """
        if self.member_sequence == 'New' and self.is_a_member:
            company_id = self.company_id.id
            self.member_sequence = self.env['ir.sequence'].with_context(
                with_company=company_id).next_by_code(
                'res.partner.member') or _('New')

    def action_renew_membership_wizard(self):
        """ Function to call action to view renew membership wizard """
        ctx = {
            'default_member': self.id,
            'default_membership_type': self.membership_type.id,
        }
        return {
            'name': _('Renew Membership'),
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'renew.membership',
            'type': 'ir.actions.act_window',
            'edit': False,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def _cron_mark_expired_members(self):
        """ Mark expired members and send notification """
        member_list = self.env['res.partner'].search([('is_a_member', '=', True)])
        for member in member_list:
            if not member.membership_type.do_not_expire:

                if not member.membership_expired and \
                        member.membership_expiry_date <= date.today():
                    # send email to customer
                    context = member._context.copy()

                    template_id = self.env.ref(
                        'library_management_system.email_template_membership_expiry')
                    template_id.with_context(context).sudo().send_mail(
                        member.id,
                        force_send=True)
                    member.membership_expired = True

    def action_view_book(self):
        """ View book on hand  """
        reg_items = self.env['book.register'].search([])
        reg_ids = []
        for each in reg_items:
            if each.register_member.id == self.id:
                reg_ids.append(each.id)
        action = \
            self.env.ref('library_management_system.action_library_register').read()[
                0]
        if len(reg_ids) > 1:
            action['domain'] = [('id', 'in', reg_ids),
                                ('register_status', 'in',
                                 ('issued', 'expired'))]
        elif len(reg_ids) == 1:
            action['views'] = [
                (self.env.ref('library_management_system.register_form_view').id,
                 'form')]
            action['res_id'] = reg_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _get_late_members(self):
        """ Action late returning members """
        book_register = self.env['book.register'].search([])
        member_ids = []
        for reg in book_register:
            if reg.register_status == 'expired':
                member_ids.append(reg.register_member.id)
        value = {
            'domain': str([('id', 'in', member_ids)]),
            'view_mode': 'kanban,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'name': 'Late Members',
            'target': 'current',
            'create': False,
            'edit': False,
        }
        return value

    def action_block_member(self):
        """ Block members """
        self.block_status = True

    def action_unblock_member(self):
        """ Unblock members """
        self.block_status = False


class MembershipHistory(models.Model):
    """ Model for storing the membership renewal history """
    _name = "membership.history"
    _description = "Membership History"

    renewal_date = fields.Date(sting="Renewal Date")
    new_expiry_date = fields.Date(sting="Next Expiry")
    renewal_plan = fields.Many2one("membership.types", sting="Plan")
    renewal_invoice = fields.Many2one("account.move", "Invoice",
                                      required=True, default=False)
    library_member = fields.Many2one('res.partner', string="Member")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)


class IssuedBookHistory(models.Model):
    """ Model for storing issued book history """
    _name = "book.history"
    _description = "Issued Book History"

    register_reference = fields.Many2one("book.register", "Register",
                                         required=True)
    register_sequence = fields.Char(string="Register ID", required=True)
    book_name = fields.Many2one("product.product", sting="Book Name",
                                required=True)
    issued_date = fields.Date(sting="Issued Date", required=True)
    expiry_date = fields.Date(sting="Expiry Date", required=True)
    no_of_copies = fields.Integer(sting="No Of Copies")
    book_isbn = fields.Char(string="ISBN 10", required=True)
    edition = fields.Char(string="Edition")

    member_book_history = fields.Many2one('res.partner', string="Book History")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)

    def action_view_register(self):
        """ Function to view details of the register """
        value = {'name': ('Register'),
                 'view_mode': 'form',
                 # 'view_type': 'form',
                 'res_id': int(self.register_reference),
                 'res_model': 'book.register',
                 'type': 'ir.actions.act_window',
                 'target': 'new'}
        return value
