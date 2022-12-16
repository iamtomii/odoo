# -*- coding: utf-8 -*-
# from odoo import http
from datetime import datetime

from odoo import exceptions, http
from odoo.http import request, Response
import json
import csv
import logging
import base64

class LibraryController(http.Controller):
    def fill_record(self,member,book):
        date = datetime.strptime("12/21/2022", '%m/%d/%Y')
        partner_id = http.request.env['res.partner'].sudo().search([('x_Member_RFID', '=', member)])
        book_id = http.request.env['product.product'].sudo().search([('x_RFID', '=', book)])
        vals = {
            "register_book_name": book_id.id,
            "register_author_name": book_id.author_name,
            "register_book_title": book_id.book_title,
            "register_isbn_number": book_id.isbn_number,
            "register_isbn_13_number": book_id.isbn_13_number,
            "book_image": book_id.image_1920,
            "register_edition": book_id.edition,
            "calc_return_date": date,
            "register_member": partner_id.id,
            "register_member_id": partner_id["member_sequence"]
        }
        return vals
    @http.route('/hello', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/library_controller/get_book', type='json', auth='public')
    def get_book(self):
        request_data = json.loads(request.httprequest.data)
        if request_data is not None:
            print(request_data)
            rfid = request_data['rfid']
            value = []
            err_RFID = []
            for v in rfid:
                #print(v)
                product_templ_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', v]])
                #book_authors_id = http.request.env['book.authors'].sudo().search([['author_name', '=', product_templ_id['author_name']]])
                #print(book_authors_id['author_name'])
                #stock_id = http.request.env['stock.quant'].sudo().search([["product_id", "=", product_product_id['id']]], limit=1)
                author=product_templ_id['author_name']
                authors=""
                for a in range(len(author)):
                    authors += author[a]['author_name']
                    if a>0:
                        authors+=", "+author[a]['author_name']

                #print(author['author_name'])
                vals = {
                #"Type":"Product_card",
                "RFID": product_templ_id['x_RFID'],
                "Book_title": product_templ_id['book_title'],
                "ISBN_13": product_templ_id['isbn_13_number'],
                "Author": authors,
                "Categories":product_templ_id['categories']
                }
                if vals['Book_title'] is not False:
                    value.append(vals)
            values={ "Type":"Product_Card",
                "content":value

            }
            return values

    @http.route('/library_controller/get_member', type='json', auth='public')
    def get_member(self):
        request_data=json.loads(request.httprequest.data)
        if request_data is not None:
            rfid = request_data['rfid']
            print(rfid)
            value = []
            v=rfid[0]
            member_templ_id = http.request.env['res.partner'].sudo().search([['x_Member_RFID', '=', v]])
            print(member_templ_id)
            membership_type=member_templ_id["membership_type"]
            country=member_templ_id["country_id"]
            vals={
                "Type":"Member_Card",
                "content": {
                "RFID": member_templ_id['x_Member_RFID'],
                "Name":member_templ_id["name"],
                "Member_ID":member_templ_id["member_sequence"],
                "Gender":member_templ_id["sex"],
                "Current_membership":membership_type["membership_name"],
                "Contact":member_templ_id["street"],
                }
            }
        return vals

    @http.route('/library_controller/issue', auth='public', type='json', methods=['POST'], cors='*',csrf=False)
    def issueBook(self,**kwargs):
        request_data = json.loads(request.httprequest.data)
        print(request_data)
        if request_data is not None:
            member = request_data['member']
            books=request_data['books']
            #product_product_id = http.request.env['product.product'].sudo().search([('name', '=', "Animal Stories")])

            for i in books:
                vals=self.fill_record(member,i)
                http.request.env['book.register'].sudo().create(vals)
        args = {'success': True, 'message': 'Success'}
        return args

    @http.route('/library_controller/test', auth='public', type='json', methods=['POST'], cors='*', csrf=False)
    def issue_Book(self, **kwargs):
        request_data = json.loads(request.httprequest.data)
        print(request_data)
        args = {'success': True, 'message': 'Success'}
        return args
        # if vals['Product_name'] is not False:
        #   value.append(vals)
        #  else:
        # err_RFID.append(v)
    #  return value, err_RFID
#     @http.route('/library_controller/library_controller', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/library_controller/library_controller/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('library_controller.listing', {
#             'root': '/library_controller/library_controller',
#             'objects': http.request.env['library_controller.library_controller'].search([]),
#         })

#     @http.route('/library_controller/library_controller/objects/<model("library_controller.library_controller"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library_controller.object', {
#             'object': oblo
#         })



