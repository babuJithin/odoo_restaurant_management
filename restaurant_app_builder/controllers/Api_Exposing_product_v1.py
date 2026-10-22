from odoo.http import request
import json
from odoo import http
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta

import itertools

import pyotp
import logging
from bs4 import BeautifulSoup
import re
import random
import geopy
from geopy.distance import geodesic
import os

_logger = logging.getLogger(__name__)

base_url = "http://3.7.90.229:8019"


class log_in_credentials_v1(http.Controller):



    @http.route('/api/v1/allCategory', methods=['POST'], type='jsonrpc', auth='public', csrf=False)
    def getallCategory_list_v1(self, **kwargs):
        kwargs = http.request.get_json_data() or kwargs
        # kwargs = http.request.jsonrequest or kwargs
        categories = request.env['product.public.category'].sudo().search(
            [('parent_id', '=', False)], order="sequence")
        category_info = []
        product_categories = []
        service_categories = []
        print(product_categories,service_categories,categories)
        for cat in categories:
            subcategories = request.env['product.public.category'].sudo().search(
                [('parent_id', '=', cat.id)])

            if cat.category_type == 'Product':
                target_array = product_categories
            elif cat.category_type == 'Service':
                target_array = service_categories
            else:
                continue
            vals = {"category_id": cat.id if cat.id else 0,
                    "category": cat.name if cat.name else "",
                    "category_type": cat.category_type if cat.category_type else "",
                    "parent_category": cat.parent_id.id if cat.parent_id.id else 0,
                    "status": "1",
                    "banner_image": "http://" + str(
                        http.request.httprequest.host) + "/website/image/product.public.category/{}/banner".format(
                        cat.id) if cat.banner else "False",
                    "category_image": "http://" + str(
                        http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                        cat.id) if cat.image_1920 else "False",
                    "created_at_date": cat.create_date.strftime('%Y-%m-%d'),
                    "created_at": cat.create_date.strftime('%Y-%m-%d'),
                    "child_cat": [],
                    "child_cat_exists": False,
                    "note": cat.note if cat.note else ""
                    }
            for subcat in subcategories:
                subchild = request.env['product.public.category'].sudo().search([('parent_id', '=', subcat.id)])
                vals1 = {"category_id": subcat.id if subcat.id else 0,
                         "category": subcat.name if subcat.name else "",
                         "category_type": subcat.category_type if subcat.category_type else "",
                         "parent_category": subcat.parent_id.id if subcat.parent_id.id else 0,
                         "status": "1",
                         "banner_image": "http://" + str(
                             http.request.httprequest.host) + "/website/image/product.public.category/{}/banner".format(
                             cat.id) if cat.banner else "False",
                         "category_image": "http://" + str(
                             http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                             subcat.id) if subcat.image_1920 else "False",
                         "created_at_date": subcat.create_date.strftime('%Y-%m-%d'),
                         "created_at": subcat.create_date.strftime('%Y-%m-%d'),
                         "child_cat": [],
                         "child_cat_exists": False,
                         "note": subcat.note if subcat.note else ""
                         }

                vals['child_cat'].append(vals1)
                if vals['child_cat']:
                    vals['child_cat_exists'] = True
                for child in subchild:
                    smallchild = request.env['product.public.category'].sudo().search(
                        [('parent_id', '=', child.id)])

                    vals2 = {"category_id": child.id if child.id else 0,
                             "category": child.name if child.name else "",
                             "parent_category": child.parent_id.id if child.parent_id.id else 0,
                             "status": "1",
                             "banner_image": "http://" + str(
                                 http.request.httprequest.host) + "/website/image/product.public.category/{}/banner".format(
                                 cat.id) if cat.banner else "False",
                             "category_image": "http://" + str(
                                 http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                                 child.id) if child.image_1920 else "False",
                             "created_at_date": child.create_date.strftime('%Y-%m-%d'),
                             "created_at": child.create_date.strftime('%Y-%m-%d'),
                             "child_cat": [],
                             "child_cat_exists": False,
                             "note": child.note if child.note else ""

                             }
                    vals1['child_cat'].append(vals2)
                    if vals1['child_cat']:
                        vals1['child_cat_exists'] = True
                    for child1 in smallchild:
                        vals3 = {"category_id": child1.id if child1.id else 0,
                                 "category": child1.name if child1.name else "",
                                 "parent_category": child1.parent_id.id if child1.parent_id.id else 0,
                                 "status": "1",
                                 "category_image": "http://" + str(
                                     http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                                     child1.id) if child1.image_1920 else "False",
                                 "created_at_date": child1.create_date.strftime('%Y-%m-%d'),
                                 "created_at": child1.create_date.strftime('%Y-%m-%d'),
                                 "child_cat": [],
                                 "child_cat_exists": False,
                                 "note": child1.note if child1.note else ""

                                 }
                        vals2['child_cat'].append(vals3)
                        if vals2['child_cat']:
                            vals2['child_cat_exists'] = True
            target_array.append(vals)
        return {'status': True, 'message': 'Categories available',
                'data': {'product_categories': product_categories, 'service_categories': service_categories}}



    @http.route('/api/v1/subCategory', methods=['POST'], type='jsonrpc', auth='public', csrf=False)
    def getSubCategoryv1(self, **kwargs):
        kwargs = http.request.get_json_data() or kwargs
        categ_id = kwargs.get('categ_id')
        if categ_id:
            categories = request.env['product.public.category'].sudo().search([('parent_id', '=', int(categ_id))],
                                                                              order='sequence')
        else:
            categories = request.env['product.public.category'].sudo().search([('parent_id', '!=', False)],
                                                                              order='sequence')
        category_info = []
        for cat in categories:
            subcategories = request.env['product.public.category'].sudo().search([('parent_id', '=', cat.id)])
            vals = {"category_id": cat.id if cat.id else 0,
                    "category": cat.name if cat.name else "",
                    "category_type": cat.category_type if cat.category_type else "",
                    "parent_category": cat.parent_id.id if cat.parent_id.id else 0,
                    "status": "1",
                    "category_image": "http://" + str(
                        http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                        cat.id) if cat.image_1920 else "False",
                    "banner_image": "http://" + str(
                        http.request.httprequest.host) + "/website/image/product.public.category/{}/banner".format(
                        cat.id) if cat.banner else "False",

                    "created_at_date": cat.create_date.strftime('%Y-%m-%d'),
                    "created_at": cat.create_date.strftime('%Y-%m-%d'),
                    "child_cat": [],
                    "child_cat_exists": False,
                    "note": cat.note if cat.note else ""
                    }
            for subcat in subcategories:
                subchild = request.env['product.public.category'].sudo().search([('parent_id', '=', subcat.id)])
                vals1 = {"category_id": subcat.id if subcat.id else 0,
                         "category": subcat.name if subcat.name else "",
                         "parent_category": subcat.parent_id.id if subcat.parent_id.id else 0,
                         "status": "1",
                         "banner_image": "http://" + str(
                             http.request.httprequest.host) + "/website/image/product.public.category/{}/banner".format(
                             cat.id) if cat.banner else "False",
                         "category_image": "http://" + str(
                             http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                             subcat.id) if subcat.image_1920 else "False",
                         "created_at_date": subcat.create_date.strftime('%Y-%m-%d'),
                         "created_at": subcat.create_date.strftime('%Y-%m-%d'),
                         "child_cat": [],
                         "child_cat_exists": False,
                         "note": subcat.note if subcat.note else ""
                         }
                vals['child_cat'].append(vals1)
                if vals['child_cat']:
                    vals['child_cat_exists'] = True
                for child in subchild:
                    smallchild = request.env['product.public.category'].sudo().search(
                        [('parent_id', '=', child.id)])

                    vals2 = {"category_id": child.id if child.id else 0,
                             "category": child.name if child.name else "",
                             "parent_category": child.parent_id.id if child.parent_id.id else 0,
                             "status": "1",
                             "banner_image": "http://" + str(
                                 http.request.httprequest.host) + "/website/image/product.public.category/{}/banner".format(
                                 cat.id) if cat.banner else "False",
                             "category_image": "http://" + str(
                                 http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                                 child.id) if child.image_1920 else "False",
                             "created_at_date": child.create_date.strftime('%Y-%m-%d'),
                             "created_at": child.create_date.strftime('%Y-%m-%d'),
                             "child_cat": [],
                             "child_cat_exists": False,
                             "note": child.note if child.note else ""
                             }
                    vals1['child_cat'].append(vals2)
                    if vals1['child_cat']:
                        vals1['child_cat_exists'] = True
                    for child1 in smallchild:
                        vals3 = {"category_id": child1.id if child1.id else 0,
                                 "category": child1.name if child1.name else "",
                                 "parent_category": child1.parent_id.id if child1.parent_id.id else 0,
                                 "status": "1",
                                 "category_image": "http://" + str(
                                     http.request.httprequest.host) + "/website/image/product.public.category/{}/image_1920".format(
                                     child1.id) if child1.image_1920 else "False",
                                 "created_at_date": child1.create_date.strftime('%Y-%m-%d'),
                                 "created_at": child1.create_date.strftime('%Y-%m-%d'),
                                 "child_cat": [],
                                 "child_cat_exists": False,
                                 "note": child1.note if child1.note else ""
                                 }
                        vals2['child_cat'].append(vals3)
                        if vals2['child_cat']:
                            vals2['child_cat_exists'] = True
            category_info.append(vals)
        return {'status': True, 'message': 'Categories available', 'data': category_info}



    @http.route('/api/v1/productBrands', method=['GET'], auth='public', csrf=False)
    def get_all_brandLists_v1(self, **kwargs):
        brand = request.env['product.brand'].sudo().search([])
        return json.dumps({'message': 'Brands Available', "message_arabic": "الماركات المتاحة",
                           'brands': [{'id': b.id, 'name': b.name,
                                       'product_count': b.product_count,
                                       'brand_image': base_url + "/web/image/product.brand/{}/brand_image".format(
                                           b.id) if b.brand_image else ""} for b in brand]})





    @http.route('/api/v1/brand/products', type='jsonrpc', methods=['POST'], auth='public', csrf=False)
    def getBrandProducts_web_v1(self, **kwargs):
        # kwargs = http.request.jsonrequest or kwargs
        kwargs = http.request.get_json_data() or kwargs
        offset = int(kwargs.get('offset'))
        limit = 12
        offset_start = offset * limit
        offset_end = offset_start + limit
        latitude = (kwargs.get('latitude', 0))
        longitude = (kwargs.get('longitude', 0))
        customer_location = (latitude, longitude)
        seller_shops = request.env['seller.shop'].sudo().search([('active', '=', True)])
        seller_available_prod = []
        for seller_shop in seller_shops:
            seller_location = (seller_shop.latitude, seller_shop.longitude)
            distance = geodesic(seller_location, customer_location).kilometers
            if distance <= seller_shop.radius:
                seller_available_prod.extend(seller_shop.seller_product_ids.ids)
        domain = [('sale_ok', '=', True), ('is_published', '=', True), ('id', 'in', seller_available_prod)]
        if kwargs.get('brandId'):
            domain.append(('brand_id', '=', int(kwargs.get('brandId'))))
            try:
                if kwargs.get('sort') == 'HL':
                    products = request.env['product.template'].sudo().search(domain, order='list_price desc')
                elif kwargs.get('sort') == 'LH':
                    products = request.env['product.template'].sudo().search(domain, order='list_price')
                elif kwargs.get('sort') == 'NW':
                    products = request.env['product.template'].sudo().search(domain, order='id desc')
                elif kwargs.get('sort') == 'ZA':
                    products = request.env['product.template'].sudo().search(domain, order='name desc')
                elif kwargs.get('sort') == 'AZ':
                    products = request.env['product.template'].sudo().search(domain, order='name')
                else:
                    products = request.env['product.template'].sudo().search(domain, order='website_sequence')
            except:
                products = request.env['product.template'].sudo().search(domain, order='website_sequence')

            product_types = [{'id': i.id, 'name': i.name} for i in products.feed_product_type]
            brand_ids = [{'id': i.id, 'name': i.name} for i in
                         request.env['product.brand'].sudo().search([('id', '=', int(kwargs.get('brandId')))])]

            if kwargs.get('filtered'):  # {'brand_id':[1783,11],'product_types':[12,14]}
                filtered_vals = kwargs.get('filtered')
                product_type = filtered_vals.get('product_types')
                if product_type != []:
                    products = [x for x in products if x.feed_product_type.id in product_type]
                else:
                    products = products

            products = products[offset_start:offset_end]
            if len(products) > 0:
                products_info = []
                for product in products:
                    vals = {
                        "qes_product_id": product.id if product.id else 0,
                        "is_wishlist": False,
                        "brand": product.brand_id.name or "",
                        "qes_product": product.name if product.name else "",
                        "product_url": str(product.website_url),
                        "qes_product_arabic": product.name_arabic if product.name_arabic else "",
                        "qes_product_code": product.default_code if product.default_code else "",
                        "qes_product_det": product.description_sale if product.description_sale else "",
                        "qes_quantity": product.virtual_available if product.virtual_available > 0.0 else 0.0,
                        "qes_prize": product.list_price if product.list_price else 0,
                        "b2b_price": product.b2b_price if product.b2b_price else 0,
                        "product_uom": product.uom_id.name if product.uom_id.name else "",
                        "product_uom_id": product.uom_id.id if product.uom_id.id else 0,
                        "country_of_origin": product.country_id.name if product.country_id.name else "",
                        "status": "1",
                        "vendor_type": "1",
                        "qes_updated_at": product.write_date.strftime('%Y-%m-%d'),
                        "created_at_date": product.create_date.strftime('%Y-%m-%d'),
                        "qes_product_image": "http://" + str(
                            http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                            product.id) if product.image_1920 else "False",
                        "product_type": []}

                    for variant in request.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', product.id)]):
                        vals1 = {
                            "product_type_id": variant.id if variant.id else 0,
                            "qes_prize": round(variant.lst_price, 2) or 0,
                            "quantity": variant.virtual_available if variant.virtual_available > 0.0 else 0.0,
                            "product_uom": variant.uom_id.name if variant.uom_id.name else "",
                            "product_uom_id": variant.uom_id.id if variant.uom_id.id else 0,
                            "qes_product_id": product.id if product.id else 0,
                            "created_at_date": variant.create_date.strftime('%Y-%m-%d'),
                            "status": "1",
                            "product_type_name": ','.join(
                                [str(v.display_name) for v in variant.product_template_attribute_value_ids]),

                            "is_wishlist": False,
                            "product_type_url": str(variant.website_url),
                            "product_type_arabic": variant.name_arabic if variant.name_arabic else "",
                            "product_type_code": variant.default_code if variant.default_code else "",
                            "product_type_det": variant.description_sale if variant.description_sale else "",
                            "product_type_image": "http://" + str(
                                http.request.httprequest.host) + "/website/image/product.product/{}/image_1920".format(
                                variant.id) if variant.image_1920 else "False",
                        }

                        vals['product_type'].append(vals1)
                    if kwargs.get('user_id'):
                        if request.env['product.wishlist'].sudo().search(
                                [('product_id', '=', product.product_variant_ids[0].id),
                                 ('partner_id', '=', request.env[
                                     'res.users'].sudo().search(
                                     [('id', '=', int(kwargs.get('user_id')))]).partner_id.id)]).exists():
                            vals['is_wishlist'] = True
                            vals1['is_wishlist'] = True
                        else:
                            vals['is_wishlist'] = False
                            vals1['is_wishlist'] = False
                    else:
                        vals['is_wishlist'] = False
                        vals1['is_wishlist'] = False
                    products_info.append(vals)

                return {'status': True, 'message': 'Available Products are', 'data': products_info,
                        'brand_info': brand_ids, 'product_types': product_types}
            else:
                return {'status': False, 'message': 'No products Found'}
        else:
            return {'status': False, 'message': 'Please pass brand id'}




    @http.route('/api/v1/category/products', methods=['POST'], type='jsonrpc', auth='public', csrf=False)
    def getCategoryProducts_web_v1(self, **kwargs):
        # kwargs = http.request.jsonrequest or kwargs
        kwargs = http.request.get_json_data() or kwargs
        offset = int(kwargs.get('offset'))
        limit = 12
        offset_start = offset * limit
        offset_end = offset_start + limit

        domain = [('sale_ok', '=', True), ('is_published', '=', True)]
        if kwargs.get('categId'):
            domain.append(('public_categ_ids', 'in', int(kwargs.get('categId'))))
            try:
                if kwargs.get('sort') == 'HL':
                    products = request.env['product.template'].sudo().search(domain, order='list_price desc')
                elif kwargs.get('sort') == 'LH':
                    products = request.env['product.template'].sudo().search(domain, order='list_price')
                elif kwargs.get('sort') == 'NW':
                    products = request.env['product.template'].sudo().search(domain, order='id desc')
                elif kwargs.get('sort') == 'ZA':
                    products = request.env['product.template'].sudo().search(domain, order='name desc')
                elif kwargs.get('sort') == 'AZ':
                    products = request.env['product.template'].sudo().search(domain, order='name')
                else:
                    products = request.env['product.template'].sudo().search(domain, order='website_sequence')
            except:
                products = request.env['product.template'].sudo().search(domain, order='website_sequence')

            products = products[offset_start:offset_end]
            if len(products) > 0:
                products_info = []
                for product in products:
                    try:
                        pricelist = request.env['product.pricelist.item'].sudo().search(
                            [('product_tmpl_id', '=', int(product.id))])
                        print("pricelist", pricelist)
                        offer_percentage = [product.list_price - (
                                product.list_price * item.percent_price / 100) if item.percent_price > 0 else (
                            product.list_price - item.discount_amount if item.discount_amount > 0 else item.fixed_price)
                                            for item in pricelist if
                                            (not item.date_end and item.pricelist_id.selectable) or (
                                                    item.date_end and item.date_end >= datetime.now() and item.pricelist_id.selectable)]
                        offer_price = offer_percentage[0]
                        discount_price = product.list_price - offer_price
                    except Exception as e:
                        offer_price = 0
                        discount_price = 0
                    vals = {
                        "product_id": product.id if product.id else 0,
                        "detailed_type": product.type if product.type else "",
                        "main_category_id":
                            [categ_id for categ_id in product.public_categ_ids][
                                0].id,

                        "category_name":
                            [categ_id for categ_id in product.public_categ_ids if
                             categ_id.id == int(kwargs.get('categId'))][0].name if
                            [categ_id for categ_id in product.public_categ_ids if
                             categ_id.id == int(kwargs.get('categId'))][0].name else "",
                        "is_wishlist": False,
                        "product": product.name if product.name else "",
                        "product_url": str(product.website_url),
                        "product_code": product.default_code if product.default_code else "",
                        "product_description_sale": product.description_sale if product.description_sale else "",
                        "quantity": product.virtual_available if product.virtual_available > 0.0 else 0.0,
                        "price": round(offer_price, 2) if offer_price else round(product.list_price, 2) or 0,
                        "org_price": round(product.list_price, 2),
                        "product_uom": product.uom_id.name if product.uom_id.name else "",
                        "product_uom_id": product.uom_id.id if product.uom_id.id else 0,
                        "status": "1",
                        "brand": product.brand_id.name or "",
                        "main_category_id":
                            [categ_id for categ_id in product.public_categ_ids if categ_id.parent_id.id == False][
                                0].id if [categ_id for categ_id in product.public_categ_ids if
                                          categ_id.parent_id.id == False] else "",
                        "product_image": "http://" + str(
                            http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                            product.id) if product.image_1920 else "False",
                        "product_type": []}
                    print(vals)
                    print(vals['price'])
                    print(offer_price)
                    for variant in request.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', product.id)]):
                        try:
                            pricelist = request.env['product.pricelist.item'].sudo().search(
                                [('product_tmpl_id', '=', int(product.id))])
                            offer_percentage = [variant.list_price - (
                                    variant.list_price * item.percent_price / 100) if item.percent_price > 0 else (
                                variant.list_price - item.discount_amount if item.discount_amount > 0 else item.fixed_price)
                                                for item in pricelist if
                                                (not item.date_end and item.pricelist_id.selectable) or (
                                                        item.date_end and item.date_end >= datetime.now() and item.pricelist_id.selectable)]
                            offer_price = offer_percentage[0]
                            discount_price = variant.list_price - offer_price
                        except Exception as e:
                            offer_price = 0
                            discount_price = 0
                        vals1 = {
                            "product_type_id": variant.id if variant.id else 0,
                            "price": round(offer_price, 2) if offer_price else round(product.list_price, 2) or 0,
                            "org_price": round(product.list_price, 2),
                            "quantity": variant.virtual_available if variant.virtual_available > 0.0 else 0.0,
                            "product_uom": variant.uom_id.name if variant.uom_id.name else "",
                            "product_uom_id": variant.uom_id.id if variant.uom_id.id else 0,
                            "product_id": product.id if product.id else 0,
                            "status": "1",
                            "brand": product.brand_id.name or "",
                            "product_type_name": ','.join(
                                [str(v.display_name) for v in variant.product_template_attribute_value_ids]),
                            "main_category_id":
                                [categ_id for categ_id in variant.public_categ_ids if
                                 categ_id.parent_id.id == False][
                                    0].id if [categ_id for categ_id in variant.public_categ_ids if
                                              categ_id.parent_id.id == False] else "",
                            "is_wishlist": False,
                            "product_type_url": str(variant.website_url),
                            "product_type_code": variant.default_code if variant.default_code else "",
                            "product_type_description": variant.description_sale if variant.description_sale else "",
                            "product_type_image": "http://" + str(
                                http.request.httprequest.host) + "/website/image/product.product/{}/image_1920".format(
                                variant.id) if variant.image_1920 else "False",
                        }

                        vals['product_type'].append(vals1)
                    if kwargs.get('user_id'):
                        if request.env['product.wishlist'].sudo().search(
                                [('product_id', '=', product.product_variant_ids[0].id),
                                 ('partner_id', '=', request.env[
                                     'res.users'].sudo().search(
                                     [('id', '=', int(kwargs.get('user_id')))]).partner_id.id)]).exists():
                            vals1['is_wishlist'] = True
                            vals['is_wishlist'] = True
                        else:
                            vals1['is_wishlist'] = False
                            vals['is_wishlist'] = False
                    else:
                        vals['is_wishlist'] = False
                        vals1['is_wishlist'] = False
                    products_info.append(vals)

                return {'status': True, 'message': 'Available Products are', 'data': products_info,
                        }
            else:
                return {'status': False, 'message': 'No products'}
        else:
            return {'status': False, 'message': 'Please pass  category id  - categId'}



    @http.route('/api/v1/product', methods=['POST'], type="jsonrpc", auth='public', csrf=False)
    def getProductWebInfo_v1(self, **kwargs):

        kwargs = http.request.get_json_data() or kwargs
        if kwargs.get('productId'):
            product = request.env['product.template'].sudo().search(
                [('id', '=', int(kwargs.get('productId'))), ('is_published', '=', True)])
            if product:
                products_info = []
                try:
                    pricelist = request.env['product.pricelist.item'].sudo().search(
                        [('product_tmpl_id', '=', int(product.id))])
                    offer_percentage = [product.list_price - (
                            product.list_price * item.percent_price / 100) if item.percent_price > 0 else (
                        product.list_price - item.discount_amount if item.discount_amount > 0 else item.fixed_price)
                                        for item in pricelist if
                                        (not item.date_end and item.pricelist_id.selectable) or (
                                                item.date_end and item.date_end >= datetime.now() and item.pricelist_id.selectable)]
                    offer_price = offer_percentage[0]
                    discount_price = product.list_price - offer_price
                except Exception as e:
                    offer_price = 0
                    discount_price = 0
                vals = {
                    "product_id": product.id if product.id else 0,
                    "detailed_type": product.type if product.type else "",
                    "product": product.name if product.name else "",
                    "brand": product.brand_id.name or "",
                    "product_url": str(product.website_url),
                    "product_code": product.default_code if product.default_code else "",
                    "product_description": product.description_sale if product.description_sale else "",
                    "quantity": product.virtual_available if product.virtual_available > 0.0 else 0.0,
                    "product_uom": product.uom_id.name if product.uom_id.name else "",
                    "product_uom_id": product.uom_id.id if product.uom_id.id else 0,
                    "price": round(offer_price, 2) if offer_price else round(product.list_price, 2) or 0,
                    "org_price": round(product.list_price, 2),
                    "country_of_origin": product.country_of_origin.name if product.country_of_origin.name else "",
                    "country_of_origin_flag": "http://" + str(
                        http.request.httprequest.host) + product.country_of_origin.image_url if product.country_of_origin.image_url else "",
                    "main_category_id":
                        [categ_id for categ_id in product.public_categ_ids if categ_id.parent_id.id == False][
                            0].id if [categ_id for categ_id in product.public_categ_ids if
                                      categ_id.parent_id.id == False] else "",
                    "status": "1",
                    "product_image": "http://" + str(
                        http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                        product.id) if product.image_1920 else "False",
                    "is_wishlist": False,
                    "images": [],
                    "product_type": [],
                    "product_type_prices": {item.display_name: [{'variantName': x.name, 'price': x.price_extra}
                                                                for x in item.product_template_value_ids if
                                                                x.product_attribute_value_id.id in product.attribute_line_ids.value_ids.ids]
                                            for item in product.attribute_line_ids},
                    "similar_products":[]
                }

                for variant in request.env['product.product'].sudo().search([('product_tmpl_id', '=', product.id)]):
                    try:
                        pricelist = request.env['product.pricelist.item'].sudo().search(
                            [('product_tmpl_id', '=', int(product.id))])
                        print("pricelist", pricelist)
                        offer_percentage = [variant.list_price - (
                                variant.list_price * item.percent_price / 100) if item.percent_price > 0 else (
                            variant.list_price - item.discount_amount if item.discount_amount > 0 else item.fixed_price)
                                            for item in pricelist if
                                            (not item.date_end and item.pricelist_id.selectable) or (
                                                    item.date_end and item.date_end >= datetime.now() and item.pricelist_id.selectable)]
                        offer_price = offer_percentage[0]
                        discount_price = variant.list_price - offer_price
                    except Exception as e:
                        offer_price = 0
                        discount_price = 0
                    vals1 = {
                        "product_type": variant.id if variant.id else 0,
                        "product_type_id": variant.id if variant.id else 0,
                        "price": round(offer_price, 2) if offer_price else round(product.list_price, 2) or 0,
                        "org_price": round(product.list_price, 2),
                        "quantity": variant.virtual_available if variant.virtual_available > 0.0 else 0.0,
                        "product_uom": variant.uom_id.name or "",
                        "product_uom_id": variant.uom_id.id or 0,
                        "product_id": product.id or 0,
                        "brand": product.brand_id.name or "",
                        "status": "1",
                        "country_of_origin": variant.country_of_origin.name if variant.country_of_origin.name else "",
                        "country_of_origin_flag": "http://" + str(
                            http.request.httprequest.host) + variant.country_of_origin.image_url if variant.country_of_origin.image_url else "",
                        "product_type_name": ','.join(
                            [str(v.display_name) for v in variant.product_template_attribute_value_ids]),
                        "main_category_id":
                            [categ_id for categ_id in variant.public_categ_ids if categ_id.parent_id.id == False][
                                0].id if [categ_id for categ_id in variant.public_categ_ids if
                                          categ_id.parent_id.id == False] else "",
                        "is_wishlist": False,
                        "product_type_url": str(variant.website_url),
                        "product_type_code": variant.default_code if variant.default_code else "",
                        "product_type_description": variant.description_sale if variant.description_sale else "",
                        "product_type_image": "http://" + str(
                            http.request.httprequest.host) + "/website/image/product.product/{}/image_1920".format(
                            variant.id) if variant.image_1920 else "False",
                    }

                    vals['product_type'].append(vals1)
                for i in product.product_template_image_ids:
                    vals2 = {
                        "product_image_id": i.id or 0,
                        "product_flag": i.display_name or "",
                        "product_id": product.id or 0,
                        "product_image": "http://" + str(
                            http.request.httprequest.host) + "/website/image/product.image/{}/image_1920".format(
                            i.id) if i.image_1920 else "False",
                    }
                    vals['images'].append(vals2)


                if kwargs.get('user_id'):
                    if request.env['product.wishlist'].sudo().search(
                            [('product_id', '=', product.product_variant_ids[0].id),
                             ('partner_id', '=', request.env[
                                 'res.users'].sudo().search(
                                 [('id', '=', int(kwargs.get('user_id')))]).partner_id.id)]).exists():
                        vals1['is_wishlist'] = True
                        vals['is_wishlist'] = True
                    else:
                        vals1['is_wishlist'] = False
                        vals['is_wishlist'] = False
                else:
                    vals['is_wishlist'] = False
                    vals1['is_wishlist'] = False
                main_category_prds = [categ_id for categ_id in product.public_categ_ids if categ_id.parent_id.id == False][
                            0].id if [categ_id for categ_id in product.public_categ_ids if
                                      categ_id.parent_id.id == False] else ""
                if main_category_prds:
                    id_main_category = int(main_category_prds)
                    main_category_templates = request.env['product.template'].search([('id','!=',product.id),('public_categ_ids','in',[id_main_category])])
                    for main_category_template in main_category_templates:
                        main_categ_temp_val= {
                            "product_id": main_category_template.id if main_category_template.id else 0,
                            "detailed_type": main_category_template.type if main_category_template.type else "",
                            "product": main_category_template.name if main_category_template.name else "",
                            "brand": main_category_template.brand_id.name or "",
                            "product_url": str(main_category_template.website_url),
                            "product_code": main_category_template.default_code if main_category_template.default_code else "",
                            "product_description": main_category_template.description_sale if main_category_template.description_sale else "",
                            "price": round(offer_price, 2) if offer_price else round(main_category_template.list_price, 2) or 0,
                            "product_image": "http://" + str(
                                http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                                main_category_template.id) if main_category_template.image_1920 else "False",

                        }


                        vals['similar_products'].append(main_categ_temp_val)

                products_info.append(vals)
                return {'status': True, 'message': 'Product Info', 'data': products_info}
            else:
                return {'status': False, 'message': 'No Product Available'}

        else:
            return {'status': False, 'message': 'Please enter Valid productId'}

    @http.route('/api/v1/SearchWeb', methods=['POST'], type="jsonrpc", auth='public', csrf=False)
    def search_web_v1(self, **kwargs):
        kwargs = http.request.get_json_data() or kwargs
        catName = kwargs.get('keyword')
        offset = int(kwargs.get('offset'))
        limit = 12
        offset_start = offset * limit
        offset_end = offset_start + limit




        products = request.env['product.template'].sudo().search(
            [('is_published', '=', True)])[offset_start:offset_end]
        products_info = []
        pro = []

        if str(catName) == '':
            products = products
        elif kwargs.get('categ_id'):
            pro.extend([x for x in request.env['product.template'].sudo().search(
                ['|', '|', '|', ('name', 'ilike', str(catName)), ('default_code', 'ilike', str(catName)),
                 ('barcode', 'ilike', str(catName)), ('brand_id.name', 'ilike', str(catName)),
                 ('public_categ_ids', 'in', int(kwargs.get('categ_id'))),
                 ('is_published', '=', True)])[offset_start:offset_end]])
            products = pro
        else:
            products = request.env['product.template'].sudo().search(
                ['|', '|', '|', ('name', 'ilike', str(catName)), ('default_code', 'ilike', str(catName)),
                 ('barcode', 'ilike', str(catName)), ('brand_id.name', 'ilike', str(catName)),
                 ('is_published', '=', True), ])[offset_start:offset_end]
            categories = request.env['product.public.category'].sudo().search(
                [('parent_id', '=', False), ('name', 'ilike', str(catName))])

            if categories:
                for cat in categories:
                    pro.extend([x for x in request.env['product.template'].sudo().search(
                        [('public_categ_ids', 'in', int(cat.id)),
                         ('is_published', '=', True)])])
                products = pro[offset_start:offset_end]

        for product in products:
            vals = {
                "product_id": product.id or 0,
                "product": product.name or "",
                "detailed_type": product.type if product.type else "",
                "brand": product.brand_id.name or "",
                "product_url": str(product.website_url),
                "product_code": product.default_code or "",
                "quantity": product.virtual_available if product.virtual_available > 0.0 else 0.0,
                "product_uom": product.uom_id.name or "",
                "product_uom_id": product.uom_id.id or 0,
                "price": product.list_price or 0,
                "status": "1",
                "main_category_id":
                    [categ_id for categ_id in product.public_categ_ids if categ_id.parent_id.id == False][0].id if [
                        categ_id for categ_id in product.public_categ_ids if
                        categ_id.parent_id.id == False] else "",

                "updated_at": product.write_date.strftime('%Y-%m-%d'),
                "created_at_date": product.create_date.strftime('%Y-%m-%d'),
                "product_image": "http://" + str(
                    http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                    product.id) if product.image_1920 else product.image_1920,
                "is_wishlist": False,
                "product_type": []}
            for variant in request.env['product.product'].sudo().search([('product_tmpl_id', '=', product.id)]):
                vals1 = {
                    "product_type_id": variant.id or 0,
                    "price": round(variant.lst_price, 2) or 0,
                    "brand": variant.brand_id.name or "",
                    "quantity": variant.virtual_available if variant.virtual_available > 0.0 else 0.0,
                    "product_uom": variant.uom_id.name or "",
                    "product_uom_id": variant.uom_id.id or 0,
                    "product_id": product.id or 0,
                    "created_at_date": variant.create_date.strftime('%Y-%m-%d'),
                    "status": "1",
                    "product_type_name": ','.join(
                        [str(v.display_name) for v in variant.product_template_attribute_value_ids]),
                    "main_category_id":
                        [categ_id for categ_id in variant.public_categ_ids if categ_id.parent_id.id == False][
                            0].id if [categ_id for categ_id in variant.public_categ_ids if
                                      categ_id.parent_id.id == False] else "",
                    "is_wishlist": False,
                    "product_type_url": str(variant.website_url),
                    "product_type_code": variant.default_code if variant.default_code else "",
                    "product_type_det": variant.description_sale if variant.description_sale else "",
                    "product_type_image": "http://" + str(
                        http.request.httprequest.host) + "/website/image/product.product/{}/image_1920".format(
                        variant.id) if variant.image_1920 else "False",
                }

                vals['product_type'].append(vals1)
                if kwargs.get('user_id'):
                    if request.env['product.wishlist'].sudo().search(
                            [('product_id', '=', product.product_variant_ids[0].id),
                             ('partner_id', '=', request.env[
                                 'res.users'].sudo().search(
                                 [('id', '=', int(kwargs.get('user_id')))]).partner_id.id)]).exists():
                        vals['is_wishlist'] = True
                        vals1['is_wishlist'] = True

                    else:
                        vals['is_wishlist'] = False
                        vals1['is_wishlist'] = False

                else:
                    vals['is_wishlist'] = False
                    vals1['is_wishlist'] = False

                products_info.append(vals)
        return {'status': True if products_info else False,
                        'message': "Products available" if products_info else "Products Not available",
                        'data': {"search_results": products_info}}





