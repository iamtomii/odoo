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

from odoo import models, fields, api


class LibraryBooks(models.Model):
    """ Extend product template for library management """

    _description = "Library Books"
    _inherit = 'product.template'

    author_name = fields.Many2many("book.authors", string="Authors",
                                   help="Author name")
    isbn_number = fields.Char(string="ISBN_10", copy=False,
                              help="International Standard Book Number \
                              (ISBN_10)")
    isbn_13_number = fields.Char(string="ISBN_13",
                                 help="International Standard "
                                      "Book Number(ISBN_13)")
    publisher = fields.Many2one("book.publisher",
                                string="Publisher Information",
                                help="Publisher details of the book")
    copyright = fields.Char(string="Copyright owner",
                            help="Copyright details of the book")
    edition = fields.Char(string="Edition details",
                          help="Edition details")
    book_title = fields.Char(string="Book Title",
                             help="Book title")
    pages = fields.Integer(string="Page Number",
                           help="Page number")

    issue_status = fields.Selection([('available', 'Available'),
                                     ('unavailable', 'Unavailable')])

    is_a_book = fields.Boolean(string="Is a Book", default=False,
                               help="Enable to use the product as abook")
    categories = fields.Char(string="Categories", help="Book categories")
    rating = fields.Char(string="Average Rating", help="Rating for the book")
    web_reader_link = fields.Char(string="Web Reader Link")
    preview_link = fields.Char(string="Preview Link")
    book_language = fields.Char(string="Language")

    pricing = fields.Boolean(string="Provide Pricing",
                             help="Select to define rental \
                                    amount for the book")
    rental_price = fields.One2many("book.rental", "book_id",
                                   string="Rental Pricing")
    issued_history = fields.One2many("issued.history", "book_issued_history")
    book_awards = fields.One2many("book.awards", "book_awards_id",
                                  string="Book awards")

    @api.onchange('is_a_book')
    @api.depends('is_a_book')
    def select_book(self):
        """ change to product when is a book is selected and also select
        book category"""
        if self.is_a_book:
            category = self.env['product.category'].search(
                [('name', '=', 'Books')], limit=1)
            if category:
                self.categ_id = int(category.id)
            self.type = 'product'


class BookAwards(models.Model):
    """ Model for storing book awards """
    _name = "book.awards"
    _description = "Book Awards"
    _rec_name = "award_name"

    award_id = fields.Many2one("library.awards", string="Award Name")
    award_name = fields.Char(string="Award Name")
    awarded_on = fields.Date(string="Awarded On")
    image_medium = fields.Binary(help="image for award", sting="Image")
    country = fields.Many2one("res.country", string="Country",
                              help="Country for award")
    awarded_by = fields.Char(string="Awarded by ")
    ribbon = fields.Binary(string="Ribbon", help="Ribbon for the award")
    next = fields.Char(string="Next (higher)", help="Next higher award")
    lower = fields.Char(string="Next (lower)", help="Next lower award")

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
    book_awards_id = fields.Many2one("product.template", string="Book")

    @api.onchange("award_id")
    @api.depends("award_id")
    def _get_award_id(self):
        """ Get award details on award id change """
        self.image_medium = self.award_id.image_medium
        self.country = self.award_id.country
        self.awarded_by = self.award_id.awarded_by
        self.ribbon = self.award_id.ribbon
        self.next = self.award_id.next
        self.lower = self.award_id.lower
        self.award_name = self.award_id.award_name


