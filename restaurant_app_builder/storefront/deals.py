# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class MobileDealElement(models.Model):
    _name = 'deal.element'
    _description = 'Deal Element'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, default=lambda self: _('New'))

    color = fields.Char('Color', tracking=True)
    sequence = fields.Integer('Sequence', required=True, default=1)
    active = fields.Boolean(default=True)
    image = fields.Binary('Image', attachment=True, store=True)
    # NOTE: 'limit' is not a valid Many2many field kwarg - it was silently
    # ignored even in Odoo 17. Cap the number of selectable records via a
    # domain/context on the view field instead of here, if that's the intent.
    categ_ids = fields.Many2many('product.public.category', string="Category", tracking=True)
    product_ids = fields.Many2many('product.template', string="Products", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('deal.element') or _('New')
        return super().create(vals_list)

    @api.onchange("product_ids")
    def set_domain_for_categ_id(self):
        # NOTE: @api.depends is for compute methods only - it was removed
        # here since this is an onchange handler, not a computed field.
        categ_ids = self.env["product.public.category"].search(
            [('product_tmpl_ids', 'in', self.product_ids.ids)])
        self.categ_ids = categ_ids