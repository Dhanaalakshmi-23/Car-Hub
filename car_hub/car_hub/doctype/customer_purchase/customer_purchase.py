import frappe
from frappe.model.document import Document


class CustomerPurchase(Document):

    def validate(self):
        self.validate_customer()
        self.validate_amount()
        self.validate_duplicate_vehicle()

    def validate_customer(self):
        if not self.customer:
            frappe.throw("Customer is mandatory")

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

    def on_submit(self):
        self.add_to_customer_history()

    def add_to_customer_history(self):
        customer_doc = frappe.get_doc("Customer Registry", self.customer)

        customer_doc.append("purchase_history", {
            "vehicle": self.vehicle,  # Link → Vehicle Classification
            "vehicle_model": self.vehicle_model,
            "registration_number": self.registration_number,
            "purchase_date": self.purchase_date,
            "sale_amount": self.sale_amount
        })

        customer_doc.save(ignore_permissions=True)

    def on_cancel(self):
        self.remove_from_customer_history()

    def remove_from_customer_history(self):
        customer_doc = frappe.get_doc("Customer Registry", self.customer)

        updated_rows = []

        for row in customer_doc.purchase_history:
            if not (
                row.registration_number == self.registration_number
            ):
                updated_rows.append(row)

        customer_doc.purchase_history = updated_rows
        customer_doc.save(ignore_permissions=True)