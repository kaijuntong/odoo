# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2011 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import tools
from osv import osv
from osv import fields
from tools.translate import _

import io, StringIO
from PIL import Image

class mail_group(osv.osv):
    """
    A mail_group is a collection of users sharing messages in a discussion group.
    Mail groups are different from user groups because they don't have a specific field holding users.
    Group users are users that follow the mail group, using the subscription/follow mechanism of OpenChatter.
    """
    
    _name = 'mail.group'
    _inherit = ['mail.thread']
    
    def action_group_join(self, cr, uid, ids, context={}):
        sub_obj = self.pool.get('mail.subscription')
        menu_values = {'res_model': 'mail.group', 'user_id': uid}
        for id in ids:
            menu_values['res_id'] = id
            sub_id = sub_obj.create(cr, uid, menu_values, context=context)
        
        for group in self.browse(cr, uid, ids, context):
            self.write(cr, uid, group.id, {
                'users': [(4, uid)]
                })
        
        return True
    
    def _get_photo_mini(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if not obj.photo:
                result[obj.id] = False
                continue

            image_stream = io.BytesIO(obj.photo.decode('base64'))
            img = Image.open(image_stream)
            img.thumbnail((120, 100), Image.ANTIALIAS)
            img_stream = StringIO.StringIO()
            img.save(img_stream, "JPEG")
            result[obj.id] = img_stream.getvalue().encode('base64')
        return result
    
    def _set_photo_mini(self, cr, uid, id, name, value, args, context=None):
        self.write(cr, uid, [id], {'photo': value}, context=context)
        return True
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),
        'responsible_id': fields.many2one('res.users', string='Responsible',
                            ondelete='set null', required=True, select=1),
        'public': fields.boolean('Public', help='This group is visible by non members'),
        'photo': fields.binary('Photo'),
        'photo_mini': fields.function(_get_photo_mini, fnct_inv=_set_photo_mini, string='Photo Mini', type="binary",
            store = {
                'mail.group': (lambda self, cr, uid, ids, c={}: ids, ['photo'], 10),
            }),
    }

    _defaults = {
        'public': True,
    }

mail_group()
