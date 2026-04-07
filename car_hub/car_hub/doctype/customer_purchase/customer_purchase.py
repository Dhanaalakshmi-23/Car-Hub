import frappe
from frappe.model.document import Document


class CustomerPurchase(Document):

    def validate(self):
        self.validate_amount()
        self.validate_duplicate_vehicle()

    
    def validate_amount(self):
        if self.sale_amount and self.sale_amount <= 0:
            frappe.throw("Sale Amount must be greater than 0")

    def validate_duplicate_vehicle(self):
        # Prevent selling same registration twice
        if self.registration_number:
            existing = frappe.db.exists("Customer Purchase", {
                "registration_number": self.registration_number,
                "docstatus": ["!=", 2],
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw("This vehicle is already sold")

