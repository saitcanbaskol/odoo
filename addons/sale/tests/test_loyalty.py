from odoo.tests.common import TransactionCase


class TestLoyaltyService(TransactionCase):

    def setUp(self):
        super().setUp()

        # Create test partner with existing loyalty points
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'loyalty_points': 40,
        })

        # Use a demo product or create a new one
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100,
            'standard_price': 50,
            'type': 'consu',
        })

    def test_loyalty_points_awarded_on_order(self):
        """Test that loyalty points are awarded correctly based on order total"""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 3,
                'price_unit': 100,
            })],
        })

        order.action_confirm()

        # 3 * 100 = 300, should award 30 points if 10:1 ratio
        self.assertEqual(order.loyalty_points_earned, 30)
        self.assertEqual(order.loyalty_points_redeemed, 0)
        self.assertEqual(self.partner.loyalty_points, 70)  # 40 + 30

    def test_loyalty_points_redeemed_on_order(self):
        """Test that loyalty points are redeemed correctly and net result is correct"""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 120,
            })],
            'loyalty_points_to_redeem': 20,
        })

        order.action_confirm()

        # Order total = 240 → Earn 24, Redeem 20 → Net +4
        self.assertEqual(order.loyalty_points_earned, 24)
        self.assertEqual(order.loyalty_points_redeemed, 20)
        self.assertEqual(self.partner.loyalty_points, 44)  # 40 - 20 + 24

    def test_redeem_more_than_available(self):
        """Redemption should not exceed available points"""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 100,
            })],
            'loyalty_points_to_redeem': 100,  # More than partner's 40
        })

        order.action_confirm()

        # Should cap redemption at 40, earn 10 (100//10), net = 10
        self.assertEqual(order.loyalty_points_redeemed, 40)
        self.assertEqual(order.loyalty_points_earned, 10)
        self.assertEqual(self.partner.loyalty_points, 10)  # 40 - 40 + 10
