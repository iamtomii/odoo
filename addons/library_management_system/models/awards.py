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

from odoo import models, fields


class LibraryAwards(models.Model):
    """ Model for storing awards """

    _name = "library.awards"
    _description = "Awards"
    _rec_name = "award_name"

    award_name = fields.Char(string="Award Name", required=True,
                             help="Award name")

    image_medium = fields.Binary(help="image for award", sting="Image")
    country = fields.Many2one("res.country", string="Country",
                              help="Country for award")
    awarded_by = fields.Char(string="Awarded by", help="Awarded by")
    ribbon = fields.Binary(string="Ribbon", help="Ribbon image for the award")
    next = fields.Char(string="Next (higher)", help="Next higher award")
    lower = fields.Char(string="Next (lower)", help="Next lower award")

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
