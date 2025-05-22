from odoo.tests.common import TransactionCase
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestLoyaltyService(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
            'loyalty_points': 0,
        })

        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'standard_price': 50.0,
            'type': 'consu',
        })
        self.discount_product = self.env['product.product'].create({
            'name': 'Loyalty Discount Product',
            'type': 'service',
            'list_price': 0.0,
            'standard_price': 0.0,
        })

        # Register it with XML ID so `self.env.ref(...)` works
        self.env['ir.model.data'].create({
            'name': 'product_product_discount',
            'model': 'product.product',
            'module': 'product',
            'res_id': self.discount_product.id,
        })


    def _create_order(self, partner, price=100.0):
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': price,
            })],
        })

    def test_award_loyalty_points_on_order(self):
        order = self._create_order(self.partner)
        order.action_confirm()
        self.partner.invalidate_recordset()
        self.assertGreater(self.partner.loyalty_points, 0, "Points not awarded")

    def test_redeem_loyalty_points(self):
        self.partner.loyalty_points = 100

        order = self._create_order(self.partner, price=111.0)
        order.action_confirm()
        self.partner.invalidate_recordset()

        # Check that a discount line was added (price_unit < 0)
        discount_lines = order.order_line.filtered(lambda l: l.price_unit < 0)
        self.assertTrue(discount_lines, "No loyalty discount line was added")


        # Check that points were used (i.e. dropped before awarding new ones)
        self.assertLessEqual(self.partner.loyalty_points, 111, "Points not correctly redeemed and re-added")


    

