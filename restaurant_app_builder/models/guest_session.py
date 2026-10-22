# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import itertools
from datetime import datetime, date, timedelta
import time
import random
import logging
_logger = logging.getLogger(__name__)
import uuid
import re


class CustomGuestSession(models.Model):
    _name = 'guest.session'
    _description = 'Guest Session'

    session_id = fields.Char(string="Session ID")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_name_ecom = fields.Char(string="Company Name")
    gst_vat = fields.Char(string="Gst vat")
    guest_user_id = fields.Integer(string="Guest USER id")


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def get_res_user_public(self):
        public_user = self.env.ref('base.public_user')
        if public_user:
            return public_user
        else:
            return False

    def create_temp_res_user(self):

        chrs = 'ABCDEFHIJITYDSNCJSUJDBSIBDSJSNOAHaskjdssoibdiusbabcdef0123456789'  # Change your required characters here
        random_key = (''.join(random.choices(chrs, k=15)))
        name = random_key or ''
        email = random_key + "@gmail.com" or ''
        phone = random_key or ''
        # NOTE: 'sel_groups_1_9_10' is an auto-generated pseudo-field name tied
        # to a specific group *category* id in the database it was built
        # against (base.group_user / base.group_portal / base.group_public
        # category, typically). These ids are NOT guaranteed to match across
        # different Odoo 19 databases/installations - if this field name
        # doesn't exist on your res.users in v19, this create() call will
        # raise a ValueError. Prefer setting the group explicitly instead:
        #
        #   portal = self.env['res.users'].sudo().create({
        #       'login': email, 'name': name, 'is_guest_user': True,
        #       'login_mobile': phone,
        #       'group_ids': [(6, 0, [self.env.ref('base.group_public').id])],
        #   })
        portal = self.env['res.users'].sudo().create(
            {'login': email, 'name': name, 'is_guest_user': True,
             'login_mobile': phone,
             'sel_groups_1_9_10': 9})
        return portal