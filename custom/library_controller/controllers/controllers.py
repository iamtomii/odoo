# -*- coding: utf-8 -*-
# from odoo import http
from datetime import datetime

from odoo import exceptions, http
from odoo.http import request, Response
import json
import csv
import logging
import os.path
import base64
from datetime import datetime
current_Date = datetime.today().strftime('%m/%d/%Y')

class LibraryController(http.Controller):
    def create_new_inventory_record(self,data_read,rfidHad):
        for line in data_read:
            if line["rfid"] not in rfidHad:
                rfid = line["rfid"]
                quantity=line["quantity"]
                product_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', rfid]])
                product_product_id = http.request.env['product.product'].sudo().search(
                    [('product_tmpl_id', '=', product_id['id'])])
                date = datetime.strptime("12/31/2022", '%m/%d/%Y')
                print(product_id)
                vals1 = {
                    "product_id": product_product_id.id,
                    "inventory_quantity":quantity,
                    "inventory_diff_quantity":quantity,
                    "inventory_quantity_set":True,
                    "location_id": 8,
                    "company_id": 1
                    }
                http.request.env['stock.quant'].sudo().create(vals1)

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
                product_templ_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', v]])
                author=product_templ_id['author_name']
                authors=""
                for a in range(len(author)):
                    authors += author[a]['author_name']
                    if a>0:
                        authors+=", "+author[a]['author_name']
                vals = {
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
            for i in books:
                vals=self.fill_record(member,i)
                http.request.env['book.register'].sudo().create(vals)
        args = {'success': True, 'message': 'Success'}
        return args
    @http.route('/inventory_controller/product/get_quant', type='json', auth='public')
    def get_multiple_product(self):
        request_data = json.loads(request.httprequest.data)
        if request_data is not None:
            rfid = request_data['rfid']
            value = []
            err_RFID = []
            for v in rfid:
                product_templ_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', v]])
                account_tax=product_templ_id['taxes_id']
                product_product_id = http.request.env['product.product'].sudo().search(
                   [['product_tmpl_id', '=', product_templ_id['id']]])
                stock_id = http.request.env['stock.quant'].sudo().search(
                   [["product_id", "=", product_product_id['id']]], limit=1)
                vals = {
                    "RFID": product_templ_id['x_RFID'],
                    "Product_name": product_templ_id['name'],
                    "Product_code": product_templ_id['default_code'],
                    "Price": product_templ_id['list_price'],
                    "Customers_taxes": account_tax["amount"],
                    "quantity": 1,
                }
                if vals['Product_name'] is not False:
                    value.append(vals)
                else:
                    err_RFID.append(v)
        return value, err_RFID



    @http.route('/inventory_controller/create_inventory', auth='public', methods=['POST'], type='json', cors='*',
                    csrf=False)
    def create_inventory(self, **kwargs):
        request_data = json.loads(request.httprequest.data)
        # print(request_data)
        if request_data is not None:
            data_get = base64.b64decode(request_data['base64']).decode("UTF-8")
            data_get_split = data_get.replace('"', '').split('\n')
            list_data_get=[x.split(",") for x in data_get_split]
            data=[]
            for i in range (1,len(list_data_get)-1):
                data.append(self.create_dict(list_data_get[0],list_data_get[i]))
        rfidHad = []
        for line in data:
            rfid = line['rfid'],
            barcode = line['barcode'],
            product = line['product_name'],
            quantity = line['quantity'],
            product_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', rfid]])
            product_product_id = http.request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', product_id['id'])])
            stock_id = http.request.env['stock.quant'].sudo().search(
                [("product_id", "=", product_product_id['id'])])
            if (http.request.env['stock.quant'].sudo().search([("product_id", "=", product_product_id['id'])])):
                vals = {
                    'inventory_quantity': quantity[0]
                }

                rfidHad.append(line['rfid'])
                for value in stock_id:
                    value.sudo().write(vals)
        print(data)
        print(rfidHad)
        self.create_new_inventory_record(data, rfidHad)
        return Response(json.dumps(json.dumps({
            "code": 201,
            "message": 'Successfully Update Product Quantity',})))
    def create_dict(self,keydict,valuedict):
        res={}
        for key in keydict:
            for value in valuedict:
                res[key] = value
                valuedict.remove(value)
                break
        return res
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
#     @http.route('/inventory_controller/create_inventory', auth='public', methods=['POST'],type='json', cors='*',
#                 csrf=False)
#     def create_inventory(self,**kwargs):
#         request_data = json.loads(request.httprequest.data)
#         #print(request_data)
#         if request_data is not None:
#             data_get = base64.b64decode(request_data['base64']).decode("UTF-8")
#             my_path = os.path.abspath(os.path.dirname("controllers"))+"\custom\library_controller\path\savefile.csv"
#             with open(my_path, 'w',
#                         encoding='utf-8') as csvFile:
#                 tmp = data_get.replace('"', '')
#                 tmp_2 = tmp.replace('\n', '')
#                 csvFile.write(tmp)
#                 csvFile.close()
#             with open(my_path, mode='r',
#                         encoding='utf-8') as file:
#                 data_read = csv.DictReader(file)
#                 rfidHad=[]
#                 list=[]
#                 for line in data_read:
#                     print(type(line))
#                     list.append(line)
#                     rfid = line['rfid'],
#                     barcode = line['barcode'],
#                     product = line['product_name'],
#                     quantity = line['quantity'],
#                     product_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', rfid]])
#                     product_product_id = http.request.env['product.product'].sudo().search(
#                         [('product_tmpl_id', '=', product_id['id'])])
#                     stock_id = http.request.env['stock.quant'].sudo().search(
#                         [("product_id", "=", product_product_id['id'])])
#                     if(http.request.env['stock.quant'].sudo().search([("product_id", "=", product_product_id['id'])]) and stock_id["location_id"==8] ):
#                         vals = {
#                             'inventory_quantity': quantity[0]
#                         }
#
#                         rfidHad.append(line['rfid'])
#                         for value in stock_id:
#                             value.sudo().write(vals)
#                 self.createLib(list, rfidHad)
#             return Response(json.dumps(json.dumps({
#                 "code": 201,
#                 "message": 'Successfully Update Product Quantity',
#         })))
#
#
