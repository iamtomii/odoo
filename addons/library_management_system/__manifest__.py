# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
{
    'name': 'Library Management System',
    'version': '15.0.1.1.1',
    'summary': 'A Module for managing libraries.',
    'description': 'A Module for managing libraries.',
    'category': 'Industries',
    'author': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['mail', 'product', 'contacts', 'account', 'stock', 'sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/book_view.xml',
        'views/member_view.xml',
        'views/register_view.xml',
        'views/res_config_view.xml',
        'views/awards.xml',
        'views/membership_view.xml',
        'views/author_view.xml',
        'views/action_manager.xml',
        'views/publisher_view.xml',
        'wizard/renew_membership_views.xml',
        'wizard/import_book_views.xml',
        'wizard/create_book_views.xml',
        'wizard/issued_book.xml',
        'wizard/member_report.xml',
        'wizard/book_report.xml',
        'data/data.xml',
        'reports/membership_card.xml',
        'reports/book_barcode.xml',
        'reports/issued_book_report.xml',
        'reports/member_report_tmpl.xml',
        'reports/book_report_tmpl.xml',
    ],

    'assets': {
        'web.assets_backend': [
                'library_management_system/static/src/js/action_manager.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 99,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}
