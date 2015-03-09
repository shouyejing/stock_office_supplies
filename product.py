from openerp import models, fields, api, exceptions, _

class product_template(models.Model):
    _inherit = "product.template"

    borrowable = fields.Boolean(compute="_compute_borrowable")

    @api.depends('categ_id')
    @api.one
    def _compute_borrowable(self):
        if not self.categ_id:
            self.isOfficeSupply = False
        else:
            self.isOfficeSupply = self.categ_id.id == self.env.ref('stock_office_supplies.product_category_office_supply').id