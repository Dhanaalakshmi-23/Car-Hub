# Copyright (c) 2026
import frappe
from frappe.model.document import Document
import re


class CustomerRegistry(Document):

    def autoname(self):
        self.name = frappe.model.naming.make_autoname("CUST-.####")

    def validate(self):
        self.set_full_name()
        self.validate_budget()
        self.validate_referral()
        self.validate_corporate_fields()
        self.update_purchase_summary()

    def set_full_name(self):
        if self.customer_type in ["Corporate Fleet", "Dealer-to-Dealer"]:
            self.full_name = self.company_name
        else:
            first = self.first_name or ""
            last = self.last_name or ""
            self.full_name = f"{first} {last}".strip()

    def validate_budget(self):
        if self.min_budget and self.max_budget:
            if self.min_budget > self.max_budget:
                frappe.throw("Min Budget cannot be greater than Max Budget")

    def validate_referral(self):
        if self.referral_source == "Referred by Existing Customer":
            if not self.referred_by:
                frappe.throw("Referred By is mandatory")

    def validate_corporate_fields(self):
        if self.customer_type in ["Corporate Fleet", "Dealer-to-Dealer"]:
            if not self.company_name or not self.gst_number:
                frappe.throw("Company Name and GST Number are mandatory")

    def update_purchase_summary(self):
        total_purchases = 0
        total_spent = 0

        for row in self.get("purchase_history") or []:
            if row.sale_amount:
                total_purchases += 1
                total_spent += row.sale_amount

        self.total_purchases = total_purchases
        self.total_spent = total_spent

        # Referral bonus (2%)
        if self.referred_by:
            self.referral_bonus = total_spent * 0.02
        else:
            self.referral_bonus = 0