# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class inventory_controller(models.Model):
#     _name = 'inventory_controller.inventory_controller'
#     _description = 'inventory_controller.inventory_controller'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