class BookAuthors(models.Model):
    """ Model for book authors """

    _name = "book.authors"
    _rec_name = "author_name"
    _description = "Author names for books"

    image_medium = fields.Binary(string="Author Image")
    author_name = fields.Char(string="Author name", required=True)
    language = fields.Char(string="Language", help="Author language")
    genre = fields.Char(string="Genre")
    Nationality = fields.Many2one("res.country", string="Nationality")
    born = fields.Date(string="Born")
    died = fields.Date(string="Died")
    author_book_qty = fields.Integer("Written books",
                                     compute="compute_written_book",
                                     help="Number of books written by author")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
    author_awards = fields.One2many("author.awards", "author_id",
                                    string="Author awards")

    def compute_written_book(self):
        """ Compute number of written books """
        books = self.env['product.template'].search([])
        book_count = 0
        for book in books:
            for author in book.author_name:
                if author.id == self.id:
                    book_count += 1
        self.author_book_qty = book_count

    def view_written_books(self):
        """ Function to view written books """
        books = self.env['product.template'].search([])
        book_ids = []
        for book in books:
            for author in book.author_name:
                if author.id == self.id:
                    book_ids.append(book.id)
        action = \
            self.env.ref('library_management_system.action_library_books').read()[
                0]
        if len(book_ids) > 1:
            action['domain'] = [('id', 'in', book_ids)]
        elif len(book_ids) == 1:
            action['views'] = [
                (self.env.ref('product.product_template_form_view').id,
                 'form')]
            action['res_id'] = book_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class AuthorAwards(models.Model):
    """ Model for storing author awards """
    _name = "author.awards"
    _description = "Author Awards"
    _rec_name = "award_name"

    award_id = fields.Many2one("library.awards", string="Award Name",
                               required=True)
    award_name = fields.Char(string="Award Name")
    awarded_on = fields.Date(string="Awarded On")
    image_medium = fields.Binary(help="image for award", sting="Image")
    country = fields.Many2one("res.country", string="Country",
                              help="Country for award")
    awarded_by = fields.Char(string="Awarded by ")
    ribbon = fields.Binary(string="Ribbon", help="Ribbon for the award")
    next = fields.Char(string="Next (higher)", help="next higher award")
    lower = fields.Char(string="Next (lower)", help="Next lower award")

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
    author_id = fields.Many2one("book.authors", string="Author")

    @api.onchange("award_id")
    @api.depends("award_id")
    def _get_award_id(self):
        """ Get award details on award id change """
        self.image_medium = self.award_id.image_medium
        self.country = self.award_id.country
        self.awarded_by = self.award_id.awarded_by
        self.ribbon = self.award_id.ribbon
        self.next = self.award_id.next
        self.lower = self.award_id.lower
        self.award_name = self.award_id.award_name


class BookPublisher(models.Model):
    """ Model for book publishers """

    _name = "book.publisher"
    _rec_name = "publisher_name"
    _description = "Publisher for book"

    image_medium = fields.Binary(string="Author Image")
    publisher_name = fields.Char(string="Publisher name", required=True)
    website = fields.Char(string="Official website")
    founder = fields.Char(string="Founder")
    country_origin = fields.Many2one("res.country", string="Country of origin")
    founded = fields.Date(string="Founded")
    publisher_book_qty = fields.Integer(string="Published Books",
                                        compute="compute_published_book")

    related_author_qty = fields.Integer(string="Authors Related",
                                        help="Authors related to publisher",
                                        compute="compute_related_author")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
    publisher_awards = fields.One2many("publisher.awards", "publisher_id",
                                       string="Publisher awards")

    def compute_published_book(self):
        """ Compute number of published books """
        books = self.env['product.template'].search([])
        book_count = 0
        for book in books:
            if book.publisher.id == self.id:
                book_count += 1
        self.publisher_book_qty = book_count

    def compute_related_author(self):
        """ Compute number of related authors """
        books = self.env['product.template'].search([])
        author_count = 0
        author_ids = []
        for book in books:
            if book.publisher.id == self.id:
                for author in book.author_name:
                    if author.id not in author_ids:
                        author_ids.append(author.id)
                        author_count += 1
        self.related_author_qty = author_count

    def view_published_books(self):
        """ Function to published books """
        books = self.env['product.template'].search([])
        book_ids = []
        for book in books:
            if book.publisher.id == self.id:
                book_ids.append(book.id)
        action = \
            self.env.ref('library_management_system.action_library_books').read()[
                0]
        if len(book_ids) > 1:
            action['domain'] = [('id', 'in', book_ids)]
        elif len(book_ids) == 1:
            action['views'] = [
                (self.env.ref('product.product_template_form_view').id,
                 'form')]
            action['res_id'] = book_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def view_related_authors(self):
        """ Function view related users to the publisher """
        books = self.env['product.template'].search([])
        author_ids = []
        for book in books:
            if book.publisher.id == self.id:
                for author in book.author_name:
                    if author.id not in author_ids:
                        author_ids.append(author.id)
        action = \
            self.env.ref('library_management_system.action_library_authors').read()[
                0]
        if len(author_ids) > 1:
            action['domain'] = [('id', 'in', author_ids)]
        elif len(author_ids) == 1:
            action['views'] = [
                (self.env.ref('library_management_system.book_authors_form_view').id,
                 'form')]
            action['res_id'] = author_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class PublisherAwards(models.Model):
    """ Model for storing publisher awards """
    _name = "publisher.awards"
    _description = "Publisher Awards"
    _rec_name = "award_name"

    award_id = fields.Many2one("library.awards", string="Award Name",
                               required=True)
    award_name = fields.Char(string="Award Name")
    awarded_on = fields.Date(string="Awarded On")
    image_medium = fields.Binary(help="image for award", sting="Image")
    country = fields.Many2one("res.country", string="Country",
                              help="Country for award")
    awarded_by = fields.Char(string="Awarded by ")
    ribbon = fields.Binary(string="Ribbon", help="Ribbon for the award")
    next = fields.Char(string="Next (higher)", help="Next higher award")
    lower = fields.Char(string="Next (lower)", help="Next lower award")

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
    publisher_id = fields.Many2one("book.publisher", string="Publisher")

    @api.onchange("award_id")
    @api.depends("award_id")
    def _get_award_id(self):
        """ Get award details on award id change """
        self.image_medium = self.award_id.image_medium
        self.country = self.award_id.country
        self.awarded_by = self.award_id.awarded_by
        self.ribbon = self.award_id.ribbon
        self.next = self.award_id.next
        self.lower = self.award_id.lower
        self.award_name = self.award_id.award_name


