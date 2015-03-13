from openerp import models, fields, api, exceptions, _
import xlwt
import StringIO
import base64

class borroworderline(models.Model):
    _name = 'stock_office_supplies.borroworderline'
    borroworder = fields.Many2one('stock_office_supplies.borrow_order')
    product_id = fields.Many2one('product.product', required=True,
                                  domain=[("product_tmpl_id.borrow_ok", "=", True)])
    quantity = fields.Integer(required=True)

    @api.one
    @api.constrains('quantity')
    def _check_quantity(self):
        if self.quantity <= 0:
            raise exceptions.ValidationError(_("Quantity must greater than zero!"))

class borroworder(models.Model):
    _inherit = 'mail.thread'
    _name = 'stock_office_supplies.borrow_order'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].get('stock_office_supplies.borrow_order') or '/',
                       copy=False)
    # name = fields.Char()

    data = fields.Binary()
    filename = fields.Char()

    amount = fields.Float(compute='_compute_amount')
    state = fields.Selection([('draft', "Draft"),
                              ('sent', "sent to manager"),
                              ('first_approved', 'First Approved'),
                              ('approved', 'Approved'),
                              ('transferd', 'Transferd'),
                              ('refused', 'Refused'),
                              ('cancelled', 'Cancelled')])
    date = fields.Date(default=fields.Date.today, required=True,
                       states={'sent': [('readonly', True)],
                               'approved': [('readonly', True)],
                               'transferd': [('readonly', True)],
                               'refused': [('readonly', True)],
                               'cancelled': [('readonly', True)]})
    user = fields.Many2one('res.users', default=lambda self: self.env.user, required=True,
                           states={'sent': [('readonly', True)],
                               'approved': [('readonly', True)],
                               'transferd': [('readonly', True)],
                               'refused': [('readonly', True)],
                               'cancelled': [('readonly', True)]})
    lines = fields.One2many('stock_office_supplies.borroworderline', 'borroworder',
                            states={'sent': [('readonly', True)],
                               'approved': [('readonly', True)],
                               'transferd': [('readonly', True)],
                               'refused': [('readonly', True)],
                               'cancelled': [('readonly', True)]})
    picking_id = fields.Many2one('stock.picking', readonly=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Borrow order name must be unique!'),
    ]

    @api.depends('lines')
    @api.one
    def _compute_amount(self):
        amount = 0
        for line in self.lines:
            if line.product_id:
                amount += line.product_id.product_tmpl_id.standard_price * line.quantity
        self.amount = amount

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
    def action_first_approved(self):
        self.state = 'first_approved'

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

    @api.one
    def action_cancel(self):
        self.state = 'cancelled'

    @api.one
    def action_transferd(self):
        self.state = 'transferd'

    @api.one
    def generate_xls_file(self):
        wbk = xlwt.Workbook()
        sheet1 = wbk.add_sheet('my sheet')
        sheet2 = wbk.add_sheet('my sheet2')


        file_data = StringIO.StringIO()
        o = wbk.save(file_data)
        out = base64.encodestring(file_data.getvalue())
        self.data = out
        self.filename = "myxls.xls"

    # @api.one
    # @api.returns('self')
    # def create(self):
    #     self.name = self.env['ir.sequence'].get('stock_office_supplies.borrow_order') or '/'
    #     super(borroworder, self).create()
    #     return self

# class picking(models.Model):
#     _inherit = 'stock.picking'
#
#     @api.one


class producttemplate(models.Model):
    _inherit = 'product.template'

    # borrow_ok = fields.Boolean('can be borrowed')

    borrow_ok = fields.Boolean(compute="_compute_borrowable", store=True)

    @api.depends('categ_id')
    @api.one
    def _compute_borrowable(self):
        if not self.categ_id:
            self.borrow_ok = False
        else:
            self.borrow_ok = self.categ_id.id == self.env.ref('stock_office_supplies.product_category_office_supply').id
