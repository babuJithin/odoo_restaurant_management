from odoo.http import request
import json
from odoo import http
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
import logging
import itertools

base_url_local = "http://3.7.90.229:8019"
# base_url_local = "http://localhost:8035"

_logger = logging.getLogger(__name__)


class banner_credentials_v1(http.Controller):


    @http.route('/api/v1/mobileHome', type="jsonrpc", methods=['POST'], auth='public', csrf=False, cors='*')
    def mobileHomeBanner_v1(self,**kwargs):
        kwargs = http.request.get_json_data() or kwargs
        banners = request.env['banner.element'].search([('active', '=', True)], order='sequence')
        banner_info = []
        for banner in banners:
            if banner.element_type != 'product':
                banner_vals = {"name": banner.name or "",
                               "sequence": banner.sequence, "element_type": banner.element_type or "","scroll_type":banner.scroll_type or "","grid_count":int(banner.grid_count),
                               "banner_items": [{
                                   "url": base_url_local+"/website/image/banner.element.item/{}/image".format(
                                       x.id) if x.image else base_url_local+"/website/image/product.public.category/{}/image_1920".format(
                                       x.categ_id.id) if x.element_type == "category" else "",
                                   "color": x.color if x.color else "NO",
                                   "product_id": x.product_id.id if x.product_id else 0,
                                   "name": x.name or "",
                                   "categ_name": x.categ_id.name if x.categ_id.name else "" if x.category_wise or x.element_type == "category" else "",
                                   "categ_id": x.categ_id.id if x.categ_id.id else 0 if x.category_wise or x.element_type == "category" else 0,
                                   "sub_categ_ids": [{"name": sub.name, "sub_categ_id": sub.id,
                                                      "url": base_url_local+"/website/image/product.public.category/{}/image_1920".format(
                                                          sub.id)} for sub in x.sub_categ_ids]} for
                                   x in banner.banner_items]}
                banner_info.append(banner_vals)

            else:
                banner_vals = {"name": banner.name,
                               "sequence": banner.sequence, "element_type": banner.element_type,"scroll_type":banner.scroll_type or "","grid_count":int(banner.grid_count), "product_ids": []}


                product_records = banner.sudo().product_ids
                for product in product_records:
                    try:
                        pricelist = request.env['product.pricelist.item'].sudo().search(
                            [('product_tmpl_id', '=', int(product.id))])
                        offer_percentage = [product.list_price - (
                                product.list_price * item.percent_price / 100) if item.percent_price > 0 else (
                            product.list_price - item.discount_amount if item.discount_amount > 0 else item.fixed_price)
                                            for item in pricelist if
                                            (not item.date_end and item.pricelist_id.selectable) or (
                                                    item.date_end and item.date_end.date() >= datetime.now().date() and item.pricelist_id.selectable)]
                        if offer_percentage:
                            offer_price = offer_percentage[0]
                        else:
                            offer_price = 0
                        discount_price = product.list_price - offer_price
                    except Exception as e:
                        print(e)
                        offer_price = 0
                        discount_price = 0
                    vals = {
                        "product_id": product.id if product.id else 0,
                        "main_category_id": product.categ_id.id if product.categ_id.id else 0,
                        "category_name": product.categ_id.name if product.categ_id.name else 0,
                        "is_wishlist": False,
                        "product": product.name if product.name else "",
                        "product_url": str(product.website_url),
                        "product_code": product.default_code if product.default_code else "",
                        "product_description_sale": product.description if product.description else "",
                        "quantity": product.qty_available if product.qty_available else 0,
                        "price": round(offer_price, 2) if offer_price else round(product.list_price, 2) or 0,
                        "org_price": round(product.list_price, 2),
                        "brand": product.brand_id.name or "",
                        "product_uom": product.uom_id.name if product.uom_id.name else "",
                        "product_uom_id": product.uom_id.id if product.uom_id.id else 0,
                        "status": "1",
                        "product_image": "http://" + str(
                            http.request.httprequest.host) + "/website/image/product.template/{}/image_1920".format(
                            product.id) if product.image_1920 else "False",
                        "product_type": []}


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
                            "price": round(offer_price, 2) if offer_price else round(variant.list_price, 2) or 0,
                            "org_price": round(variant.list_price, 2),
                            "quantity": variant.qty_available if variant.qty_available else 0,
                            "product_uom": variant.uom_id.name if variant.uom_id.name else "",
                            "product_uom_id": variant.uom_id.id if variant.uom_id.id else 0,
                            "product_id": product.id if product.id else 0,
                            "brand": product.brand_id.name or "",
                            "status": "1",
                            "product_type_name": ','.join(
                                [str(v.display_name) for v in variant.product_template_attribute_value_ids]),
                            "main_category_id": product.categ_id.id if product.categ_id.id else 0,
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
                                [('product_id', '=', product.product_variant_ids[0].id), ('partner_id', '=',
                                                                                          request.env[
                                                                                              'res.users'].sudo().search(
                                                                                              [('id', '=', int(
                                                                                                  kwargs.get(
                                                                                                      'user_id')))]).partner_id.id)]).exists():
                            vals1['is_wishlist'] = True
                            vals['is_wishlist'] = True
                        else:
                            vals1['is_wishlist'] = False
                            vals['is_wishlist'] = False

                    if kwargs.get('location_id'):
                        location_ids = [x.delivery_location_id.ids for x in product.delivery_method]
                        location_ids = list(itertools.chain(*location_ids))

                        if int(kwargs.get('location_id')) in location_ids:
                            vals['in_location'] = True
                        else:
                            vals['in_location'] = False
                    banner_vals["product_ids"].append(vals)
                banner_info.append(banner_vals)


        return {"status": "Ok", "status_code": 200, "banner_info": banner_info, "order_rules": {},
                "brandInfo": [{"brand_id": b.id,
                               "brand": b.name, "element_type": "brand",
                               "brand_image": base_url_local+"/website/image/product.brand/{}/brand_image".format(
                                   b.id) if b.brand_image else "False",
                               "products_count": b.product_count} for b in
                              request.env['product.brand'].sudo().search([('top_brand', '=', True)])]}







