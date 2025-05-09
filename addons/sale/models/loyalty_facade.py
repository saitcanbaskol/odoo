class LoyaltyManager:
    def apply_loyalty_logic(self, order):
        if not order.partner_id:
            return

        partner = order.partner_id

        # Loyalty points earned: 1 point per 10 currency units
        earned = int(order.amount_total // 10)

        # Redeem only up to available points or requested amount
        redeemable = min(partner.loyalty_points, order.loyalty_points_to_redeem or 0)

        # Update order fields
        order.loyalty_points_earned = earned
        order.loyalty_points_redeemed = redeemable

        # Update partner points
        partner.loyalty_points += earned - redeemable

        # Optional: If points reduce total, apply reward logic here
        # order.amount_total -= redeemable * 0.1  # Example logic
