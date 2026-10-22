from datetime import datetime, date
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError


class ColorInfo(models.Model):
    _name = 'color.info'
    _description = 'Color Information'

    name = fields.Char(string='Color Name', help='Name of the color')
    code = fields.Char(string='Color Code', help='Code or identifier for the color')
    backend_config = fields.Selection([
        ('toolbar_color', 'Toolbar Color'),
        ('menu_color', 'Menu Color'),
        ('button_color', 'Button Color'),
        ('background_color', 'Text Color')
        # Add more options as needed
    ], string='Backend Configuration', help='Configuration for the Mobile App backend Color')

    @api.constrains('code')
    def _check_color_code(self):
        for record in self:
            if not record.code or record.code != record.code.upper():
                raise ValidationError(_('Color code must be provided and in uppercase.'))


class AppImageAttachments(models.Model):
    _name = 'app.image.attachments'
    _description = 'App Image Attachments'

    name = fields.Char(string='Attachment Name', help='Name of the image attachment')
    image_type = fields.Selection([
        ('logo', 'App Logo'),
        ('background', 'Background Image'),
        ('splash_screen', 'Splash Screen Image'),
        ('icon', 'Icon Images'),
        ('illustration', 'Illustrations'),
        ('screenshot', 'Screenshots'),
        ('social_media', 'Social Media Images'),
        # Add more options as needed
    ], string='Image Type', required=True, help='Type of image for the app')
    image_data = fields.Binary(string='Image Data', attachment=True, help='Image for the specified type')
    image_data_attachment = fields.Many2one(
        'ir.attachment', string='Image Data Attachment', help='Image attachment record for the specified type')