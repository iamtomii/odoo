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

from odoo import api, fields, models
import json
import io
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class LibraryMemberReport(models.TransientModel):
    """ Model for member report """
    _name = 'member.report'

    date_today = fields.Date(string="Date Today",
                             default=fields.Date.context_today)
    membership_type = fields.Many2one("membership.types",
                                      string="Membership",
                                      help="Name of the membership")
    block_status = fields.Boolean(string="Blocked Members",
                                  help="Display blocked members only")

    def get_report(self):
        """ Function to print pdf report """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_today': self.date_today,
                'membership_id': self.membership_type.id,
                'block_status': self.block_status,
            },
        }
        return self.env.ref(
            'library_management_system.member_report_id').report_action(
            self, data=data)

    def get_xlsx_report(self):
        """ Print xlsx report """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_today': self.date_today,
                'membership_id': self.membership_type.id,
                'block_status': self.block_status,
            },
        }

        return {
            'type': 'ir.actions.report',
            'report_type': 'library_xlsx',
            # 'name': json.dumps(data, default=date_utils.json_default),

            'data': {'model': self._name,
                     'name': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
        },
        }



    def generate_xlsx_report(self, data, response):
        """ Function generate report and write to excel sheet """

        data = json.loads(data)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        membership_obj = self.env['membership.types'].sudo()
        company_id = self.env.user.company_id.id
        membership = membership_obj.browse(data['form']['membership_id'])
        query = """select * from res_partner 
        where 
        is_a_member=True 
        and 
        created_company_id=%s""" % company_id

        if membership:
            query += """ and membership_type=%s """ % \
                     data['form']['membership_id']
        if data['form']['block_status']:
            query += """ and block_status=True """
        self._cr.execute(query)
        members = self._cr.dictfetchall()

        sheet = workbook.add_worksheet('Report')
        bold = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})
        date = workbook.add_format({'bold': True, 'font_size': '10px'})
        date_to = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px',
             'border': 1})
        txt = workbook.add_format({'font_size': '10px', 'border': 1})
        type = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})
        sheet.merge_range('C2:K3', 'MEMBERS REPORT', head)
        sheet.write('C5', "REPORT DATE", date)
        sheet.write('C6', data['form']['date_today'], date)
        sheet.write('D5', "BLOCK STATUS", date_to)
        sheet.write('D6', str(data['form']['block_status']), date)
        sheet.write('E5', "MEMBERSHIP TYPE", date_to)
        sheet.write('E6', membership.membership_name, date)
        sheet.write('C8', 'MEMBERSHIP ID', bold)
        sheet.write('D8', 'MEMBER', bold)
        sheet.write('E8', 'ADDRESS', bold)
        sheet.write('F8', 'MOBILE', bold)
        sheet.write('G8', 'EMAIL', bold)
        sheet.write('H8', 'MEMBERSHIP', bold)
        sheet.write('I8', 'EXPIRY', bold)
        sheet.write('J8', 'DUE PAID', bold)
        sheet.write('K8', 'BOOK ON HAND', bold)

        # set column width
        sheet.set_column(2, 7, 15)
        sheet.set_column(3, 7, 15)
        sheet.set_column(4, 7, 15)
        sheet.set_column(5, 7, 15)
        sheet.set_column(6, 7, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 7, 15)
        sheet.set_column(9, 7, 15)
        sheet.set_column(10, 7, 15)

        row_num = 7
        col_num = 2
        for memb in members:
            membership = membership_obj.browse(memb['membership_type'])

            sheet.write(row_num + 1, col_num, memb['member_sequence'], txt)
            sheet.write(row_num + 1, col_num + 1, memb['name'], txt)
            sheet.write(row_num + 1, col_num + 2, memb['street'], txt)
            sheet.write(row_num + 1, col_num + 3, memb['mobile'], txt)
            sheet.write(row_num + 1, col_num + 4, memb['email'], txt)
            sheet.write(row_num + 1, col_num + 5, membership.membership_name,
                        txt)
            sheet.write(row_num + 1, col_num + 6,
                        str(memb['membership_expiry_date']),
                        txt)
            sheet.write(row_num + 1, col_num + 7, memb['due_amount_paid'], txt)
            sheet.write(row_num + 1, col_num + 8, memb['book_count'], txt)
            row_num = row_num + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class LibraryMemberReportPdf(models.AbstractModel):
    """ Abstract model for generating PDF report value and send to template """

    _name = 'report.library_management_system.member_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Provide report values to template """
        membership_obj = self.env['membership.types'].sudo()
        company_id = self.env.user.company_id.id
        membership = membership_obj.browse(data['form']['membership_id'])

        query = """select * from res_partner 
                where 
                is_a_member=True 
                and 
                created_company_id=%s""" % company_id

        if membership:
            query += """ and membership_type=%s """ % \
                     data['form']['membership_id']
        if data['form']['block_status']:
            query += """ and block_status=True """
        self._cr.execute(query)
        members = self._cr.dictfetchall()
        lst = []
        for memb in members:
            membership = membership_obj.browse(memb['membership_type'])
            lst.append({
                'memb_id': memb['member_sequence'] or '',
                'member_name': memb['name'] or '',
                'address': memb['street'] or '',
                'mobile': memb['mobile'] or '',
                'email': memb['email'] or '',
                'cur_membership': membership.membership_name or '',
                'exp_date': memb['membership_expiry_date'] or '',
                'book_on_hand': memb['book_count'] or '',
                'due_paid': memb['due_amount_paid'] or ''
            })
        return {
            'values': lst,
            'rep_date': data['form']['date_today'] or False,
            'membership_name': membership.membership_name,
            'block_status': data['form']['block_status'],
        }

