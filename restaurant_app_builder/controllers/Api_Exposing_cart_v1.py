from odoo.http import request
import json
from odoo import http
from odoo import models, fields, api, _
from datetime import datetime
import ast
from odoo.http import Controller, request, route
import pytz
import logging
import itertools

_logger = logging.getLogger(__name__)


class Api_Exposing_Cartv1(http.Controller):



    @http.route('/api/v1/cart/summary', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def cart_summary_v1(self, **data):
        data = http.request.get_json_data() or data
        is_guest = data.get('is_guest')
        if is_guest == "true":
            guest_user = request.env['guest.session'].sudo().search([('id', '=', int(data.get('uid')))])
            if guest_user:
                public_user = request.env['res.users'].sudo().get_res_user_public()
                customer_id = public_user.partner_id.id
            else:
                return ({'status': False, 'message': 'You are not a Valid user'})
        else:
            customer_id = request.env['res.users'].sudo().search([('id', '=', int(data.get('uid')))]).partner_id.id
        if not customer_id:
            guest_user = request.env['custom.guest.session'].sudo().search(
                [('id_unique', '=', int(data.get('uid')))])
            if guest_user:
                public_user = request.env['res.users'].get_res_user_public()
                customer_id = public_user.partner_id.id
        if customer_id:
            carts_info_check = request.env['sale.order'].sudo().search(
                [('partner_id', '=', customer_id), ('cart_chekouted', '=', False),
                 ('state', '=', 'draft')])
            if not carts_info_check:
                return ({'status': False, 'message': 'Cant find a cart for customer with given Id', 'id_code': 404})
            try:
                carts1 = request.env['sale.order'].sudo().search_read(
                    [('partner_id', '=', customer_id), ('cart_chekouted', '=', False),
                     ('state', '=', 'draft')],
                    ['order_line', 'amount_total', 'name'])
                carts2 = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', customer_id), ('cart_chekouted', '=', False),
                     ('state', '=', 'draft')],
                )
                if carts2:
                    try:
                        cart_lines = request.env['sale.order.line'].sudo().search(
                            [('order_id', '=', carts2[0]['id'])])
                    except:
                        return ({'status': False, 'message': 'Please Pass Correct Valuessss', 'id_code': 404})
                cart_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', carts2[0]['id'])])
                cart_lines_info = []
                for x in cart_lines:
                    carts_info = {
                        'id': x.id or 0,
                        'product_type_id': x.product_id.id or 0,
                        'product_name': x.product_id.display_name or "",
                        'product_id': x.product_id.product_tmpl_id.id or 0,
                        'quantity': x.product_uom_qty or 0,
                        'qes_quantity': x.product_uom_qty,
                        "max_allowed_qty": x.product_id.virtual_available if x.product_id.virtual_available > 0.0 else 0.0,
                        "product_uom": x.product_id.uom_id.name if x.product_id.uom_id else "",
                        "product_uom_id": x.product_id.uom_id.id if x.product_id.uom_id else 0,
                        'max_product_qty': 0,
                        'product_packaging': [],
                        'price': round(x.price_unit, 2) or 0,
                        'delivery_methods': [],
                        "image": "http://" + str(
                            http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                            x.product_id.product_tmpl_id.id) if x.product_id.product_tmpl_id.image_1920 else "False",
                        'sub_total': round(x.price_subtotal, 2) or 0,
                        "product_note": x.product_id.product_tmpl_id.product_note or "",
                    }
                    cart_lines_info.append(carts_info)
                return (
                    {'status': True, 'message': 'Your Cart Summary Details:', 'cart': carts1,
                     'lines': cart_lines_info} if carts1 else {'status': False,
                                                               'message': 'Your Cart Is Empty',
                                                               'cart': carts1,
                                                               'lines': cart_lines_info})
            except:
                return ({'status': False, 'message': 'Please Pass Correct Valuesyyy', 'id_code': 404})
        else:
            return ({'status': False, 'message': 'Your Cusomer id dont exist', 'id_code': 404})


    
    @http.route('/api/v1/cart/view', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def cart_view_v1(self, **data):
        data = http.request.get_json_data() or data
        is_guest = data.get('is_guest')
        if is_guest == "true":
            guest_user = request.env['guest.session'].sudo().search([('id', '=', int(data.get('uid')))])
            if guest_user:
                public_user = request.env['res.users'].sudo().get_res_user_public()
                customer_id = public_user.partner_id.id
            else:
                return ({'status': False, 'message': 'You are not a Valid user'})
        else:
            customer_id = request.env['res.users'].sudo().search([('id', '=', int(data.get('uid')))]).partner_id.id
        if not customer_id:
            guest_user = request.env['custom.guest.session'].sudo().search(
                [('id_unique', '=', int(data.get('uid')))])
            if guest_user:
                public_user = request.env['res.users'].get_res_user_public()
                customer_id = public_user.partner_id.id
        if customer_id:
            try:
                carts1 = request.env['sale.order'].sudo().search(
                    [('id', '=', int(data.get('cart_id'))), ('partner_id', '=', customer_id),
                     ('cart_chekouted', '=', False),
                     ('state', '=', 'draft')])
                live_cart_info = []
                live_carts = {
                    "id": carts1.id,
                    "name": carts1.name,
                    "order_line": [carts_lines.id for carts_lines in carts1.order_line if carts1.order_line],
                    "amount_without_discount": round(carts1.amount_undiscounted, 2),
                    "amount_total": round(carts1.amount_total, 2),
                }
                live_cart_info.append(live_carts)
                carts2 = request.env['sale.order'].sudo().search(
                    [('id', '=', int(data.get('cart_id'))), ('partner_id', '=', customer_id),
                     ('cart_chekouted', '=', False),
                     ('state', '=', 'draft')],
                )

                try:
                    cart_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', carts2[0]['id'])])
                    cart_lines_info = []
                    for x in cart_lines:
                        live_carts['amount_without_discount'] = live_carts[
                            'amount_without_discount']
                        live_carts['amount_total'] = live_carts['amount_total']
                        carts_info = {
                            'id': x.id or 0,
                            'product_type_id': x.product_id.id or 0,
                            'product_name': x.product_id.display_name or "",
                            'product_id': x.product_id.product_tmpl_id.id or 0,
                            "brand": x.product_id.brand_id.name or "",
                            'quantity': x.product_uom_qty or 0,
                            'qes_quantity': x.product_uom_qty or 0,
                            "max_allowed_qty": x.product_id.virtual_available if x.product_id.virtual_available > 0.0 else 0.0,
                            "product_uom": x.product_id.uom_id.name if x.product_id.uom_id else "",
                            "product_uom_id": x.product_id.uom_id.id if x.product_id.uom_id else 0,
                            'inventory_availability': "always",
                            'price': x.product_id.list_price or 0,
                            'delivery_methods': [],
                            "image": "http://" + str(
                                http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                                x.product_id.product_tmpl_id.id) if x.product_id.product_tmpl_id.image_1920 else "False",
                            'sub_total': round(x.price_subtotal, 2),
                            "product_note": x.product_id.product_tmpl_id.product_note or "",
                        }

                        cart_lines_info.append(carts_info)
                    return (
                        {'status': True, 'message': 'Your Cart Summary Details:', 'cart': live_cart_info,
                         'lines': cart_lines_info} if len(cart_lines) > 0 else {'status': False,
                                                                                'message': 'Your Cart Is Empty',
                                                                                'cart': live_cart_info,
                                                                                'lines': cart_lines_info})
                except Exception as e:
                    return ({'status': False, 'message': 'Please Pass Correct Cart info', 'id_code': 404})
            except Exception as e:
                return ({'status': False, 'message': 'Please Pass Correct Cart info', 'id_code': 404})
        else:
            return ({'status': False, 'message': 'Please Pass Correct Customer Id', 'id_code': 404})




    
    # add cart create seperate api   pass product ID uom ID and quantity in product info dictionary
    @http.route('/api/v1/cart/create', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def cart_live_create_v1(self, **data):
        data = http.request.get_json_data() or data
        guest_user = request.env['guest.session']
        is_guest = data.get('is_guest')
        if  is_guest == "true":
            guest_user = request.env['guest.session'].sudo().search([('id', '=', int(data.get('uid')))])
            if guest_user:
                public_user = request.env['res.users'].sudo().get_res_user_public()
                customer_id = public_user.partner_id.id
            else:
                return ({'status': False, 'message': 'You are not a Valid user'})
        else:
            customer_id = request.env['res.users'].sudo().search([('id', '=', int(data.get('uid')))]).partner_id.id
        if customer_id:
            try:
                if not data.get('cart_id') and not data.get('line_id'):
                    cart_line = []
                    for i in data.get('products_info'):
                        product = request.env['product.product'].sudo().search(
                            [('id', '=', int(i.get('product_type_id')))])
                        product_id = product
                        if product:
                            product_id = product
                            if i.get('package_id'):
                                package_id = request.env['product.packaging'].sudo().search(
                                    [('id', '=', int(i.get('package_id')))])
                                if package_id:
                                    cart_line.append((0, 0,
                                                      {'product_id': product_id.id,
                                                       'product_uom_qty': i.get('quantity'),
                                                      }))
                                else:
                                    cart_line.append((0, 0,
                                                      {'product_id': product_id.id,
                                                       'product_uom_qty': i.get('quantity')}))
                            else:
                                cart_line.append((0, 0,
                                                  {'product_id': product_id.id,
                                                   'product_uom_qty': i.get('quantity')}))

                        else:
                            return {"status": False, "message": "Please pass Product Variant ID"}
                    try:
                        location_id = int(data.get('location_id'))
                    except:
                        location_id = False
                    carts_info_check = request.env['sale.order'].sudo().search(
                        [('partner_id', '=', customer_id),
                         ('state', '=', 'draft'), ('cart_chekouted', '=', False)], limit=1)
                    if carts_info_check:
                        cart = carts_info_check
                        cart.sudo().write(
                            {'partner_id': customer_id, 'order_line': cart_line, 'state': 'draft',
                             })
                    else:
                        cart = request.env['sale.order'].sudo().create(
                            {'partner_id': customer_id, 'order_line': cart_line, 'state': 'draft',
                             })
                    if guest_user:
                        cart.sudo().write({'guest_checkout':True,'guest_user_id':guest_user.id})
                    if cart:
                        cart_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', cart[0]['id'])])
                        cart_lines_info = []
                        cart_info = []
                        cart_line_list=[]
                        for x in cart_lines:
                            cart_line_list.append(x.id or 0)
                            carts_info = {
                                'id': x.id or 0,
                                'product_type_id': x.product_id.id or 0,
                                'product_name': x.product_id.display_name or "",
                                'product_id': x.product_id.product_tmpl_id.id or 0,
                                'quantity': x.product_uom_qty or 0,
                                'qes_quantity': x.product_uom_qty or 0,
                                'inventory_availability':  "always",
                                'price': x.product_id.list_price or 0,
                                'delivery_methods': [],
                                'image':  "http://" + str(
                                    http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                                    x.product_id.product_tmpl_id.id) if x.product_id.product_tmpl_id.image_1920 else "False",
                                'sub_total': round(x.price_subtotal, 2),
                                "product_note":x.product_id.product_tmpl_id.product_note or "",

                            }


                            cart_lines_info.append(carts_info)
                        cart_info_dict = {
                            'id':cart.id,
                            "order_line": cart_line_list,
                            'amount_total': cart.amount_total,
                            'name': cart.name,
                        }
                        cart_info.append(cart_info_dict)
                        return ({'status': True, 'message': 'Cart Created Successfully','cart':cart_info,
                                 'lines': cart_lines_info})
                    else:
                        return ({'status': False, 'message': 'Please pass correct values for the cart creation'})
            except Exception as e:
                _logger.info("enterd in Exception  %s" % str(e))
                return ({'status': False, 'message': 'Please Pass Correct Info', "err": str(e)})

        else:
            return ({'status': False, 'message': 'You are not a Valid user'})
        
    @http.route('/api/v1/cart/update', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def cart_update_v3(self, **data):
        data = http.request.get_json_data() or data
        guest_user = request.env['guest.session']
        is_guest = data.get('is_guest')
        if is_guest == "true":
            guest_user = request.env['guest.session'].sudo().search([('id', '=', int(data.get('uid')))])
            if guest_user:
                public_user = request.env['res.users'].sudo().get_res_user_public()
                customer_id = public_user.partner_id.id
            else:
                return ({'status': False, 'message': 'You are not a Valid user'})
        else:
            customer_id = request.env['res.users'].sudo().search([('id', '=', int(data.get('uid')))]).partner_id.id
        if data.get('cart_id'):
            carts_id = request.env['sale.order'].sudo().search(
                [('id', '=', int(data.get('cart_id'))), ('partner_id', '=', customer_id),('cart_chekouted', '=',False),
                 ('state', '=', 'draft')])
        if customer_id:
            try:
                if data.get('line_id'):
                    if data.get('quantity') != 0:
                        rec = request.env['sale.order.line'].sudo().search([('id', '=', int(data.get('line_id')))])

                        if rec:
                            rec.write(
                                {'product_uom_qty': float(data.get('quantity'))})
                            cart_id = rec.order_id.id
                            carts = request.env['sale.order'].sudo().search_read(
                                [('id', '=', cart_id), ('partner_id', '=', customer_id), ('state', '=', 'draft'),('cart_chekouted', '=',False)],
                                ['order_line','amount_undiscounted', 'amount_total'])

                            cart_lines = request.env['sale.order.line'].sudo().search(
                                [('order_id', '=', carts[0]['id'])])
                            cart_lines_info = []
                            for x in cart_lines:
                                carts_info = {
                                    'id': x.id or 0,
                                    'product_type_id': x.product_id.id or 0,
                                    'product_name': x.product_id.display_name or "",
                                    'product_id': x.product_id.product_tmpl_id.id or 0,
                                    'quantity': x.product_uom_qty or 0,
                                    'qes_quantity': x.product_uom_qty or 0,
                                    "max_allowed_qty": x.product_id.virtual_available if x.product_id.virtual_available > 0.0 else 0.0,
                                    "product_uom": x.product_id.uom_id.name if x.product_id.uom_id else "",
                                    "product_uom_id": x.product_id.uom_id.id if x.product_id.uom_id else 0,
                                    'inventory_availability':  "always",
                                    'price': x.product_id.list_price or 0,
                                    'image':  "http://" + str(
                                            http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                                            x.product_id.product_tmpl_id.id) if x.product_id.product_tmpl_id.image_1920 else "False",
                                    'sub_total': round(x.price_subtotal, 2),
                                    "product_note": x.product_id.product_tmpl_id.product_note or "",

                                }


                                cart_lines_info.append(carts_info)
                            if carts:
                                return ({'status': True, 'message': 'Quantity updation is done', 'cart': carts,
                                         'lines': cart_lines_info})
                            else:
                                return (
                                {'status': False, 'message': 'Please pass correct values for cart quantity updation',
                                 'cart': carts, 'lines': cart_lines_info, 'id_code': 404})
                        else:
                            return ({'status': False, 'message': 'Please pass correct values for the cart updation',
                                     'id_code': 404})

                    else:
                        line = request.env['sale.order.line'].sudo().search([('id', '=', int(data.get('line_id')))])
                        cart_id = line.order_id.id
                        carts = request.env['sale.order'].sudo().search_read(
                            [('id', '=', cart_id), ('partner_id', '=', customer_id), ('state', '=', 'draft'),('cart_chekouted', '=',False)],
                            ['order_line', 'amount_total'])
                        if line:
                            if carts:
                                line.unlink()
                                carts = request.env['sale.order'].sudo().search_read(
                                    [('id', '=', cart_id), ('partner_id', '=', customer_id), ('state', '=', 'draft'),('cart_chekouted', '=',False)],
                                    ['order_line', 'amount_total'])

                                cart_lines = request.env['sale.order.line'].sudo().search(
                                    [('order_id', '=', carts[0]['id'])])
                                cart_lines_info = []
                                for x in cart_lines:
                                    carts_info = {
                                        'id': x.id or 0,
                                        'product_type_id': x.product_id.id or 0,
                                        'product_name': x.product_id.display_name or "",
                                        'product_id': x.product_id.product_tmpl_id.id or 0,
                                        'quantity': x.product_uom_qty or 0,
                                        'qes_quantity': x.product_uom_qty or 0,
                                        "max_allowed_qty": x.product_id.virtual_available if x.product_id.virtual_available > 0.0 else 0.0,
                                        "product_uom": x.product_id.uom_id.name if x.product_id.uom_id else "",
                                        "product_uom_id": x.product_id.uom_id.id if x.product_id.uom_id else 0,
                                        'inventory_availability': "always",
                                        'price': x.product_id.list_price or 0,
                                        'image': "http://" + str(
                                                http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                                                x.product_id.product_tmpl_id.id) if x.product_id.product_tmpl_id.image_1920 else "False",
                                        'sub_total': round(x.price_subtotal, 2),
                                        "product_note": x.product_id.product_tmpl_id.product_note or "",
                                    }


                                    cart_lines_info.append(carts_info)

                                return ({'status': True, 'message': 'Quantity removed', 'cart': carts,
                                         'lines': cart_lines_info})
                            else:
                                return ({'status': False, 'message': 'Please pass correct Line Info', 'id_code': 404})
                        else:
                            try:
                                cart_lines = request.env['sale.order.line'].sudo().search(
                                    [('order_id', '=', carts[0]['id'])])
                                cart_lines_info = []
                                for x in cart_lines:
                                    carts_info = {
                                        'id': x.id or 0,
                                        'product_type_id': x.product_id.id or 0,
                                        'product_name': x.product_id.display_name or "",
                                        'product_id': x.product_id.product_tmpl_id.id or 0,
                                        'quantity': x.product_uom_qty or 0,
                                        'qes_quantity': x.product_uom_qty or 0,
                                        "max_allowed_qty": x.product_id.virtual_available if x.product_id.virtual_available > 0.0 else 0.0,
                                        "product_uom": x.product_id.uom_id.name if x.product_id.uom_id else "",
                                        "product_uom_id": x.product_id.uom_id.id if x.product_id.uom_id else 0,
                                        'inventory_availability': "always",
                                        'price': x.product_id.list_price or 0,
                                        'image': "http://" + str(
                                            http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                                            x.product_id.product_tmpl_id.id) if x.product_id.product_tmpl_id.image_1920 else "False",
                                        'sub_total': round(x.price_subtotal, 2),
                                        "product_note": x.product_id.product_tmpl_id.product_note or "",
                                    }


                                    cart_lines_info.append(carts_info)
                                return ({'status': False, 'message': 'Please pass correct lineID for quantity remove',
                                         'cart': carts, 'lines': cart_lines_info})
                            except:
                                return ({'status': False, 'message': 'Please pass correct Line Info', 'id_code': 404})



                else:
                    if data.get('cart_id'):
                        cart_line = []
                        rec = request.env['sale.order'].sudo().search(
                            [('id', '=', int(data.get('cart_id'))), ('partner_id', '=', customer_id),('cart_chekouted', '=',False),
                             ('state', '=', 'draft')])
                        for i in data.get('products_info'):

                            product = request.env['product.product'].sudo().search(
                                [('id', '=', int(i.get('product_type_id')))])
                            product_id = product
                            if product.id not in rec.order_line.mapped('product_id').ids:
                                if i.get('package_id'):
                                    package_id = request.env['product.packaging'].sudo().search(
                                        [('id', '=', int(i.get('package_id')))])
                                    if package_id:
                                        cart_line.append((0, 0,
                                                          {'product_id': product_id.id,
                                                           'product_uom_qty': float(i.get('quantity')),
                                                           }))
                                    else:
                                        cart_line.append((0, 0,
                                                          {'product_id': product_id.id,

                                                           'product_uom_qty': i.get('quantity')}))
                                else:
                                    cart_line.append((0, 0,
                                                      {'product_id': product_id.id,
                                                       'product_uom_qty': float(i.get('quantity'))}))

                        rec = request.env['sale.order'].sudo().search(
                            [('id', '=', int(data.get('cart_id'))), ('partner_id', '=', customer_id),('cart_chekouted', '=',False),
                             ('state', '=', 'draft')])
                        if rec:
                            rec.write({'order_line': cart_line})

                            recs = request.env['sale.order'].sudo().search_read(
                                [('id', '=', rec.id), ('partner_id', '=', customer_id), ('state', '=', 'draft'),('cart_chekouted', '=',False)],
                                ['order_line', 'amount_total']
                            )

                            cart_lines = request.env['sale.order.line'].sudo().search(
                                [('order_id', '=', recs[0]['id'])])
                            cart_lines_info = []
                            for x in cart_lines:
                                carts_info = {
                                    'id': x.id or 0,
                                    'product_type_id': x.product_id.id or 0,
                                    'product_name': x.product_id.display_name or "",
                                    'product_id': x.product_id.product_tmpl_id.id or 0,
                                    'quantity': x.product_uom_qty or 0,
                                    'qes_quantity': x.product_uom_qty or 0,
                                    "max_allowed_qty": x.product_id.virtual_available if x.product_id.virtual_available > 0.0 else 0.0,
                                    "product_uom": x.product_id.uom_id.name if x.product_id.uom_id else "",
                                    "product_uom_id": x.product_id.uom_id.id if x.product_id.uom_id else 0,
                                    'inventory_availability': "always",
                                    'price': x.product_id.list_price or 0,
                                    'image': "http://" + str(
                                                http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                                                x.product_id.product_tmpl_id.id) if x.product_id.product_tmpl_id.image_1920 else "False",
                                    'sub_total': round(x.price_subtotal, 2),
                                    "product_note": x.product_id.product_tmpl_id.product_note or "",
                                }


                                cart_lines_info.append(carts_info)

                            return ({'status': True, 'message': 'Cart Updated Successfully', 'cart': recs,
                                     'lines': cart_lines_info})
                        else:
                            rec = request.env['sale.order'].sudo().search(
                                [('partner_id', '=', customer_id),
                                 ('state', '=', 'draft')])
                            return ({'status': False, 'message': 'Please pass Correct cartID for the updation',
                                     'cart_id': rec[0].id if len(rec) > 0 else 0, 'id_code': 404})
                    else:
                        return ({'status': False, 'message': 'Please pass cartID for the updation'})

            except Exception as e:
                return ({'status': False, 'message': 'Please Pass Correct Info', 'id_code': 404,'error':str(e),'cart_id':carts_id.id})
        else:
            return ({'status': False, 'message': 'You are not a Valid user'})

    @http.route('/api/v1/cart/delete', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def cart_delete_v1(self,**kwargs):
        kwargs = http.request.get_json_data() or kwargs
        is_guest = kwargs.get('is_guest')
        if is_guest == "true":
            guest_user = request.env['guest.session'].sudo().search([('id', '=', int(kwargs.get('uid')))])
            if guest_user:
                public_user = request.env['res.users'].sudo().get_res_user_public()
                customer_id = public_user.partner_id.id
            else:
                return ({'status': False, 'message': 'You are not a Valid user'})
        else:
            customer_id = request.env['res.users'].sudo().search([('id', '=', kwargs.get('uid'))]).partner_id.id
        if customer_id:
            cart = request.env['sale.order'].sudo().search(
                [('state', '=', 'draft'),('partner_id', '=', customer_id), ('id', '=', int(kwargs.get('cart_id')))])
            print("cart",cart)
            if cart:
                cart.mark_deleted()
                return ({'status': True, 'message': 'Cart Deleted Successfully'})
            else:
                return ({'status': False, 'message': 'Invalid Cart ID or Cart Not Found'})

        else:
            return ({'status': False, 'message': 'You are not a Valid user'})
        
    # Cart list is starting from here
    @http.route('/api/v1/cart/list/summary', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def cart_list_summary_v1(self, **kwargs):
        kwargs = http.request.get_json_data() or kwargs
        if kwargs.get('uid'):
            is_guest = kwargs.get('is_guest')
            if is_guest == "true":
                guest_user = request.env['guest.session'].sudo().search([('id', '=', int(kwargs.get('uid')))])
                if guest_user:
                    public_user = request.env['res.users'].sudo().get_res_user_public()
                    customer_id = public_user.partner_id.id
                else:
                    return ({'status': False, 'message': 'You are not a Valid user'})
            else:
                customer_id = request.env['res.users'].sudo().search([('id', '=', kwargs.get('uid'))]).partner_id.id
            if not customer_id:
                guest_user = request.env['custom.guest.session'].sudo().search(
                    [('id_unique', '=', int(kwargs.get('uid')))])
                if guest_user:
                    public_user = request.env['res.users'].get_res_user_public()
                    customer_id = public_user.partner_id.id
            carts = request.env['sale.order'].search_read([('state', '=', 'draft'),('partner_id_id', '=', customer_id)],
                                                         ['cart_name', 'amount_total'])
            return (carts if carts else {'status': False, 'message': 'Sorry Your Cart List Is Empty'})
        else:
            return ({'status': False, 'message': 'Please Pass Correct Info'})
        
    @http.route('/api/v1/cart/list/view', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def cart_list_view_v1(self, **kwargs):
        kwargs = http.request.get_json_data() or kwargs
        if kwargs.get('uid'):
            return (
                request.env['sale.order.line'].search_read([('order_id', '=', kwargs.get('list_id'))],
                                                          ['product_id', 'product_uom_qty', 'price_unit', 'price_subtotal']))
        else:
            return json.dumps({'status': False, 'message': 'Please Pass Correct Info'})