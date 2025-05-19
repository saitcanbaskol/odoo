from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

class TestSaleOrderLoyalty(TransactionCase):

    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, no_reset_password=True))  # prevent password email sending
        self.partner = self.env['res.partner'].sudo().create({
            'name': 'Test Customer',
            'loyalty_points': 50
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'type': 'consu',
        })

    def test_loyalty_points_award_and_redeem(self):
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0
            })],
            'loyalty_points_to_redeem': 20
        })

        sale_order.action_confirm()

        self.assertEqual(sale_order.loyalty_points_earned, 10)  # 100 // 10
        self.assertEqual(sale_order.loyalty_points_redeemed, 20)
        self.assertEqual(sale_order.partner_id.loyalty_points, 40)  # 50 - 20 + 10
