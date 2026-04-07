# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import re

import frappe
from frappe.model.document import Document


class SellerRegistry(Document):
    def validate(self):
        self.validate_id_proof()
        self.validate_phone()

    def validate_id_proof(self):
        if self.seller_type != "Individual Owner":
            return

        if not self.id_proof_type or not self.id_proof_number:
            frappe.throw("ID Proof Type and Number are mandatory for Individual Owner")

        id_number = self.id_proof_number.strip()

        if self.id_proof_type == "Aadhar":
            if not re.fullmatch(r"\d{12}", id_number):
                frappe.throw("Aadhar must be exactly 12 digits")

        elif self.id_proof_type == "PAN":
            if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", id_number):
                frappe.throw("Invalid PAN format (Example: ABCDE1234F)")

        elif self.id_proof_type == "Driving License":
            if not re.fullmatch(r"[A-Z]{2}\d{2}\d{4}\d{7}", id_number.replace(" ", "")):
                frappe.throw("Invalid Driving License format")

        elif self.id_proof_type == "Passport":
            if not re.fullmatch(r"[A-Z][0-9]{7}", id_number):
                frappe.throw("Invalid Passport format (Example: A1234567)")

    def validate_phone(self):
        if self.phone_number:
            if not re.match(r"^[0-9]{10}$", self.phone_number):
                frappe.throw("Phone number must be exactly 10 digits")


