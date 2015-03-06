from openerp import models, fields, api, exceptions, _


class borroworderline(models.Model):
    _name = 'stock_office_supplies.borroworderline'
    borroworder = fields.Many2one('stock_office_supplies.borrow_order')
    product_id = fields.Many2one('product.product',
                                  domain=[("product_tmpl_id.isOfficeSupply", "=", True)])
    quantity = fields.Integer(required=True)


class borroworder(models.Model):
    _inherit = 'mail.thread'
    _name = 'stock_office_supplies.borrow_order'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].get('stock_office_supplies.borrow_order') or '/',
                       copy=False)
    state = fields.Selection([('draft', "Draft"), ('sent', "sent to manager"),
                              ('approved', 'Approved'), ('refused', 'Refused')])
    date = fields.Date(default=fields.Date.today, required=True)
    user = fields.Many2one('res.users', default=lambda self: self.env.user)
    lines = fields.One2many('stock_office_supplies.borroworderline', 'borroworder')
    picking_id = fields.Many2one('stock.picking')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Borrow order name must be unique!'),
    ]

    @api.one
    @api.constrains('lines')
    def _check_lines(self):
        if not self.lines:
            raise exceptions.ValidationError(_("Not borrow order lines!"))

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_sent(self):
        self.state = 'sent'

    @api.one
    def action_approved(self):
        self.state = 'approved'
        if self.lines:
            pick = self.env["stock.picking"].create({"move_type": 'direct',
                                                     "invoice_state": 'none',
                                                     "picking_type_id": self.env.ref("stock_office_supplies.stock_picking_borrow").id,
                                                     "priority": '1',
                                                     "origin": self.name})
            for line in self.lines:
                self.env["stock.move"].create({"name": 'OK',
                    "product_id": line.product_id.id,
                    "product_uom": line.product_id.product_tmpl_id.uom_id.id,
                    "product_uom_qty": line.quantity,
                    "location_dest_id": pick.picking_type_id.default_location_dest_id.id,
                    "location_id": pick.picking_type_id.default_location_src_id.id,
                    "picking_id": pick.id})
            pick.action_confirm()
            self.picking_id = pick.id

    @api.one
    def action_refused(self):
        self.state = 'refused'