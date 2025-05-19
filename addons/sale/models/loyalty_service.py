from odoo import models, fields, api

class LoyaltyService(models.AbstractModel):
    _name = 'sale.loyalty.service'
    _description = 'Loyalty Service'

    @api.model
    def award_loyalty_points(self, order):
        """Award loyalty points to the customer based on the order amount."""
        if order.partner_id:
            points = int(order.amount_total // 10)  # Example: 1 point per €10
            order.partner_id.loyalty_points += points

    @api.model
    def redeem_loyalty_points(self, order):
        """Redeem loyalty points for the order."""
        if order.partner_id and order.partner_id.loyalty_points >= 10:
            discount = 10  # Example: €10 discount for 10 points
            order.amount_total -= discount
            order.partner_id.loyalty_points -= 10
