from odoo import api, fields, models, tools, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError, RedirectWarning, UserError
import pyotp
import contextlib
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # NOTE: 'cart_chekouted' is also defined on sale.order in
    # 01_payment_type.py with the same type/default. Having the same field
    # declared in two different Python files that both extend sale.order
    # isn't a hard error (Odoo merges them), but it's redundant and confusing
    # to maintain - keep the definition in one place only.
    guest_checkout = fields.Boolean(string="Guest Checkout")
    guest_user_id = fields.Integer(string="Guest USER id")
    delivery_date = fields.Date(string="Delivery date")
    transaction_id = fields.Char(string="Payment Reference")
    order_platform = fields.Selection([('web', 'Website'), ('Android', 'Android'), ('ios', 'IOS')], 'Order platform')
    payment_type = fields.Selection([('card', 'Card'), ('COD', 'Cash on Delivery'), ('online', 'Online')],
                                     'Payment type')
    client_order_ref = fields.Char('Order Note')
    marketplace_state = fields.Selection(
        [("new", "New"), ("approved", "Approved"), ("processing", "Processing"), ("shipped", "Shipped"),
         ("delivered", "Delivered"), ("cancel", "Cancelled")], default="new", copy=False, tracking=True)

    def mark_deleted(self):
        self.unlink()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_note = fields.Char(string="Product Description")