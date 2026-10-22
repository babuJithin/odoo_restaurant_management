from odoo.http import request
import json
from odoo import http
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
import itertools
import logging
from bs4 import BeautifulSoup
import re
import random
import os
_logger = logging.getLogger(__name__)
from odoo.tools.urls import urljoin as url_join
from odoo.http.session import authenticate


class Ecommerce_Api_V1(http.Controller):

    @http.route('/api/v1/getAppFeatures', methods=['POST'],type='jsonrpc',  auth='public', csrf=False)
    def getAppFeatures_v1(self, **kwargs):
        """Api to get configurations for Initialization"""

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ENV = request.env.user.sudo().company_id
        attachment_obj = request.env['ir.attachment'].sudo()

        color_configurations = request.env['color.info'].search_read([],['id','name','code','backend_config'])
        image_configurations = request.env['app.image.attachments'].search_read([],['id','name','image_type'])

        for color_configuration in color_configurations:
            if color_configuration['backend_config'] == 'toolbar_color':
                toolbar_color = color_configuration['code']
            if color_configuration['backend_config'] == 'menu_color':
                menu_color = color_configuration['code']
            if color_configuration['backend_config'] == 'button_color':
                button_color = color_configuration['code']
            if color_configuration['backend_config'] == 'background_color':
                background_color = color_configuration['code']

        for image_configuration in image_configurations:
            url=""
            attachment = attachment_obj.search(
                [('res_id', '=', image_configuration['id']), ('res_model', '=', 'app.image.attachments'),
                 ('res_field', '=', 'image_data')], limit=1)
            if attachment:
                access_token = attachment._generate_access_token()
                attachment.access_token = access_token
                url = url_join(base_url, 'web/content/%s?access_token=%s' % (attachment.id, attachment.access_token))
            if image_configuration['image_type'] == 'logo':
                logo = url
            if image_configuration['image_type'] == 'background':
                background_image = url
            if image_configuration['image_type'] == 'splash_screen':
                splash_screen_image = url


        return {

                "status": True,
                "message": "App Features ",
                "country_id":ENV.country_id.id,
                "country_name":ENV.country_id.name,
                "currecny_id":ENV.currency_id.id,
                "currecny_name": ENV.currency_id.name,
                "currecny_name": ENV.currency_id.name,
                "language": "en",
                "toolbar_color":toolbar_color,
                 "menu_color": menu_color,
                "button_color": button_color,
                "text_color": background_color,
                "logo": logo,
                "background_image": background_image,
                "splash_screen_image": splash_screen_image,

                }

    @http.route('/api/v1/create_customer', methods=['POST'], type='jsonrpc', auth='public', csrf=False)
    def create_customer_v1(self, **kwargs):
        """API TO ADD NEW USERS"""
        kwargs = http.request.get_json_data() or kwargs

        is_guest = kwargs.get('is_guest')
        if is_guest == "true":
            obj = request.env['res.users']
            guest_obj = request.env['guest.session']
            public_user = obj.get_res_user_public()
            guest_user = guest_obj.sudo().create({})
            session_id = "GUEST_SESSION_" + str(guest_user.id)
            guest_user.write({'session_id':session_id})

            return {'status': True, 'message': 'Guest session activated successfully',
                    "data": {'uid': guest_user.id, 'name': session_id, 'email': public_user.login,
                             'phone_number': public_user.phone_number or ""}}


        if not kwargs.get('name'):
            return {'status': False,
                               'message': 'Please enter name ',
                               }
        if not kwargs.get('email'):
            return {'status': False,
                               'message': 'Please enter  email',
                               }

        if not kwargs.get('password'):
            return {'status': False,
                               'message': 'Please enter  password'
                               }

        user = request.env['res.users'].sudo().search([('login', '=', kwargs.get('email'))]).exists()
        if user:
            return {'status': False,'message': 'Sorry, the email {0} is already registered. Please choose a different email address.'.format(kwargs.get('email'))}
        else:
            otp_registry = request.env['user.otp.registry'].sudo().search([('email', '=', kwargs.get('email'))],order='create_date DESC',limit=1)

            if otp_registry:
                if not kwargs.get('otp'):
                    otp = otp_registry.sudo().generate_otp()
                    otp_registry.write({'otp': otp})
                    otp_registry._action_send_signup_otp()
                    return {'status': True,
                            'message': 'Please enter the OTP send to {0} '.format(otp_registry.email)}
                if int(otp_registry.otp) == int(kwargs.get('otp')):
                    val = {'name': kwargs.get('name') or '', 'phone': kwargs.get('phone') or '',
                           'email': kwargs.get('email') or '',
                           }
                    company_ids = request.env['res.company'].sudo().search([])
                    try:
                        portal = request.env['res.users'].sudo().create(
                            {'phone_number': kwargs.get('phone'),
                             'login': kwargs.get('email'), 'name': kwargs.get('name'),
                             'password': kwargs.get('password'), 'sel_groups_1_9_10': 10})

                        portal.company_ids |= company_ids
                        portal.partner_id.sudo().write(val)

                        return {'status': True, 'message': 'Registered Successfully',
                                "data": {'uid': portal.id, 'name': portal.name, 'email': portal.login,
                                         'phone_number': portal.phone_number}}

                    except:
                        return {'status': False, 'message': 'Something Went Wrong Please Try Again'}

                else:
                    return {'status': False, 'message': 'Please enter valid OTP'}
            else:
                otp_registry = request.env['user.otp.registry'].sudo().create({'phone_number': kwargs.get('phone'),
                     'email': kwargs.get('email'),
                     'name': kwargs.get('name'),
                     })
                otp = otp_registry.sudo().generate_otp()
                otp_registry.write({'otp': otp})
                otp_registry._action_send_signup_otp()

                return {'status': True,
                        'message': 'Please enter the OTP send to {0} '.format(otp_registry.email)}


    @http.route('/api/v1/customer_login', methods=['POST'],type='jsonrpc', auth='public', csrf=False, cors='*')
    def customer_login_v1(self, **kwargs):
        kwargs = http.request.get_json_data() or kwargs
        _logger.info("parameters %s",kwargs)

        db = kwargs.get('db') or ''
        domain = []
        _logger.info("prameters <%s> ,  <%s>  , <%s>", kwargs.get('login'), kwargs.get('password'),kwargs.get('password'),kwargs.get('db'))
        if not kwargs.get('login'):
            return {'status': False,
                               'message': 'Please enter email address',
                               }
        if not kwargs.get('password'):
            return {'status': False,
                            'message': 'Please enter  password',
                               }

        user_id = request.env['res.users'].sudo().search([('login', '=', kwargs.get('login'))])
        _logger.info("parameters %s",kwargs)
        if user_id:
            try:
                credential = {'login': user_id.login, 'password': kwargs.get('password'), 'type': 'password'}
                uid = authenticate(request.session, request.env, credential)['uid']
                user = request.env['res.users'].sudo().search([('id', '=', int(uid))])

                return {'status': True,
                     'message': 'Logged in successfully',
                     "data": {'uid': user.id, 'phone': user.phone_number or '',
                              'name': user.name,
                              'email': user.partner_id.email or '',
                              }}
            except:
                return {'status': False, 'message': 'Wrong Credential',
                     }
        else:
            return {'status': False, 'message': 'Invalid Email Address',
                 }

    @http.route('/api/v1/forgotPassword', methods=['POST'], type="jsonrpc", auth='public', csrf=False)
    def forgotWebPassword_v2(self, **kwargs):
        kwargs = http.request.get_json_data() or kwargs
        email = kwargs.get('login')
        user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if not user:
            return {'status': False, 'message': 'Account is not registered.'}
        else:
            try:
                user._action_reset_password_ecommerce()
                return {'status': True, 'message': 'A password reset link has been sent to your email {0} '.format(user.login)}
            except:
                return {'status': False, 'message': 'Something Went Wrong',
                     }







