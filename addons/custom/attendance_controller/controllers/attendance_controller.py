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

    # api get employee information
    @http.route('/attendance_controller/employee-RFID/<string:rfid>', auth='public', type='http', csrf=False)
    def get_employee_by_rfid(self, rfid, **kw):
        employee_rfid = http.request.env['hr.employee'].sudo().search([["x_RFID", "=", rfid]])
        last_checkin = http.request.env['hr.attendance'].sudo().search([["employee_id", "=", employee_rfid['id']]])
        name = employee_rfid['name']
        department = http.request.env['hr.department'].sudo().search([["id", "=", int(employee_rfid['department_id'])]])
        if len(last_checkin) == 0:
            print("1")
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
            print("2")
            data = {
                "id": employee_rfid['id'],
                "name": name,
                "work phone": employee_rfid['work_phone'],
                "work email": employee_rfid['work_email'],
                "job": employee_rfid['job_title'],
                "department": department['name'],
                "avatar": str(employee_rfid['image_1920']),
                "last_checkin": str(last_checkin[0]['check_in']),
                "last_checkin_image": str(last_checkin[0].checkin_image),
                "last_checkout": str(last_checkin[0].check_out),
                "last_checkout_image": str(last_checkin[0].checkout_image),
            }
        else:
            if not last_checkin[0].check_out:
                print("3")

                data = {
                    "id": employee_rfid['id'],
                    "name": name,
                    "work phone": employee_rfid['work_phone'],
                    "work email": employee_rfid['work_email'],
                    "job": employee_rfid['job_title'],
                    "department": department['name'],
                    "avatar": str(employee_rfid['image_1920']),
                    "last_checkin": str(last_checkin[0]['check_in']),
                    "last_checkin_image": str(last_checkin[0].checkin_image),
                    "last_checkout": str(last_checkin[1].check_out),
                    "last_checkout_image": str(last_checkin[1].checkout_image),
                }
            elif last_checkin[0].check_out is not False:
                print("4")

                data = {
                    "id": employee_rfid['id'],
                    "name": name,
                    "work phone": employee_rfid['work_phone'],
                    "work email": employee_rfid['work_email'],
                    "job": employee_rfid['job_title'],
                    "department": department['name'],
                    "avatar": str(employee_rfid['image_1920']),
                    "last_checkin": str(last_checkin[0]['check_in']),
                    "last_checkin_image": str(last_checkin[0].checkin_image),
                    "last_checkout": str(last_checkin[1].check_out),
                    "last_checkout_image": str(last_checkin[1].checkout_image),
                }
            else:
                print("5")

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
                }
        return Response(json.dumps(data, ensure_ascii=False))

    # api checkin
    @http.route('/attendance_controller/employee-checkin', type='json', auth='public',
                methods=['POST'], cors='*', csrf=False)
    def get_employee_checkin(self, **rec):
        employee_request = json.loads(request.httprequest.data)
        if employee_request is not None:
            employee_rfid = http.request.env['hr.employee'].sudo().search([["x_RFID", "=", employee_request['rfid']]])
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
            employee_rfid = http.request.env['hr.employee'].sudo().search([["x_RFID", "=", employee_request['rfid']]])
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
                                'checkout image': employee_request['image']
                            }
                        else:
                            raise exceptions.ValidationError("Employee is already checked-out")
            else:
                raise exceptions.ValidationError("Can not find employee")
        else:
            raise exceptions.ValidationError("Invalid Employee Input")