class BookRentalDetails(models.Model):
    """ Model for book rental details """
    _name = "book.rental"
    _description = "Book Rental details"

    book_id = fields.Many2one("product.template", string="Rental Pricing")
    from_day = fields.Integer(string="From", required=True,
                              help="From day to calculate rent")
    to_day = fields.Integer(string="To", required=True,
                            help="To day to calculate rent")
    duration = fields.Integer(string="Duration in Days", required=True,
                              help="One month is considered as 30 days")
    unit = fields.Selection([('days', 'Days'),
                             ('months', 'Months')], required=True)
    price = fields.Float(string="Price", required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)

    @api.onchange('from_day', 'to_day', 'unit')
    @api.depends('from_day', 'to_day', 'unit')
    def from_to_day(self):
        """ compute number of days when corresponding fields changes """
        if not self.unit:
            self.unit = 'days'
        if self.unit == 'days':
            self.duration = self.to_day - self.from_day
        elif self.unit == 'months':
            months = self.to_day - self.from_day
            self.duration = months * 30
        else:
            self.duration = 0


class BoosIssueHistory(models.Model):
    """ Model for storing issued book history """
    _name = "issued.history"
    _description = "Book Issued History"
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env[
                                     'res.users'].browse(
                                     self.env.uid).company_id.id)
    created_user = fields.Many2one('res.users', 'User Responsible',
                                   required=True, readonly=True,
                                   default=lambda self: self.env.uid)
    register_reference = fields.Many2one("book.register", "Register",
                                         required=True)
    register_sequence = fields.Char(string="Register ID", required=True)
    book_name = fields.Many2one("product.product", sting="Book Name",
                                required=True)
    issued_date = fields.Date(sting="Issued Date", required=True)
    expiry_date = fields.Date(sting="Expiry Date", required=True)
    no_of_copies = fields.Integer(sting="No Of Copies")
    book_isbn = fields.Char(string="ISBN 10", required=True)
    edition = fields.Char(string="Edition")
    member_book_history = fields.Many2one('res.partner', string="Member Name")
    book_issued_history = fields.Many2one('product.template',
                                          string="Issued Book")

    def action_view_register(self):
        """ Function to view details of the register """
        value = {'name': ('Register'),
                 'view_mode': 'form',
                 'res_id': int(self.register_reference),
                 'res_model': 'book.register',
                 'type': 'ir.actions.act_window',
                 'target': 'new'}
        return value
