import io

from odoo import exceptions, http
from odoo.http import request, Response
import json
import csv
import logging
import base64


class InventoryController(http.Controller):

    def total_quant(self, b):
        list = []
        sum = 0
        csv_data = base64.b64decode(b).decode("UTF-8")
        with open('D:\odoo\odoo\custom\inventory_controller\path\savefile.csv', 'w', encoding='utf-8') as csvFile:
            tmp = csv_data.replace('"', '')
            tmp_2 = tmp.replace('\n', '')
            csvFile.write(tmp_2)
            csvFile.close()
        with open('D:\odoo\odoo\custom\inventory_controller\path\savefile.csv', mode='r', encoding='utf-8') as file:
            data_read = csv.DictReader(file)
            for line in data_read:
                list.append(line)
            flag = list[0]['barcode']
            for i in list:
                if flag == list[i]['barcode']:
                    sum = flag['quantity'] + list[i]['quantity']
        return data_read, sum


    @http.route('/inventory_controller/all_products', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/inventory_controller/product/<string:rfid>', auth='public')
    def get_product_by_rfid(self, rfid, **kw):
        product_requests = http.request.env['product.template'].sudo().search([['x_RFID', '=', rfid]])
        vals = {
            "Product name": product_requests['name'],
            "Type of product": product_requests['detailed_type'],
            "Product code": product_requests['default_code'],
            "Description": product_requests['description'],
            "Description Sale": product_requests['description_sale'],
            "Price": product_requests['list_price'],
            "Invoice": product_requests['invoice_policy'],
        }
        return Response(json.dumps(vals))

    @http.route('/inventory_controller/product/get_quant/<string:rfid>', type='http', auth='public')
    def get_product_quantity_by_rfid(self, rfid, **kwargs):
        product_requests = http.request.env['product.template'].sudo().search([['x_RFID', '=', rfid]])
        product_quantity = http.request.env['stock.quant'].sudo().search([['product_id', '=', product_requests['id']]])
        for value in product_quantity:
            if value['quantity'] > 0:
                vals = {
                    "Product name": product_requests['name'],
                    "Product code": product_requests['default_code'],
                    "Expected quantity": value['quantity'],
                    "Actually quantity": value['inventory_quantity']
                }
                return Response(json.dumps(vals))

    @http.route('/inventory_controller/product/get_quant', type='json', auth='public')
    def get_multiple_product(self):
        request_data = json.loads(request.httprequest.data)
        if request_data is not None:
            rfid = request_data['rfid']
            value = []
            err_RFID = []
            for v in rfid:
                product_templ_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', v]])
                product_product_id = http.request.env['product.product'].sudo().search([['product_tmpl_id', '=', product_templ_id['id']]])
                stock_id = http.request.env['stock.quant'].sudo().search([["product_id", "=", product_product_id['id']]], limit=1)
                vals = {
                    "RFID": product_templ_id['x_RFID'],
                    "Product_name": product_templ_id['name'],
                    "Product_code": product_templ_id['default_code'],
                    "Price": product_templ_id['list_price'],
                    "Expected_quantity": stock_id['quantity'],
                    "Actually_quantity": stock_id['inventory_quantity'],
                }
                if vals['Product_name'] is not False:
                    value.append(vals)
                else:
                    err_RFID.append(v)
        return value, err_RFID


    @http.route('/inventory_controller/product/update_quant', auth='public', methods=['POST'], type='json', cors='*',
                csrf=False)
    def update_product_quantity(self, **kwargs):
        inventory_request = json.loads(request.httprequest.data)
        if inventory_request is not None:
            product_id = http.request.env['product.template'].sudo().search(
                [['x_RFID', '=', inventory_request['rfid']]])
            product_product_id = http.request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', product_id['id']), ('default_code', '=', inventory_request['code'])])
            stock_id = http.request.env['stock.quant'].sudo().search(
                [["product_id", "=", product_product_id['id']]])
            vals = {
                'inventory_quantity': inventory_request['quantity']
            }
            if stock_id['lot_id']:
                stock_id.sudo().write(vals)
                args = {
                    'message': 'success',
                    'success': True,
                    'data': {
                        'response': 200,
                        'data': stock_id
                    }
                }
                return args
            else:
                raise exceptions.ValidationError("Can not find lot/serial number")

    @http.route('/inventory_controller/test_update', auth='public', methods=['POST'], type='json', cors='*', csrf=False)
    def test_read_csv(self):
        request_data = json.loads(request.httprequest.data)
        if request_data is not None:
            data_get = base64.b64decode(request_data['base64']).decode("UTF-8")
            with open('D:\odoo\odoo\custom\inventory_controller\path\savefile.csv', 'w', encoding='utf-8') as csvFile:
                tmp = data_get.replace('"', '')
                tmp_2 = tmp.replace('\n', '')
                csvFile.write(tmp_2)
                csvFile.close()
            with open('D:\odoo\odoo\custom\inventory_controller\path\savefile.csv', mode='r', encoding='utf-8') as file:
                data_read = csv.DictReader(file)
                list = []
                quantity = 0
                for line in data_read:
                    list.append(line)
                for i in range(len(list)):
                    if i['barcode'] == i+1['barcode']:
                        # list[i]['barcode']['quantity'] += list[i+1]['quantity']
                        list.pop(i+1)
                print(list)
                # if list[0]['barcode'] == list[1]['barcode']:
                #     print(int(list[0]['quantity']) + int(list[1]['quantity']))
        #             rfid = line['rfid'],
        #             barcode = line['barcode'],
        #             product = line['product_name'],
        #             quantity = line['quantity'],
        #             product_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', rfid]])
        #             product_product_id = http.request.env['product.product'].sudo().search(
        #                 [('product_tmpl_id', '=', product_id['id'])])
        #             stock_id = http.request.env['stock.quant'].sudo().search([("product_id", "=", product_product_id['id'])])
        #             vals = {
        #                 'inventory_quantity': quantity[0]
        #             }
        #             for value in stock_id:
        #                 value.sudo().write(vals)
        #         return Response(json.dumps(json.dumps({
        #             "code": 201,
        #             "message": 'Successfully Update Product Quantity',
        #         })))
        # else:
        #     return exceptions.ValidationError("Can not find product input")



        # with open('D:\odoo\odoo\custom\inventory_controller\path\MOCK_DATA.csv', mode='r') as file:
        #     data_read = csv.DictReader(file)
        #     print(data_read)
        #     if data_read is not None:
        #         for line in data_read:
        #             rfid = line['rfid']
        #             code = line['code']
        #             quantity = line['quantity']
        #             serial_number = line['barcode']
        #             product_id = http.request.env['product.template'].sudo().search([['x_RFID', '=', rfid]])
        #             product_product_id = http.request.env['product.product'].sudo().search(
        #                 [('product_tmpl_id', '=', product_id['id']), ('default_code', '=', code)])
        #             stock_id = http.request.env['stock.quant'].sudo().search([("product_id", "=", product_product_id['id']), ("lot_id", "=", serial_number)])
        #             vals = {
        #                 'inventory_quantity': quantity
        #             }
        #             for value in stock_id:
        #                 value.sudo().write(vals)
        #         return Response(json.dumps({
        #             "code": 201,
        #             "message": 'Successfully Update Product Quantity',
        #         }))
        #     else:
        #         return exceptions.ValidationError("Can not find product input")
        #
