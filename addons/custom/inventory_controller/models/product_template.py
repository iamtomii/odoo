from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_RFID = fields.Char(string='RFID')