from odoo import fields, models
class SchoolProfile(models.Model):
    _name = "school.profile"

    name=fields.Char(String="School Name")
    email=fields.Char(String="Email")
    phone=fields.Char("Phone")
    attendance_id = fields.Many2one('hr.attendance', string="attendance id")