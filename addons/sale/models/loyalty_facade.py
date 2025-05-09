class LoyaltyManager:
    # Constants for better readability and maintainability
    LOYALTY_POINTS_RATIO = 10  # 1 point per 10 currency units
    LOYALTY_POINTS_EARNED = 'earned'
    LOYALTY_POINTS_REDEEMED = 'redeemed'

    def apply_loyalty_logic(self, order):
        if not order.partner_id:
            return

        partner = order.partner_id
        
        # Calculate loyalty points
        earned = self.calculate_earned_points(order.amount_total)
        redeemable = self.redeem_points(partner, order.loyalty_points_to_redeem)

        # Update order fields with loyalty points
        self.update_order_fields(order, earned, redeemable)

        # Update partner points after redemption
        self.update_partner_points(partner, earned, redeemable)

    def calculate_earned_points(self, amount_total):
        """
        Calculate loyalty points based on the order's total amount.
        1 point per 10 currency units.
        """
        return int(amount_total // self.LOYALTY_POINTS_RATIO)

    def redeem_points(self, partner, points_to_redeem):
        """
        Calculate the number of loyalty points that can be redeemed.
        Redeem only up to the available points or requested amount.
        """
        return min(partner.loyalty_points, points_to_redeem or 0)

    def update_order_fields(self, order, earned, redeemable):
        """
        Update the order with the earned and redeemed loyalty points.
        """
        order.loyalty_points_earned = earned
        order.loyalty_points_redeemed = redeemable

    def update_partner_points(self, partner, earned, redeemable):
        """
        Update the partner's loyalty points balance after redemption.
        """
        partner.loyalty_points += earned - redeemable

