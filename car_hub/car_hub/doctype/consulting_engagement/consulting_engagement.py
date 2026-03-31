# Copyright (c) 2026, Dhanaa Lakshmi
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import hashlib
import time

class ConsultingEngagement(Document):

    def autoname(self):
        unique_string = str(time.time()) + (self.customer or "")
        self.name = hashlib.sha256(unique_string.encode()).hexdigest()[:12]

    def validate(self):
        self.fetch_customer_details()
        self.validate_dates()
        self.calculate_totals()
        self.validate_recommendation()
        self.validate_child_table()

    def fetch_customer_details(self):
        if self.customer:
            cus = frappe.get_doc("Customer Registry", self.customer)

            self.customer_name = cus.full_name
            self.phone_number = cus.phone_number

    def validate_dates(self):
        if self.expected_completion_date and self.engagement_date:
            if self.expected_completion_date < self.engagement_date:
                frappe.throw("Expected Completion Date cannot be before Engagement Date")

    def validate_recommendation(self):
        if self.final_recommendations == "Do Not Buy" and not self.reason:
            frappe.throw("Reason is mandatory when recommendation is 'Do Not Buy'")

    def validate_child_table(self):
        for row in self.recommendations:
            if not row.area_of_inspection:
                frappe.throw("Area of Inspection is required in Recommendations")
            if not row.observation:
                frappe.throw("Observation is required in Recommendations")

    def calculate_totals(self):
        self.tax_amount = 0
        self.total_amount = 0

        if self.consulting_fee:
            tax_percentage = self.tax_percentage or 0
            self.tax_amount = (self.consulting_fee * tax_percentage) / 100
            self.total_amount = self.consulting_fee + self.tax_amount

    def on_submit(self):
        self.create_revenue_entry()

    def create_revenue_entry(self):
        revenue = frappe.get_doc({
            "doctype": "Consulting Revenue",
            "consulting_engagement": self.name,
            "customer": self.customer,
            "amount": self.total_amount,
            "date": frappe.utils.today()
        })

        revenue.insert(ignore_permissions=True)