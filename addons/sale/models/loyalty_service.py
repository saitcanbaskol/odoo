from odoo import models, fields, api

class LoyaltyService(models.AbstractModel):
    _name = 'sale.loyalty.service'
    _description = 'Loyalty Service'

    @api.model
    def award_loyalty_points(self, order):
        if order.partner_id:
            points = int(order.amount_total // 1)  # 1 point per €1
            order.partner_id.loyalty_points += points

    @api.model
    def redeem_loyalty_points(self, order):
        if not order.partner_id or order.partner_id.loyalty_points <= 0:
            return

        available_points = order.partner_id.loyalty_points
        max_discount_amount = order.amount_total

        # 1 point = €1 discount, up to amount_total
        discount_to_apply = min(available_points, int(max_discount_amount))

        if discount_to_apply <= 0:
            return

        # Add discount line
        order.write({
            'order_line': [(0, 0, {
                'name': 'Loyalty Points Discount',
                'product_id': self.env.ref('product.product_product_discount').id,
                'product_uom_qty': 1,
                'price_unit': -discount_to_apply,
            })]
        })

        # Deduct used points
        order.partner_id.loyalty_points -= discount_to_apply
