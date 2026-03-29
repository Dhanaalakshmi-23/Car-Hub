# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleSale(Document):

    def before_insert(self):
        self.sale_date = frappe.utils.today()
        self.fetch_dealership_details()

    def validate(self):
        self.fetch_vehicle_price()
        self.calculate_addons()
        self.calculate_totals()
        self.validate_discount()
        self.calculate_profit()
        self.check_discount_limit()
    def before_save(self):
        self.handle_discount_workflow()
    def before_submit(self):
        self.prevent_submit_without_approval()

    def fetch_dealership_details(self):
        settings = frappe.get_single("Dealership Settings")

        self.dealership_name = settings.dealership_name
        self.dealership_address = settings.address
        self.dealership_email = settings.system_email
        self.dealership_logo = settings.logo

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
            + (self.transfer_fee or 0)
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
            "max_discount_percent_without_approval"
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


    #Check discount amount
    def check_discount_limit(self):
        max_discount = frappe.db.get_single_value(
            "Dealership Settings", "max_discount_percent_without_approval"
        ) or 0

        if self.discount and self.discount > max_discount:
            if self.workflow_state != "Pending Discount Approval":
                frappe.msgprint(
                    "Discount exceeds allowed limit. Moving to Pending Approval."
                )
    # Handle auto move approval state and notifications
    def handle_discount_workflow(self):
        max_discount = frappe.db.get_single_value(
            "Dealership Settings", "max_discount_percent_without_approval"
        ) or 0

        if self.discount and self.discount > max_discount:

            # Move to Pending Approval
            if self.workflow_state != "Pending Discount Approval":
                self.workflow_state = "Pending Discount Approval"
                self.notify_managers()

        else:
            # If discount corrected, allow back to Draft
            if self.workflow_state == "Pending Discount Approval":
                self.workflow_state = "Draft"

    # prevent submission if discount is not approved
    def prevent_submit_without_approval(self):
        max_discount = frappe.db.get_single_value(
            "Dealership Settings", "max_discount_percent_without_approval"
        ) or 0

        if self.discount and self.discount > max_discount:
            if self.workflow_state != "Draft":
                frappe.throw(
                    "Cannot submit. Discount not approved by Sales Manager."
                )

    # Notify Email to Sales Managers for Approval
    def notify_managers(self):
        managers = frappe.get_all(
            "Has Role",
            filters={"role": "Sales Manager"},
            pluck="parent"
        )

        if not managers:
            return

        for user in managers:
            frappe.sendmail(
                recipients=[user],
                subject="Discount Approval Required",
                message=f"""
                Vehicle Sale <b>{self.name}</b> requires approval.<br><br>
                Discount entered: <b>{self.discount_percentage}%</b><br>
                Please review and approve/reject.
                """
            )
    


    def on_submit(self):
        self.update_vehicle_status("Sold")
        self.update_customer_history()
        self.handle_referral_bonus()
        self.log_profit()

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

    def update_customer_history(self):
        customer = frappe.get_doc("Customer Registry", self.customer)

        customer.append("purchase_history", {
            "vehicle": self.vehicle,
            "date": self.sale_date,
            "sale_amount": self.grand_total
        })

        customer.save(ignore_permissions=True)

    def revert_customer_history(self):
        customer = frappe.get_doc("Customer Registry", self.customer)

        customer.purchase_history = [
            row for row in customer.purchase_history
            if row.vehicle != self.vehicle
        ]

        customer.save(ignore_permissions=True)

    def handle_referral_bonus(self):
        customer = frappe.get_doc("Customer Registry", self.customer)

        if customer.referred_by:
            referrer = frappe.get_doc("Customer Registry", customer.referred_by)

            bonus = self.grand_total * 0.02
            referrer.referral_bonus_earned += bonus

            referrer.save(ignore_permissions=True)

    def reverse_referral_bonus(self):
        customer = frappe.get_doc("Customer Registry", self.customer)

        if customer.referred_by:
            referrer = frappe.get_doc("Customer Registry", customer.referred_by)

            bonus = self.grand_total * 0.02
            referrer.referral_bonus_earned -= bonus

            referrer.save(ignore_permissions=True)

    def log_profit(self):
        frappe.get_doc({
            "doctype": "Profit Log",
            "vehicle_sale": self.name,
            "vehicle": self.vehicle,
            "profit": self.profit_margin
        }).insert(ignore_permissions=True)