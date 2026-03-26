# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleSale(Document):

    def before_insert(self):
        self.sale_date = frappe.utils.today()

    def validate(self):
        self.fetch_customer_details()
        self.fetch_vehicle_price()
        self.calculate_addons()
        self.calculate_totals()
        self.validate_discount()
        self.calculate_profit()

    def fetch_vehicle_price(self):
        if self.vehicle and not self.selling_price:
            self.selling_price = frappe.db.get_value(
                "Vehicle Inventory",
                self.vehicle,
                "expected_selling_price"
            )

    def calculate_addons(self):
        total = 0

        for row in self.accessories:
            row.total_amount = (row.quantity or 0) * (row.unit_price or 0)
            total += row.total_amount

        self.addons_total = total

    def calculate_totals(self):
        settings = frappe.db.get_value(
            "Dealership Settings",
            None,
            ["documentation_charges", "tax_percentage"],
            as_dict=True
        )

        self.documentation_charges = self.documentation_charges or (settings.documentation_charges if settings else 0)

        self.subtotal = (
            (self.selling_price or 0)
            + (self.documentation_charges or 0)
            + (self.transfer_fees or 0)
            + (self.insurance_charges or 0)
            + (self.addons_total or 0)
        )

        tax_percentage = settings.tax_percentage if settings else 0
        self.tax_amount = (self.subtotal * tax_percentage) / 100

        self.grand_total = (
            self.subtotal
            - (self.discount or 0)
            + self.tax_amount
        )

    def validate_discount(self):
        max_discount = frappe.db.get_single_value(
            "Dealership Settings",
            "max_discount"
        ) or 0

        if (self.discount or 0) > max_discount:
            frappe.throw("Discount exceeds maximum allowed limit!")

    def calculate_profit(self):
        if not self.vehicle:
            return

        investment = frappe.db.get_value(
            "Vehicle Inventory",
            self.vehicle,
            "total_investment"
        ) or 0

        self.profit_margin = (self.selling_price or 0) - investment

        min_profit = frappe.db.get_single_value(
            "Dealership Settings",
            "minimum_profit"
        ) or 0

        if self.profit_margin < min_profit:
            frappe.msgprint("Warning: Profit margin is below minimum!")


    def on_submit(self):
        self.update_vehicle_status("Sold")
        # self.update_customer_history()

    def before_cancel(self):
        if not self.cancel_reason:
            frappe.throw("Cancellation reason is required")

    def on_cancel(self):
        self.update_vehicle_status("Available for Sale")
        # self.revert_customer_history()

    def update_vehicle_status(self, status):
        frappe.db.set_value(
            "Vehicle Inventory",
            self.vehicle,
            "status",
            status
        )