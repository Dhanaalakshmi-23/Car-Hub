# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

# Copyright (c) 2026
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

    def fetch_customer_details(self):
        if self.customer:
            self.customer_name = frappe.db.get_value(
                "Customer Registry", self.customer, "customer_name"
            )

    def validate_dates(self):
        if self.expected_completion_date and self.engagement_date:
            if self.expected_completion_date < self.engagement_date:
                frappe.throw("Expected Completion Date cannot be before Engagement Date")

    def validate_recommendation(self):
        if self.final_recommendations == "Do Not Buy" and not self.reason:
            frappe.throw("Reason is mandatory when recommendation is 'Do Not Buy'")

    def calculate_totals(self):
        self.tax_amount = 0
        self.total_amount = 0

        if self.consulting_fee:
            if self.tax_percentage:
                self.tax_amount = (self.consulting_fee * (self.tax_percentage or 0)) / 100

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
def get_permission_query_conditions(user):
    if "Sales Consultant" in frappe.get_roles(user):
        return f"`tabConsulting Engagement`.assigned_consultant = '{user}'"