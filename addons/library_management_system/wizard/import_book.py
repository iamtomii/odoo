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

import base64
import json
import logging

import certifi
import urllib3

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportBookDetails(models.TransientModel):
    _name = 'import.book'

    isbn_value = fields.Char(string="ISBN_13 / ISBN_10", required=True,
                             help="13 Digit ISBN number")

    book_found = fields.Boolean("Book Found", default=False)

    def import_book_wizard(self):
        """ Action showing wizard for importing book """

        return {
            'name': _('Import Book'),
            'view_mode': 'form',
            'res_model': 'import.book',
            'type': 'ir.actions.act_window',
            'edit': True,
            'target': 'new',
        }

    def get_book_details(self):
        """ Get book details from api call using the isbn number and
        book image from the thumbnail url """
        isbn = str(self.isbn_value)
        try:
            # get book details from api
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                       ca_certs=certifi.where())
            url = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
            response1 = http.request('GET', url + isbn)
            res = json.loads(response1.data.decode("utf-8"))

            if res['totalItems'] == 0:
                raise UserError(_(
                    'ISBN number not found, please check the entered\
                     ISBN number you have entered'))
            # get book thumbnail image
            if 'imageLinks' in res['items'][0]['volumeInfo']:
                image_response = http.request('GET', res['items'][0]['volumeInfo'][
                    'imageLinks']['thumbnail'])
                image_thumbnail = base64.b64encode(image_response.data)
        except Exception as e:
            raise UserError("Error %s" % e)

        # format and get author names
        authors = []
        try:
            authors_obj = self.env['book.authors'].search([])
            for author in res['items'][0]['volumeInfo']['authors']:
                auth_found = False
                for db_author in authors_obj:
                    if db_author.author_name == author:
                        authors.append(db_author.id)
                        auth_found = True
                        break
                if not auth_found:
                    new_author = authors_obj.create(
                        {'author_name': author})
                    authors.append(new_author.id)
        except Exception as e:
            _logger.info("# book create api authors not found %s" % e)
            pass

        # format and get publisher names
        try:
            publisher_name = res['items'][0]['volumeInfo']['publisher']
            publisher_obj = self.env['book.publisher'].search(
                [("publisher_name", "=", publisher_name)])
            if not publisher_obj:
                publisher_obj = self.env['book.publisher'].create(
                    {'publisher_name': publisher_name})
        except Exception as e:
            _logger.info("# book create api authors not found %s" % e)
            pass

        categories = ""
        # format category names
        try:
            for categ in res['items'][0]['volumeInfo']['categories']:
                if categories != "":
                    categories += ", " + categ
                else:
                    categories = categ
        except Exception as e:
            _logger.info("# book create api categories not found %s" % e)
            pass
        ctx = {}
        try:
            ctx.update(
                {'default_name': res['items'][0]['volumeInfo']['title'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_title': res['items'][0]['volumeInfo'][
                                             'title'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_authors': [(6, 0, [y for y in authors])]})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_description': res['items'][0]['volumeInfo'][
                                                   'description'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_isbn_13': res['items'][0]['volumeInfo'][
                                               'industryIdentifiers'][1][
                                               'identifier'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_isbn_10': res['items'][0]['volumeInfo'][
                                               'industryIdentifiers'][0][
                                               'identifier'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_pageCount': int(
                res['items'][0]['volumeInfo']['pageCount']) or 0})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_webReaderLink': res['items'][0]['accessInfo'][
                                                     'webReaderLink'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_previewLink': res['items'][0]['volumeInfo'][
                                                   'previewLink'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_book_language': res['items'][0]['volumeInfo'][
                                                     'language'] or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_image_medium': image_thumbnail or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update({'default_categories': categories or ""})
        except Exception as e:
            _logger.info("# book create api some properties not found %s" % e)
            pass
        try:
            ctx.update(
                {'default_publisher': publisher_obj.id or ""})
        except Exception as e:
            _logger.info("# book create api publisher not found %s" % e)
            pass
        try:
            ctx.update({'default_averageRating': res['items'][0]['volumeInfo'][
                                                     'averageRating'] or 0})
        except Exception as e:
            _logger.info("# book create api averageRating not found %s" % e)
            pass
        return {
            'name': _('Import Book'),
            'view_mode': 'form',
            'res_model': 'create.book',
            'type': 'ir.actions.act_window',
            'edit': False,
            'target': 'new',
            'context': ctx,
        }


class BookDetailsCreate(models.Model):
    _name = 'create.book'

    name = fields.Char(string="Book Name")
    authors = fields.Many2many("book.authors", string="Authors")
    title = fields.Char(string="Title")
    publisher = fields.Many2one("book.publisher", string="Publisher")
    description = fields.Text(string="Description")
    isbn_13 = fields.Char(string="ISBN_13")
    isbn_10 = fields.Char(string="ISBN_10")
    pageCount = fields.Integer(string="PageCount")
    categories = fields.Char(string="Categories")
    averageRating = fields.Char(string="AverageRating")
    webReaderLink = fields.Char(string="WebReaderLink")
    previewLink = fields.Char(string="PreviewLink")
    image_medium = fields.Binary(store=True, attachment=True)
    book_language = fields.Char(string="Language")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)

    def _check_isbn(self, isbn_10, isbn_13):
        """ Check whether isbn already exists
        :return book_isbn_found true if found in db
        :argument isbn_10 10 digit isbn number
        :argument isbn_13 13 digit isbn number"""
        product_obj = self.env['product.template'].search([])
        book_isbn_found = False
        for book in product_obj:
            if book.isbn_number == isbn_10 or book.isbn_13_number == isbn_13:
                book_isbn_found = True
        return book_isbn_found

    def create_book(self):
        """ Create a book with provided datas """
        isbn_found = self._check_isbn(self.isbn_10, self.isbn_13)
        if not isbn_found:
            product_obj = self.env['product.template']
            product_ctx = {
                'is_a_book': True,
                'type': 'product',
                'name': self.name,
                'image_1920': self.image_medium,
                'book_title': self.title,
                'author_name': [(6, 0, [int(y.id) for y in self.authors])],
                'pages': self.pageCount,
                'company_id': self.env.user.company_id.id,
                'isbn_number': self.isbn_10,
                'isbn_13_number': self.isbn_13,
                'publisher': int(self.publisher.id),
                'description': self.description,
                'categories': self.categories,
                'rating': self.averageRating,
                'web_reader_link': self.webReaderLink,
                'preview_link': self.previewLink,
                'book_language': self.book_language,
            }
            new_book = product_obj.create(product_ctx)
            category = self.env['product.category'].search(
                [('name', '=', 'Books')], limit=1)
            if category:
                new_book.update({'categ_id': int(category.id)})
        else:
            raise UserError("Book already exists in database")
