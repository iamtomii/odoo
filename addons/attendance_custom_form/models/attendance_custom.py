from odoo import models, fields, api


class AttendanceCustom(models.Model):
    _inherit = "hr.attendance"
    video_base64 = fields.Char(string="Video Base64", compute="_compute_video_base64",size=1000000)

    @api.depends('check_in')
    def _compute_video_base64(self):
        for attendance in self:
            if attendance.check_in:
                a=str(self.env['attendance.video'].search([['attendance_id','=',attendance.id]]).checkin_video)
                attendance.video_base64 =a
            else:
                attendance.video_base64 = False




