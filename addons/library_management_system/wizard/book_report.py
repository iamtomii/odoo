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

from datetime import date

from odoo import api, models


class LibraryBookReport(models.Model):
    """ Model for book report """
    _name = 'books.report'

    def get_report(self):
        """ Function to print pdf report """
        return self.env.ref(
            'library_management_system.book_report_id').report_action(
            self, data=None)


class LibraryBookReportPdf(models.AbstractModel):
    """ Abstract model for generating PDF report value and send to template """

    _name = 'report.library_management_system.book_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Provide report values to template """
        # qry = self.env['product.product'].search([])
        company_id = self.env.user.company_id.id
        query = """select pp.id as pp_id ,pp.product_tmpl_id, pt.is_a_book
                from product_product pp
                join product_template pt
                on pt.id = pp.product_tmpl_id 
                where pt.company_id = %s""" % company_id
        self._cr.execute(query)
        qry = self._cr.dictfetchall()
        book_id = []
        for book in qry:
            if book['is_a_book']:
                book_id.append(book['pp_id'])
        lst = []
        sl_no = 1
        for cur_id in book_id:
            book = self.env['product.product'].browse(cur_id)
            qty_available = 0
            # get on hand from all location
            for loc in self.env['stock.location'].sudo().search([]):
                if loc.usage == 'internal':
                    qty_available += self.env[
                        'stock.quant']._get_available_quantity(
                        book, loc)
            publisher = book.product_tmpl_id.publisher.publisher_name or False
            author_names = ''
            # get authors of a book
            authors = book.product_tmpl_id.author_name
            if authors:
                for author in authors:
                    name = author.author_name
                    if name:
                        author_names += name + ", "
            lst.append({
                'sl_no': sl_no or '',
                'book_name': book.name or '',
                'authors': author_names or '',
                'publisher': publisher or '',
                'isbn_10': book.isbn_number or '',
                'isbn_13': book.isbn_13_number or '',
                'category': book.categories or '',
                'on_hand': qty_available
            })
            sl_no += 1

        return {
            'values': lst,
            'rep_date': str(date.today()) or False,
        }
