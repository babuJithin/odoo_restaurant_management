# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging

_logger = logging.getLogger(__name__)


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    top_category = fields.Boolean()
    banner = fields.Binary('Banner Image', attachment=True, store=True)
    note = fields.Text(string="Note")
    category_type = fields.Selection([
        ('Product', 'Product'), ('Service', 'Service')], string="Category Type")


class MobileBannerElement(models.Model):
    _name = 'banner.element'
    _description = 'Banner Element'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, default=lambda self: _('New'))
    sequence = fields.Integer('Sequence', required=True, default=1)
    element_type = fields.Selection([
        ("banner", "Banner"),
        ("featured product category", "Featured Product Category"),
        ("product category", "Product Category"),
        ("carousel", "Carousel"),
        ("full", "Full Block"),
        ("product", "Product"),
        ("grid", "Grid"),
        ("category", "Category"),
    ], string="Element Type", tracking=True, required=True, default='banner')
    banner_items = fields.Many2many('banner.element.item', string='Items', tracking=True)
    active = fields.Boolean(default=True)
    # NOTE: 'limit' is not a valid Many2many field kwarg - it was silently
    # ignored by Odoo even in 17. If you want to cap the number of selectable
    # products in the UI, do it via a domain/context on the view field
    # instead of here.
    product_ids = fields.Many2many('product.template', string="Products", tracking=True)
    grid_count = fields.Selection([
        ('0', '0'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ], string="Grid Count", default='0')

    scroll_type = fields.Selection([
        ('grid', 'Grid'),
        ('horizontal', 'Horizontal'),
    ], string="Scroll Type", default='grid')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('banner.element') or _('New')
        return super().create(vals_list)

    @api.onchange('element_type')
    def set_domain_banner_items(self):
        # NOTE: this duplicates the domain already set directly on the
        # banner_items field in the form view (domain="[('element_type', '=',
        # element_type)]"), except it also filters on active=True. Consider
        # consolidating to one place so behavior stays consistent.
        return {'domain': {'banner_items': [('element_type', '=', self.element_type), ('active', '=', True)]}}


class MobileBannerElementItems(models.Model):
    _name = 'banner.element.item'
    _description = 'Banner Element Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True, required=True, default=lambda self: _('New'))

    color = fields.Char('Color', tracking=True)
    active = fields.Boolean(default=True)
    product_wise = fields.Boolean('Product Wise?')
    category_wise = fields.Boolean('Category Wise?')
    product_id = fields.Many2one('product.template', string="Product", tracking=True)
    categ_id = fields.Many2one(
        'product.public.category', string="Category", tracking=True, domain="categ_id_domain")
    sub_categ_ids = fields.Many2many('product.public.category', string="Sub Categories", tracking=True)
    element_type = fields.Selection([
        ("banner", "Banner"),
        ("featured product category", "Featured Product Category"),
        ("service category", "Service Category"),
        ("product category", "Product Category"),
        ("carousel", "Carousel"),
        ("full", "Full Block"),
        ("grid", "Grid"),
        ("category", "Category"),
    ], string="Element Type", required=True, tracking=True)
    image = fields.Binary('Image', attachment=True, store=True)

    categ_id_domain = fields.Char(
        compute="_compute_categ_id_domain",
        readonly=True,
    )

    @api.depends('element_type')
    def _compute_categ_id_domain(self):
        for record in self:
            if record.element_type in ['featured product category', 'product category']:
                domain = [('category_type', '=', 'Product')]
            elif record.element_type == 'service category':
                domain = [('category_type', '=', 'Service')]
            else:
                domain = []
            record.categ_id_domain = json.dumps(domain)

    @api.onchange('element_type')
    def _onchange_element_type(self):
        self._compute_categ_id_domain()  # Re-compute

    @api.onchange('categ_id')
    def set_sub_categ_domain(self):
        if self.categ_id:
            child_ids = self.env['product.public.category'].search(
                [('parent_id', '=', self.categ_id.id)], order='sequence', limit=4).ids
            self.sub_categ_ids = child_ids

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('banner.element.item') or _('New')
        return super().create(vals_list)