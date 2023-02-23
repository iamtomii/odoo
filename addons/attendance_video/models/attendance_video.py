from odoo import fields, models
class SchoolProfile(models.Model):
    _name = "attendance.video"
    _inherit = "hr.attendance"
    attendance_id = fields.Many2one('hr.attendance', string="attendance id")
    checkin_video=fields.Char(string="Check In Video link",size=1000000)
    checkout_video=fields.Char(string="Check Out Video link",size=1000000)


