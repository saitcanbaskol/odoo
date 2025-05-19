from odoo.tests.common import TransactionCase

class TestLoyaltyLogic(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Loyal Customer',
            'loyalty_points': 50
        })
        self.product = self.env.ref('product.product_product_1')  # standard demo product

    def test_loyalty_award_and_redeem(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 100,
            })],
            'loyalty_points_to_redeem': 30
        })

        order.action_confirm()

        # Order total = 200, Earned = 200 // 10 = 20
        self.assertEqual(order.loyalty_points_earned, 20)
        self.assertEqual(order.loyalty_points_redeemed, 30)
        self.assertEqual(self.partner.loyalty_points, 40)  # 50 - 30 + 20
