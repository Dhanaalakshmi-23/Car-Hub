# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from car_hub.utils.notifications import notify_sale_submitted,notify_documentation_in_progress, notify_vehicle_delivered,notify_sale_cancelled,notify_discount_approval_needed
from frappe.utils.data import today


class VehicleSale(Document):

    def before_insert(self):
        self.sale_date = frappe.utils.today()
        self.fetch_dealership_details()

    def validate(self):
        # settings = frappe.get_single("Dealership Settings")

        # if self.discount_percentage > settings.max_discount_percent:
        #     if self.workflow_state != "Pending Discount Approval":
        #         frappe.throw("Discount exceeds limit. Request approval first.")

        #     if self.approval_status != "Approved":
        #         frappe.throw("Discount not approved by Sales Manager.")
        self.fetch_vehicle_price()
        self.calculate_addons()
        self.calculate_totals()
        self.validate_discount()
        self.calculate_profit()

    def before_submit(self):
        self.prevent_submit_without_approval()

    def on_update(self):
        if self.workflow_state == "Pending Discount Approval":
            notify_documentation_in_progress(self.name)
        if self.status == "Delivered":
            if not self.delivery_date:
                self.db_set("delivery_date", today())
            notify_vehicle_delivered(self.name)
    def fetch_dealership_details(self):
        settings = frappe.get_single("Dealership Settings")

        self.dealership_name = settings.dealership_name
        self.dealership_address = settings.address
        self.dealership_email = settings.system_email
        self.dealership_logo = settings.logo
        self.warranty_statement = settings.warranty_days

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

        self.accessories_total = total

    def calculate_totals(self):
        settings = frappe.db.get_value(
            "Dealership Settings",
            None,
            ["documentation_charges", "tax_percentage"],
            as_dict=True
        )

        self.documentation_charges = float(self.documentation_charges or settings.default_documentation_charges or 0)
        self.selling_price = float(self.selling_price or 0)
        self.transfer_fee = float(self.transfer_fee or 0)
        self.insurance_charges = float(self.insurance_charges or 0)
        self.accessories_total = float(self.accessories_total or 0)
        self.discount = float(self.discount_percentage or 0)

        self.subtotal = (
            self.selling_price
            + self.documentation_charges
            + self.transfer_fee
            + self.insurance_charges
            + self.accessories_total
        )

        tax_percentage = float(settings.tax_percentage or 0)
        self.tax_amount = (self.subtotal * tax_percentage) / 100

        self.grand_total = (
            self.subtotal
            - self.discount
            + self.tax_amount
        )

    def validate_discount(self):
        max_discount = frappe.db.get_single_value(
            "Dealership Settings",
            "max_discount_percent_without_approval"
        ) or 0

        # Only block DIRECT submit (not workflow)
        if self.discount and self.discount > max_discount:
            if self.workflow_state == "Draft":
                frappe.msgprint(
                    "Discount exceeds allowed limit. Please request approval."
                )
        discount_amount = getattr(self, "discount_amount", 0)
        discount_pct = self.discount
        notify_discount_approval_needed(self.name, discount_amount, discount_pct)
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
            "minimum_profit_margin"
        ) or 0

        if self.profit_margin < min_profit:
            frappe.msgprint("Warning: Profit margin is below minimum!")



    # prevent submission if discount is not approved
    def prevent_submit_without_approval(self):
        max_discount = frappe.db.get_single_value(
            "Dealership Settings",
            "max_discount_percent_without_approval"
        ) or 0

        if self.discount and self.discount > max_discount:
            frappe.throw(
                "Cannot submit. Discount requires manager approval."
            )


    def on_submit(self):
        self.update_vehicle_status("Sold")
        self.update_customer_history()
        self.handle_referral_bonus()
        self.log_profit()
        notify_sale_submitted(self.name) #Notification-2

    def before_cancel(self):
        if not self.cancel_reason:
            frappe.throw("Cancellation reason is required")

    def on_cancel(self):
        self.update_vehicle_status("Available for Sale")
        notify_sale_cancelled(self.name)

        # self.revert_customer_history()

    def update_vehicle_status(self, status):
        frappe.db.set_value(
            "Vehicle Inventory",
            self.vehicle,
            "status",
            status
        )

    def update_customer_history(self):
        if not self.customer:
            return

        customer = frappe.get_doc("Customer Registry", self.customer)

        customer.append("purchase_history", {
            "vehicle": self.vehicle,
            "purchase_date": self.sale_date,
            "sale_amount": self.grand_total
        })

        customer.save(ignore_permissions=True)

    def revert_customer_history(self):
        if not self.customer:
            return

        rows = frappe.get_all(
            "Customer Purchase History",
            filters={
                "parent": self.customer,
                "vehicle": self.vehicle
            },
            pluck="name"
        )

        for row in rows:
            frappe.db.delete("Customer Purchase History", row)

    def handle_referral_bonus(self):
        if not self.customer:
            return

        referrer = frappe.db.get_value(
            "Customer Registry",
            self.customer,
            "referred_by"
        )

        if referrer:
            bonus = self.grand_total * 0.02

            current_bonus = frappe.db.get_value(
                "Customer Registry",
                referrer,
                "referral_bonus_earned"
            ) or 0

            frappe.db.set_value(
                "Customer Registry",
                referrer,
                "referral_bonus_earned",
                current_bonus + bonus
            )

    def reverse_referral_bonus(self):
        if not self.customer:
            return

        referrer = frappe.db.get_value(
            "Customer Registry",
            self.customer,
            "referred_by"
        )

        if referrer:
            bonus = self.grand_total * 0.02

            current_bonus = frappe.db.get_value(
                "Customer Registry",
                referrer,
                "referral_bonus_earned"
            ) or 0

            frappe.db.set_value(
                "Customer Registry",
                referrer,
                "referral_bonus_earned",
                current_bonus - bonus
            )

    def log_profit(self):
        frappe.get_doc({
            "doctype": "Profit Log",
            "vehicle_sale": self.name,
            "vehicle": self.vehicle,
            "profit": self.profit_margin
        }).insert(ignore_permissions=True)
def get_permission_query_conditions(user):
    if "Sales Consultant" in frappe.get_roles(user):
        return f"`tabVehicle Sale`.assigned_consultant = '{user}'"