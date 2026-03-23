# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet

class VehicleClassification(NestedSet):

    def validate(self):
        self.validate_price_range()
        self.validate_leaf_nodes()
        self.validate_group_nodes()
        self.validate_popularity_score()
        self.depreciation_rate()

    def validate_price_range(self):
        if self.min_price and self.max_price:
            if self.min_price > self.max_price:
                frappe.throw("Min Price cannot be greater than Max Price")

    def validate_leaf_nodes(self):
        if not self.is_group:
            if not self.min_price or not self.max_price:
                frappe.throw("Leaf classifications must have Min and Max Price")

    def validate_group_nodes(self):
        if self.is_group:
            if self.min_price or self.max_price:
                frappe.throw("Group (parent) classifications should not have price values")

    def validate_popularity_score(self):
        if self.popularity_score:
            if self.popularity_score < 0 or self.popularity_score > 100:
                frappe.throw("Popularity Score must be between 0 and 100")
                
    def depreciation_rate(self):
        if self.depreciation_rate:
            if self.popularity_score < 0 or self.popularity_score > 100:
                frappe.throw("Popularity Score must be between 0 and 100")
        