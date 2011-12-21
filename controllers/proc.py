# -*- coding: utf-8 -*-

"""
    Procurement

    A module to handle Procurement

    Currently handles
        Suppliers
        Planned Procurements

    @ToDo: Extend to
        Purchase Requests (PRs)
        Purchase Orders (POs)
"""

module = request.controller
resourcename = request.function

if not deployment_settings.has_module("proc"):
    raise HTTP(404, body="Module disabled: %s" % module)

s3_menu(module)

# Load Models
s3mgr.load("proc_supplier")

# =============================================================================
def index():
    """
        Application Home page
    """

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name
    return dict(module_name=module_name)

# =============================================================================
def supplier():
    """ RESTful CRUD controller """

    return s3_rest_controller(module, resourcename)

# =============================================================================
def plan():
    """ RESTful CRUD controller """

    rheader = response.s3.plan_rheader
    return s3_rest_controller(module, resourcename,
                              rheader=rheader)

# END =========================================================================
