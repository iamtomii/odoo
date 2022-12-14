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

from odoo import models, fields, api


class LibraryMembershipTypes(models.Model):
    """ Model for storing library membership details """

    _name = "membership.types"
    _description = "Membership Types"
    _rec_name = "membership_name"

    membership_name = fields.Char(string="Membership Name", required=True)

    membership_product = fields.Many2one("product.product", "Renewal Product",
                                         help="If not selected automatically \
                                         create a product of this name",
                                         domain=[('is_a_book', '=', False)])

    renewal_amount = fields.Float(sting="Renewal Amount", required=True,
                                  help="Membership renewal amount")
    expires_in = fields.Integer(string="Expiry In Days", default=0,
                                help="Membership duration in days")

    expiry_email = fields.Boolean(string="Expiry email",
                                  help="Send email on membership expiry")
    do_not_expire = fields.Boolean(string="Do Not Expire",
                                   help="Will not expire membership")

    email_template = fields.Many2one("mail.template", default=lambda
        self: self._get_report_template())

    note = fields.Text(string="Extra notes")

    no_of_books = fields.Integer(string="No of books",
                                 help="No of books a user can hold at a time",
                                 default=0)
    restrict_books = fields.Boolean(string="Restrict book count",
                                    help="Restrict ni of book that can hold \
                                    at a time for a member")

    terms_conditions = fields.One2many("membership.terms", "membership_id",
                                       string="Terms and Conditions")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)

    @api.model
    def create(self, vals):
        """ Create a product if no membership product selected """
        if not vals['membership_product']:
            context = {
                'name': vals['membership_name'],
                'type': 'service',
                'invoice_policy': 'order',
                'company_id': self.env['res.users'].browse(
                                     self.env.uid).company_id.id,
            }
            product = self.env['product.template'].create(context)
            vals['membership_product'] = product.product_variant_id.id
        return super(LibraryMembershipTypes, self).create(vals)

    def _get_report_template(self):
        """ Get default email template for membership expiry """
        template = self.env.ref(
            'library_management_system.email_template_membership_expiry',
            raise_if_not_found=False)

        return template.id if template else False


class MembershipTerms(models.Model):
    """ Model for terms and conditions in membership """
    _name = "membership.terms"
    _description = "Terms and condition for membership"
    _rec_name = "terms"

    membership_id = fields.Many2one("membership.types",
                                    string="Membership Types")
    terms = fields.Text(string="Terms and Conditions", required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
