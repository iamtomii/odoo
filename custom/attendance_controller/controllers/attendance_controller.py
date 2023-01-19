# -*- coding: utf-8 -*-
from odoo import exceptions, http
from odoo.http import request, Response
import json
from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter
import socket
from pytz import timezone

from odoo.tools.json import JSON


class AttendanceController(http.Controller):

    @http.route('/attendance_controller/employee_all', auth='public', csrf=False)
    def index(self, **kw):
        employees_rec = http.request.env['hr.employee'].search([])
        output = "<h1>The list of employees: </h1><ul>"
        for employee in employees_rec:
            output += '<li>' + employee['name'] + '</li>' + '/<ul>'
        return output
    @http.route('/attendance_controller/employee-RFID-Exist/<string:rfid>', auth='public', type='http', csrf=False)
    def get_employee_by_rfid_exist(self, rfid, **kw):
        employee_rfid = http.request.env['hr.employee'].sudo().search([["x_EMPLOYEE_RFID", "=", rfid]])
        print(employee_rfid['id'])
        last_checkin = http.request.env['hr.attendance'].sudo().search([["employee_id", "=", employee_rfid.id]])
        print(last_checkin)
        if  len(last_checkin)!=0 and employee_rfid.name is not False:
            if last_checkin[0].check_in is not False and last_checkin[0].check_out is False:
                vals={
                    "signalexist": "exist",
                    "signalcheck":"checkout"

                }
            else:
                vals={
                    "signalexist": "exist",
                    "signalcheck": "checkin"

                }
        elif len(last_checkin)==0 and employee_rfid.name is not False:
            vals = {
                "signalexist": "exist",
                "signalcheck": "checkin"

            }
        else:
            vals={
                "signalexist":"not exist",
                "signalcheck":"can't check"
            }

        return Response(json.dumps(vals, ensure_ascii=False))
    # api get employee information
    @http.route('/attendance_controller/employee-RFID/<string:rfid>', auth='public', type='http', csrf=False)
    def get_employee_by_rfid(self, rfid, **kw):
        employee_rfid = http.request.env['hr.employee'].sudo().search([["x_EMPLOYEE_RFID", "=", rfid]])
        last_checkin = http.request.env['hr.attendance'].sudo().search([["employee_id", "=", employee_rfid['id']]])
        name = employee_rfid['name']
        department = http.request.env['hr.department'].sudo().search([["id", "=", int(employee_rfid['department_id'])]])
        if len(last_checkin) == 0:
            data = {
                "id": employee_rfid['id'],
                "name": name,
                "work phone": employee_rfid['work_phone'],
                "work email": employee_rfid['work_email'],
                "job": employee_rfid['job_title'],
                "department": department['name'],
                "avatar": str(employee_rfid['image_1920']),
            }
        elif len(last_checkin) < 2:
            data = {
                "id": employee_rfid['id'],
                "name": name,
                "work phone": employee_rfid['work_phone'],
                "work email": employee_rfid['work_email'],
                "job": employee_rfid['job_title'],
                "department": department['name'],
                "avatar": str(employee_rfid['image_1920']),
                "checkin": str(last_checkin[0]['check_in']),
                "checkin_image": str(last_checkin[0].checkin_image),
                "checkout": str(last_checkin[0].check_out),
                "checkout_image": str(last_checkin[0].check_out)
            }
        else:
            if not last_checkin[0].check_out:
                data = {
                    "id": employee_rfid['id'],
                    "name": name,
                    "work phone": employee_rfid['work_phone'],
                    "work email": employee_rfid['work_email'],
                    "job": employee_rfid['job_title'],
                    "department": department['name'],
                    "avatar": str(employee_rfid['image_1920']),
                    "last_checkout": str(last_checkin[1].check_out),
                    "last_checkout_image": str(last_checkin[1].checkout_image),
                    "checkin": str(last_checkin[0]['check_in']),
                    "checkin_image": str(last_checkin[0].checkin_image),
                }
            elif last_checkin[0].check_out is not False:
                data = {
                    "id": employee_rfid['id'],
                    "name": name,
                    "work phone": employee_rfid['work_phone'],
                    "work email": employee_rfid['work_email'],
                    "job": employee_rfid['job_title'],
                    "department": department['name'],
                    "avatar": str(employee_rfid['image_1920']),
                    "last_checkout": str(last_checkin[1].check_out),
                    "last_checkout_image": str(last_checkin[1].checkout_image),
                    "checkin": str(last_checkin[0]['check_in']),
                    "checkin_image": str(last_checkin[0].checkin_image),
                }
            else:
                data = {
                    "id": employee_rfid['id'],
                    "name": name,
                    "work phone": employee_rfid['work_phone'],
                    "work email": employee_rfid['work_email'],
                    "job": employee_rfid['job_title'],
                    "department": department['name'],
                    "avatar": str(employee_rfid['image_1920']),
                    "last_checkin": str(last_checkin[1]['check_in']),
                    "last_checkin_image": str(last_checkin[1].checkin_image),
                    "last_checkout": str(last_checkin[1].check_out),
                    "last_checkout_image": str(last_checkin[1].checkout_image),
                    "checkin": str(last_checkin[0]['check_in']),
                    "checkin_image": str(last_checkin[0].checkin_image),
                    "checkout": str(last_checkin[0].check_out),
                    "checkout_image": str(last_checkin[0].check_out)
                }
        return Response(json.dumps(data, ensure_ascii=False))

    # api checkin
    @http.route('/attendance_controller/employee-checkin', type='json', auth='public',
                methods=['POST'], cors='*', csrf=False)
    def get_employee_checkin(self, **rec):
        print("checkin")
        employee_request = json.loads(request.httprequest.data)
        if employee_request is not None:
            employee_rfid = http.request.env['hr.employee'].sudo().search([["x_EMPLOYEE_RFID", "=", employee_request['rfid']]])
            print(employee_rfid['gender'])
            image_request = employee_request['image']
            checkin_request = employee_request['checkin_time']
            if employee_request['rfid'] == " ":
                raise exceptions.ValidationError("RFID is empty")
            if employee_rfid:
                vals = {
                    'employee_id': employee_rfid['id'],
                    'check_in': str(checkin_request),
                    'checkin_image': str(image_request),
                }
                employee_attendance = http.request.env['hr.attendance'].sudo().create(vals)
                return {
                    "code": 201,
                    "message": 'Successfully Check-in',
                    'check in image': str(image_request),
                    "gender": employee_rfid['gender']
                }
            else:
                raise exceptions.ValidationError("Can not find employee")
        else:
            raise exceptions.ValidationError('Invalid Employee Input')

    # api checkout

    @http.route('/attendance_controller/employee-checkout', type='json', auth='public', methods=['POST'], cors='*',
                csrf=False)
    def get_employee_checkout(self, **rec):
        employee_request = json.loads(request.httprequest.data)
        if employee_request is not None:
            # print(str(employee_request['image']))
            # print(employee_request['checkout_time'])
            employee_rfid = http.request.env['hr.employee'].sudo().search([["x_EMPLOYEE_RFID", "=", employee_request['rfid']]])
            if employee_rfid:
                employee_id = employee_rfid['id']
                employee_attendance = http.request.env['hr.attendance'].sudo().search(
                    [("employee_id", "=", employee_id), ("check_out", '=', False)], order='check_in desc')
                if not employee_attendance:
                    raise exceptions.ValidationError("Employee already checked-out or has not checked-in yet")
                else:
                    flag = employee_attendance[0]
                    if flag is not None:
                        vals = {
                            'check_out': str(employee_request['checkout_time']),
                            'checkout_image': str(employee_request['image'])
                        }
                        if not flag['check_out']:
                            flag.sudo().write(vals)
                            return {
                                "code": 201,
                                "message": 'Successfully Check-out',
                                'time checkout': str(employee_request['checkout_time']),
                                'checkout image': employee_request['image'],
                                "gender": employee_rfid['gender']

                            }
                        else:
                            raise exceptions.ValidationError("Employee is already checked-out")
            else:
                raise exceptions.ValidationError("Can not find employee")
        else:
            raise exceptions.ValidationError("Invalid Employee Input")
    @http.route('/attendance_controller/create_new_hr_employee', type='json', auth='public', methods=['POST'], cors='*',
                csrf=False)
    def create_new_hr_employee(self, **rec):
        employee_request = json.loads(request.httprequest.data)
        if employee_request is not None:
            id=employee_request["id"]
            rfid=employee_request["rfid"]
            employee_info = http.request.env['hr.employee'].sudo().search([["pin", "=", id]])
            if not employee_info:
                raise exceptions.ValidationError("ID does not exist")
            else:
                if employee_info['x_EMPLOYEE_RFID'] is not False:
                    raise exceptions.ValidationError("EMPLOYEE HAVE RFID")
                else:
                    vals = {
                        "x_EMPLOYEE_RFID": rfid
                    }
                    employee_info.sudo().write(vals)
                    return {
                        "code": 201,
                        "message": 'Successfully',
                        "name": employee_info['name']
                    }

        else:
            raise exceptions.ValidationError("Invalid Employee Input")

    @http.route('/attendance_controller/show_information_employee_by_id/<string:id>',auth='public',type='http',csrf=False)
    def show_information_employee_by_id(self,id,**aw):
        employee_info = http.request.env['hr.employee'].sudo().search([["pin", "=", id]])
        department = http.request.env['hr.department'].sudo().search([["id", "=", int(employee_info['department_id'])]])
        if not employee_info:
            vals = {
                "code": "ID is not exist",
                "name":"false",
                "ID":"false",
                "department":"false",
                "avatar":"false",
                "phone":"false",

            }
        else:
                if employee_info['x_EMPLOYEE_RFID'] is not False:
                    vals = {
                        "code": "Employee had RFID ",
                        "name": "false",
                        "ID": "false",
                        "department": "false",
                        "avatar": "false",
                        "phone":"false",

                        }
                else:
                    vals = {
                        "code": "ok",
                        "name":employee_info['name'],
                        "ID":employee_info['id'],
                        "department":department['name'],
                        "avatar": str(employee_info['image_1920']),
                        "phone":employee_info['work_phone'],

                    }

        return Response(json.dumps(vals, ensure_ascii=False))
    @http.route('/attendence_controller/update_checkout', type='json', auth='public', methods=['POST'], cors='*',
                csrf=False)
    def Update_checkout(self,**rec):
        data_request=json.loads(request.httprequest.data)
        if data_request is not None:
            employee_rfid = http.request.env['hr.employee'].sudo().search([["x_EMPLOYEE_RFID", "=", data_request['rfid']]])
            if employee_rfid:
                employee_id = employee_rfid['id']
                employee_attendance = http.request.env['hr.attendance'].sudo().search(
                    [["employee_id", "=", employee_id]])
                print(employee_attendance[0]['check_out'])
                vals={
                    'check_out': str(data_request['checkout_time']),
                    'checkout_image': str(data_request['image'])
                }
                employee_attendance[0].sudo().write(vals)
                return {
                    "code": 201,
                    "message": 'Successfully Check-out',
                    'time checkout': str(data_request['checkout_time']),
                    'checkout image': data_request['image'],
                    "gender": employee_rfid['gender']

                }
            else:
                raise exceptions.ValidationError("Can not find employee")
        else:
            raise exceptions.ValidationError("Invalid Employee Input")
