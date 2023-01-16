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
        print(request_data)
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
        print(request_data)
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
        print(data)
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

    @http.route('/inventory_controller/inventory/create_transfer/transfer', auth='public', methods=['POST'], type='json', cors='*',
                    csrf=False)
    def create_transfer(self, **kwargs):
        request_data = json.loads(request.httprequest.data)
        print(request_data)
        if request_data is not None:
            type=request_data['Operation Type'][0].split(": ")
            print(type)
            contact=request_data['Contact'][0].split(", ")
            print(contact)
            source=request_data["Source Location"][0].split("/")
            print(source)
            destination=request_data['Destination Location'][0].split("/")
            sourcedocument=request_data['Source Document'][0]
            print(destination)
            rfid=request_data['rfid']
            print(rfid)

            type_id=http.request.env['stock.picking.type'].sudo().search([["name","=",type[1]]])
           # print(type_id[0]["return_picking_type_id"])
            if (type_id[0]['name']=="Receipts"):
                print("hi");
                self.receipts_transfer(type_id, contact, source,rfid,sourcedocument)
            elif (type_id[0]['name']=="Internal Transfers"):
                #self.receipts_transfer(type_id,contact,destination)
                self.internal_transfer(type_id,contact,source,destination,rfid,sourcedocument)
            elif (type_id[0]['name']=="Manufacturing"):
                #self.receipts_transfer(type_id,contact,destination)
                self.internal_transfer(type_id,contact,source,destination,rfid,sourcedocument)

            elif (type_id[0]["name"]=="Delivery Orders"):
                self.delivery_orders_transfer(type_id, contact,source,rfid,sourcedocument)
            elif (type_id[0]["name"]=="Returns"):
                self.return_transfer(type_id, contact,source,rfid,sourcedocument)



        return Response(json.dumps(json.dumps({
            "code": 201,
            "message": 'Successfully Update Product Quantity'})))
    def receipts_transfer(self,type_id,contact,destination,rfid,sourcedocument):
        #contact
        if len(contact)==1:
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[0]]])
        else:
            parent_id = http.request.env['res.partner'].sudo().search([["name", "=", contact[0]]])
            print(parent_id['id'])
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[1]], ["parent_id", "=", parent_id['id']]])
        # print(destination[0])
        #destination
        if len(destination) == 1:
            destination_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", destination[0]]])
        else:
            location_name = http.request.env['stock.location'].sudo().search([["name", "=", destination[0]]])
            destination_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", destination[1]], ["location_id", "=", location_name['id']]])
        destination_id_local = destination_id[0]
        #  print(destination_id)
        vals = {
            "partner_id": contact_id['id'],
            "picking_type_id": type_id[0]['id'],
            "location_dest_id": destination_id_local['id'],
            "location_id": 4,
            "user_id": 2,
            "company_id": 1,
            "origin": sourcedocument
        }
        result = http.request.env['stock.picking'].sudo().create(vals)
        print(result['id'])
        location_id = 4
        location_dest_id = destination_id['id']
        self.stock_move_transfer(rfid, location_dest_id, contact_id, result, location_id)
    def internal_transfer(self,type_id,contact,source,destination,rfid,sourcedocument):
        #contact
        if len(contact)==1:
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[0]]])
        else:
            parent_id = http.request.env['res.partner'].sudo().search([["name", "=", contact[0]]])
            print(parent_id['id'])
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[1]], ["parent_id", "=", parent_id['id']]])
        # print(destination[0])
        #source
        if len(source)==1:
            source_id = http.request.env['stock.location'].sudo().search([["name", "=", source[0]]])
        else:
            source_location_name = http.request.env['stock.location'].sudo().search([["name", "=", source[0]]])
            source_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", source[1]], ["location_id", "=", source_location_name['id']]])
        source_id_local=source_id[0]
        print(source_id_local['id'])
        #destination
        if len(destination) == 1:
            destination_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", destination[0]]])
        else:
            location_name = http.request.env['stock.location'].sudo().search([["name", "=", destination[0]]])
            destination_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", destination[1]], ["location_id", "=", location_name['id']]])
        destination_id_local = destination_id[0]
        vals = {
            "partner_id": contact_id['id'],
            "picking_type_id": type_id[0]['id'],
            "location_dest_id": destination_id_local['id'],
            "location_id": source_id_local['id'],
            "user_id": 2,
            "company_id": 1,
            "origin": sourcedocument
        }
        result = http.request.env['stock.picking'].sudo().create(vals)
        print(result['id'])
        location_id = source_id_local['id']
        location_dest_id = destination_id_local['id']
        self.stock_move_transfer(rfid, location_dest_id, contact_id, result, location_id)
    def delivery_orders_transfer(self,type_id, contact,source,rfid,sourcedocument):
        # contact
        if len(contact) == 1:
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[0]]])
        else:
            parent_id = http.request.env['res.partner'].sudo().search([["name", "=", contact[0]]])
            print(parent_id['id'])
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[1]], ["parent_id", "=", parent_id['id']]])
        # print(destination[0])
        # source
        if len(source)==1:
            source_id = http.request.env['stock.location'].sudo().search([["name", "=", source[0]]])
        else:
            source_location_name = http.request.env['stock.location'].sudo().search([["name", "=", source[0]]])
            source_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", source[1]], ["location_id", "=", source_location_name['id']]])
        source_id_local = source_id[0]

        #  print(destination_id)
        vals = {
            "partner_id": contact_id['id'],
            "picking_type_id": type_id[0]['id'],
            "location_dest_id": 5,
            "location_id": source_id_local['id'],
            "user_id": 2,
            "company_id": 1,
            "origin": sourcedocument

        }
        result = http.request.env['stock.picking'].sudo().create(vals)
        print(result['id'])
        location_id = source_id['id']
        location_dest_id = 5
        self.stock_move_transfer(rfid, location_dest_id, contact_id, result, location_id)




    def return_transfer(self,type_id,contact,destination,rfid,sourcedocument):
        # contact
        if len(contact) == 1:
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[0]]])
        else:
            parent_id = http.request.env['res.partner'].sudo().search([["name", "=", contact[0]]])
            print(parent_id['id'])
            contact_id = http.request.env['res.partner'].sudo().search(
                [["name", "=", contact[1]], ["parent_id", "=", parent_id['id']]])
        # print(destination[0])
        #destination
        if len(destination) == 1:
            destination_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", destination[0]]])
        else:
            location_name = http.request.env['stock.location'].sudo().search([["name", "=", destination[0]]])
            destination_id = http.request.env['stock.location'].sudo().search(
                [["name", "=", destination[1]], ["location_id", "=", location_name['id']]])
        destination_id_local = destination_id[0]
        #  print(destination_id)
        vals = {
            "partner_id": contact_id['id'],
            "picking_type_id": type_id[0]['id'],
            "location_dest_id": destination_id_local['id'],
            "location_id": 4,
            "user_id": 2,
            "company_id": 1,
            "origin":sourcedocument
            #"move_ids_without_package":35
        }
        result=http.request.env['stock.picking'].sudo().create(vals)
        print(result['id'])
        location_id=4
        location_dest_id=destination_id['id']
        self.stock_move_transfer(rfid,location_dest_id,contact_id,result,location_id)


    def stock_move_transfer(self,rfid,location_dest_id,contact_id,result,location_id):
        for line in rfid:
            product_id = http.request.env['product.product'].sudo().search([['x_RFID', '=', line]])
            product_template_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', line]])
            print(product_id['id'])
            move_vals = {
                "product_id": product_template_id['id'],
                "product_uom_qty": 1,
                "product_uom": 1,
                "location_id":location_id,
                "location_dest_id":location_dest_id,
                "partner_id": contact_id['id'],
                "picking_id":result['id'],
                "name":product_template_id['name'],
                "state":"done",
                "quantity_done":1
            }
            http.request.env['stock.move'].sudo().create(move_vals)
    @http.route('/inventory/transfer/gettype',methods=['POST'],type="json",auth='public',csrf=False)
    def get_type(self):
        request_data = json.loads(request.httprequest.data)
        print(request_data)
        if request_data is not None:
            type_code=request_data["type"].replace(" ","_")
            print(type_code)
            user_id = http.request.env['res.users'].sudo().search([["job_title", "=", "Chief Executive Officer"]])
            adress_uid = user_id.address_id
            adress_name = adress_uid.name.replace("My Company (", "").replace(")", "")
            print(adress_name)
            type_transfer = http.request.env['stock.picking.type'].sudo().search([["company_id", "=", adress_uid.id],["code","=",type_code]])
            print(type_transfer)
            list_type = ["type"]
            for type_id in type_transfer:
                type_name = adress_name + ": " + type_id.name + ""
                list_type.append(type_name)


        return list_type
    @http.route('/inventory/transfer/getcontact',methods=['POST'],type="json",auth='public',csrf=False)
    def get_contact(self):
        list_partner=["contact"]
        request_data = json.loads(request.httprequest.data)
        partner_id=http.request.env['res.partner'].sudo().search([["company_id","!=","1"]])
        # for person_id in partner_id:
        #     parent_id=person_id["parent_id"]
        #     if parent_id.name is not False:
        #         list_partner.append(parent_id.name + ", "+person_id.name)
        #     else:
        #         list_partner.append(person_id.name)
        for person in partner_id:
            list_partner.append(person['display_name'])
        return list_partner
    @http.route('/inventory/transfer/getwarehouse',methods=['POST'],type="json",auth='public',csrf=False)
    def get_warehouse(self):
        list_location=["source"]
        request_data = json.loads(request.httprequest.data)
        location_id=http.request.env['stock.location'].sudo().search([["active","=","true"],["usage","!=","view"]])
        for location in location_id:
            list_location.append(location['complete_name'])
        return list_location
    @http.route('/inventory/transfer/getwarehousedest',methods=['POST'],type="json",auth='public',csrf=False)
    def get_warehousedest(self):
        list_location=["dest"]
        request_data = json.loads(request.httprequest.data)
        location_id=http.request.env['stock.location'].sudo().search([["active","=","true"],["company_id","!=","2"],["usage","!=","view"]])
        for location in location_id:
            list_location.append(location['complete_name'])
        return list_location
    @http.route('/inventory/transfer/gettypetransfer',methods=['POST'],type="json",auth='public',csrf=False)
    def get_typetransfer(self):
        request_data = json.loads(request.httprequest.data)
        print(request_data)
        user_id = http.request.env['res.users'].sudo().search([["job_title","=","Chief Executive Officer"]])
        adress_uid=user_id.address_id
        adress_name=adress_uid.name.replace("My Company (","").replace(")","")
        print(adress_name)
        type_transfer=http.request.env['stock.picking.type'].sudo().search([["company_id","=",adress_uid.id]])
        print(type_transfer)
        title_type=["typetransfer"]
        list_type=[]
        for type_id in type_transfer:
            # type_name=adress_name +": "+type_id.name+""
            list_type.append(type_id.code.replace("_"," "))
        title_type.extend(list(set(list_type)))
        return title_type