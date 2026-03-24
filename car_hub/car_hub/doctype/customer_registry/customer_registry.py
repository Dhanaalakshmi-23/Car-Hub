# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class CustomerRegistry(Document):

    def validate(self):
        self.set_full_name()
        self.validate_phone()
        self.validate_email()
        self.validate_budget()
        self.validate_referral()
        self.validate_corporate_fields()

    def set_full_name(self):
        self.full_name = f"{self.first_name} {self.last_name or ''}".strip()

    def validate_phone(self):

        if not re.match(r'^\d{10}$', self.phone_number):
            frappe.throw("Phone number must be 10 digits")

        existing = frappe.db.exists("CustomerRegistry", {"phone_number": self.phone_number, "name": ["!=", self.name]})
        if existing:
            frappe.throw("Phone number must be unique")

    def validate_email(self):

        if not re.match(r'^\S+@\S+\.\S+$', self.email_address):
            frappe.throw("Invalid email format")

    def validate_budget(self):
        if self.min_budget and self.max_budget:
            if self.min_budget > self.max_budget:
                frappe.throw("Min Budget cannot be greater than Max Budget")

    def validate_referral(self):
        if self.referral_source == "Referred by Existing Customer":
            if not self.referred_by:
                frappe.throw("Referred By is mandatory for referral source")

    def validate_corporate_fields(self):
        if self.customer_type in ["Corporate Fleet", "Dealer-to-Dealer"]:
            if not self.company_name or not self.gst_number:
                frappe.throw("Company Name and GST Number are mandatory for corporate customers")
