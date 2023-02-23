from odoo import models,fields
class HrAttendanceVideo(models.Model):
    _name ='hr.video'
    _inherit = 'hr.attendance'
    attendance_id=fields.Many2one('hr.attendance',string="attendance id")
    checkin_video=fields.Text(string="Check In Video link")
    checkout_video=fields.Text(string="Check Out Video link")
    menu_id = fields.Many2one('ir.ui.menu', string='Menu Item', readonly=True)