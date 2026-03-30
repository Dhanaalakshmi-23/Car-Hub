app_name = "car_hub"
app_title = "Car Hub"
app_publisher = "Dhanaa Lakshmi"
app_description = "Second hand car dealership and consulting platform"
app_email = "dhanaalakshminarayanan@gmail.com"
app_license = "mit"

doc_events = {
    "Vehicle Inventory": {
        "after_insert": "car_hub.car_hub.doctype.vehicle_inventory.vehicle_inventory.after_insert",
        "validate":     "car_hub.car_hub.doctype.vehicle_inventory.vehicle_inventory.validate",
        "before_delete":"car_hub.car_hub.doctype.vehicle_inventory.vehicle_inventory.before_delete",
    },
    "Vehicle Sale": {
        "validate":  "car_hub.car_hub.doctype.vehicle_sale.vehicle_sale.validate",
        "on_submit": "car_hub.car_hub.doctype.vehicle_sale.vehicle_sale.on_submit",
        "on_update": "car_hub.car_hub.doctype.vehicle_sale.vehicle_sale.on_update",
        "on_cancel": "car_hub.car_hub.doctype.vehicle_sale.vehicle_sale.on_cancel",
    },
    "Vehicle Evaluation Task": {
        "validate":  "car_hub.car_hub.doctype.vehicle_evaluation_task.vehicle_evaluation_task.validate",
        "on_update": "car_hub.car_hub.doctype.vehicle_evaluation_task.vehicle_evaluation_task.on_update",
    },
}

scheduler_events = {
    "weekly": [
        "car_hub.car_hub.utils.notifications.send_slow_inventory_report",
    ],
    "daily_long": [
        "car_hub.car_hub.utils.notifications.auto_close_delivered_sales",   # 6 PM
        "car_hub.car_hub.utils.notifications.log_overdue_evaluations",      # 9 AM
    ],
}

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "car_hub",
# 		"logo": "/assets/car_hub/logo.png",
# 		"title": "Car Hub",
# 		"route": "/car_hub",
# 		"has_permission": "car_hub.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/car_hub/css/car_hub.css"
# app_include_js = "/assets/car_hub/js/car_hub.js"

# include js, css files in header of web template
# web_include_css = "/assets/car_hub/css/car_hub.css"
# web_include_js = "/assets/car_hub/js/car_hub.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "car_hub/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "car_hub/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "car_hub.utils.jinja_methods",
# 	"filters": "car_hub.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "car_hub.install.before_install"
# after_install = "car_hub.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "car_hub.uninstall.before_uninstall"
# after_uninstall = "car_hub.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "car_hub.utils.before_app_install"
# after_app_install = "car_hub.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "car_hub.utils.before_app_uninstall"
# after_app_uninstall = "car_hub.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "car_hub.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"car_hub.tasks.all"
# 	],
# 	"daily": [
# 		"car_hub.tasks.daily"
# 	],
# 	"hourly": [
# 		"car_hub.tasks.hourly"
# 	],
# 	"weekly": [
# 		"car_hub.tasks.weekly"
# 	],
# 	"monthly": [
# 		"car_hub.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "car_hub.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "car_hub.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "car_hub.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "car_hub.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["car_hub.utils.before_request"]
# after_request = ["car_hub.utils.after_request"]

# Job Events
# ----------
# before_job = ["car_hub.utils.before_job"]
# after_job = ["car_hub.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"car_hub.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

