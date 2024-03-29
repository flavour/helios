# -*- coding: utf-8 -*-

"""
    Deployment settings
    All settings which are typically edited for a deployment should be done here
    Deployers shouldn't typically need to edit any other files.
    NOTE FOR DEVELOPERS:
    /models/000_config.py is NOT in the BZR repository, as this file will be changed
    during deployments.
    To for changes to be committed to trunk, please also edit:
    deployment-templates/models/000_config.py
"""

# Remind admin to edit this file
FINISHED_EDITING_CONFIG_FILE = False # change to True after you finish editing this file

# Database settings
deployment_settings.database.db_type = "sqlite"
deployment_settings.database.host = "localhost"
deployment_settings.database.port = None # use default
deployment_settings.database.database = "sahana"
deployment_settings.database.username = "sahana"
deployment_settings.database.password = "password" # NB Web2Py doesn't like passwords with an @ in them
deployment_settings.database.pool_size = 30

# Authentication settings
# This setting should be changed _before_ registering the 1st user
deployment_settings.auth.hmac_key = "akeytochange"
# These settings should be changed _after_ the 1st (admin) user is
# registered in order to secure the deployment
# Should users be allowed to register themselves?
deployment_settings.security.self_registration = True
deployment_settings.auth.registration_requires_verification = True
deployment_settings.auth.registration_requires_approval = True

# Uncomment this to request the Mobile Phone when a user registers
deployment_settings.auth.registration_requests_mobile_phone = False
# Uncomment this to have the Mobile Phone selection during registration be mandatory
#deployment_settings.auth.registration_mobile_phone_mandatory = True
# Uncomment this to request the Organisation when a user registers
#deployment_settings.auth.registration_requests_organisation = True
# Uncomment this to have the Organisation selection during registration be mandatory
#deployment_settings.auth.registration_organisation_mandatory = True
# Uncomment this to have the Organisation input hidden unless the user enters a non-whitelisted domain
#deployment_settings.auth.registration_organisation_hidden = True
# Uncomment this to request an image when users register
#deployment_settings.auth.registration_requests_image = True
# Uncomment this to direct newly-registered users to their volunteer page to be able to add extra details
# NB This requires Verification/Approval to be Off
#deployment_settings.auth.registration_volunteer = True
# Uncomment this to allow users to Login using OpenID
deployment_settings.auth.openid = False
# @ToDo: Extend to all optional Profile settings: Homepage, Twitter, Facebook, Mobile Phone, Image
# Always notify the approver of a new (verified) user, even if the user is automatically approved
deployment_settings.auth.always_notify_approver = False

# Base settings
deployment_settings.base.system_name = T("Interagency Information Sharing")
deployment_settings.base.system_name_short = T("Sahana Eden")

# Set this to the Public URL of the instance
deployment_settings.base.public_url = "http://127.0.0.1:8000"

# Switch to "False" in Production for a Performance gain
# (need to set to "True" again when Table definitions are changed)
deployment_settings.base.migrate = True
# To just create the .table files:
#deployment_settings.base.fake_migrate = True

# Enable/disable pre-population of the database.
# Should be non-zero on 1st_run to pre-populate the database
# - unless doing a manual DB migration
# Then set to zero in Production (to save 1x DAL hit every page)
# NOTE: the web UI will not be accessible while the DB is empty,
# instead run:
#   python web2py.py -N -S eden -M
# to create the db structure, then exit and re-import the data.
# This is a simple status flag with the following meanings
# 0 - No pre-population
# 1 - Base data entered in the database
# 2 - Regression (data used by the regression tests)
# 3 - Scalability testing
# 4-9 Reserved
# 10 - User (data required by the user typically for specialised test)
# 11-19 Reserved
# 20+ Demo (Data required for a default demo)
#     Each subsequent Demos can take any unique number >= 20
#     The actual demo will be defined by the file demo_folders.cfg
deployment_settings.base.prepopulate = 24 # Just HELIOS

# Set this to True to use Content Delivery Networks to speed up Internet-facing sites
deployment_settings.base.cdn = False

# Set this to True to switch to Debug mode
# Debug mode means that uncompressed CSS/JS files are loaded
# JS Debug messages are also available in the Console
# can also load an individual page in debug mode by appending URL with
# ?debug=1
deployment_settings.base.debug = False

# Email settings
# Outbound server
deployment_settings.mail.server = "127.0.0.1:25"
#deployment_settings.mail.tls = True
# Useful for Windows Laptops:
#deployment_settings.mail.server = "smtp.gmail.com:587"
#deployment_settings.mail.tls = True
#deployment_settings.mail.login = "username:password"
# From Address
deployment_settings.mail.sender = "'Sahana' <sahana@your.org>"
# Default email address to which requests to approve new user accounts gets sent
# This can be overridden for specific domains/organisations via the auth_domain table
deployment_settings.mail.approver = "useradmin@your.org"
# Daily Limit on Sending of emails
#deployment_settings.mail.limit = 1000

# Frontpage settings
# RSS feeds
deployment_settings.frontpage.rss = []
#    {"title": "Eden",
#     # Trac timeline
#     "url": "http://eden.sahanafoundation.org/timeline?ticket=on&changeset=on&milestone=on&wiki=on&max=50&daysback=90&format=rss"
#    },
#    {"title": "Twitter",
#     # @SahanaFOSS
#     "url": "http://twitter.com/statuses/user_timeline/96591754.rss"
#     # Hashtag
#     #url: "http://search.twitter.com/search.atom?q=%23eqnz"
#    }
#]

# L10n settings
#deployment_settings.L10n.default_country_code = 1
# Languages used in the deployment (used for Language Toolbar & GIS Locations)
# http://www.loc.gov/standards/iso639-2/php/code_list.php
deployment_settings.L10n.languages = OrderedDict([
    #("ar", T("Arabic")),
    #("zh-cn", T("Chinese (Simplified)")),
    #("zh-tw", T("Chinese (Traditional)")),
    ("en-gb", T("English")),
    ("fr", T("French")),
    #("de", T("German")),
    #("el", T("Greek")),
    #("it", T("Italian")),
    #("ja", T("Japanese")),
    #("ko", T("Korean")),
    #("pt", T("Portuguese")),
    ("pt-br", T("Portuguese (Brazil)")),
    #("ru", T("Russian")),
    ("es", T("Spanish")),
    #("ur", T("Urdu")),
    #("vi", T("Vietnamese")),
])
# Default language for Language Toolbar (& GIS Locations in future)
deployment_settings.L10n.default_language = "en-gb"
# Display the language toolbar
deployment_settings.L10n.display_toolbar = True
# Default timezone for users
deployment_settings.L10n.utc_offset = "UTC +0000"
# Uncomment these to use US-style dates in English (localisations can still convert to local format)
#deployment_settings.L10n.date_format = T("%m-%d-%Y")
#deployment_settings.L10n.time_format = T("%H:%M:%S")
#deployment_settings.L10n.datetime_format = T("%m-%d-%Y %H:%M:%S")
# Religions used in Person Registry
# @ToDo: find a better code
# http://eden.sahanafoundation.org/ticket/594
deployment_settings.L10n.religions = {
    "none":T("none"),
    "christian":T("Christian"),
    "muslim":T("Muslim"),
    "jew":T("Jew"),
    "buddhist":T("Buddhist"),
    "hindu":T("Hindu"),
    "bahai":T("Bahai"),
    "other":T("other")
}
# Make last name in person/user records mandatory
#deployment_settings.L10n.mandatory_lastname = True

# Finance settings
#deployment_settings.fin.currencies = {
#    "USD" :T("United States Dollars"),
#    "EUR" :T("Euros"),
#    "GBP" :T("Great British Pounds")
#}
#deployment_settings.fin.currency_default = "USD" # Dollars
#deployment_settings.fin.currency_writable = False # False currently breaks things

# PDF settings
# Default page size for reports (defaults to A4)
#deployment_settings.base.paper_size = T("Letter")
# Location of Logo used in pdfs headers
#deployment_settings.ui.pdf_logo = "static/img/mylogo.png"

# GIS (Map) settings
# Restrict the Location Selector to just certain countries
# NB This can also be over-ridden for specific contexts later
# e.g. Activities filtered to those of parent Project
#deployment_settings.gis.countries = ["US"]
# Hide the Map-based selection tool in the Location Selector
#deployment_settings.gis.map_selector = False
# Hide LatLon boxes in the Location Selector
#deployment_settings.gis.latlon_selector = False
# Use Building Names as a separate field in Street Addresses?
#deployment_settings.gis.building_name = False
# Display Resources recorded to Admin-Level Locations on the map
# @ToDo: Move into gis_config?
deployment_settings.gis.display_L0 = False
# Currently unused
#deployment_settings.gis.display_L1 = True

# Map settings that relate to locale, such as the number and names of the
# location hierarchy levels, are now in gis_config.  The site-wide gis_config
# will be populated from the settings here.
# @ToDo: Move to 1st_run to avoid confusion
deployment_settings.gis.location_hierarchy = OrderedDict([
    ("L0", T("Country")),
    ("L1", T("State")),
     #("L2", "%s / %s / %s" % (T("County"), T("District")),
    ("L3", "%s / %s / %s" % (T("City"), T("Town"), T("Village"))),
    #("L2", T("City")),
    #("L3", T("Town")),
    #("L4", T("Neighborhood")),
    #("L4", T("Village")),
])
# Maximum hierarchy level to allow for any map configuration.
deployment_settings.gis.max_allowed_hierarchy_level = "L4"
# @ToDo: Move to 1st_run to avoid confusion
deployment_settings.gis.default_symbology = "US"
# Default map configuration values for the site:
# @ToDo: Move this to zzz_1st_run / prepopulate
# @ToDo: Projections & Markers should use UUIDs not IDs
deployment_settings.gis.default_config_values = Storage(
    name = "Site Map Configuration",
    # Where the map is centered:
    lat = "22.593723263",
    lon = "5.28516253",
    # How close to zoom in initially -- larger is closer.
    zoom = 2,
    zoom_levels = 22,
    projection_id = 1,
    marker_id = 1,
    map_height = 600,
    map_width = 1000,
    # Rough bounds for locations, used by onvalidation to filter out lon, lat
    # which are obviously wrong (e.g. missing minus sign) or far outside the
    # intended region.
    min_lon = -180,
    min_lat = -90,
    max_lon = 180,
    max_lat = 90,
    # Optional source of map tiles.
    #wmsbrowser_name = "Web Map Service",
    #wmsbrowser_url = "http://geo.eden.sahanafoundation.org/geoserver/wms?service=WMS&request=GetCapabilities",
    search_level = "L0",
    # Should locations that link to a hierarchy location be required to link
    # at the deepest level? (False means they can have a hierarchy location of
    # any level as parent.)
    strict_hierarchy = False,
    # Should all specific locations (e.g. addresses, waypoints) be required to
    # link to where they are in the location hierarchy?
    location_parent_required = False
)
# Set this if there will be multiple areas in which work is being done,
# and a menu to select among them is wanted. With this on, any map
# configuration that is designated as being available in the menu will appear
#deployment_settings.gis.menu = T("Maps")
# Maximum Marker Size
# (takes effect only on display)
deployment_settings.gis.marker_max_height = 35
deployment_settings.gis.marker_max_width = 30
# Duplicate Features so that they show wrapped across the Date Line?
# Points only for now
# lon<0 have a duplicate at lon+360
# lon>0 have a duplicate at lon-360
deployment_settings.gis.duplicate_features = False
# Mouse Position: 'normal', 'mgrs' or 'off'
deployment_settings.gis.mouse_position = "normal"
# Print Service URL: http://eden.sahanafoundation.org/wiki/BluePrintGISPrinting
#deployment_settings.gis.print_service = "/geoserver/pdf/"
# Do we have a spatial DB available? (currently unused. Will support PostGIS & Spatialite.)
deployment_settings.gis.spatialdb = False
# GeoServer (Currently used by GeoExplorer. Will allow REST control of GeoServer.)
# NB Needs to be publically-accessible URL for querying via client JS
#deployment_settings.gis.geoserver_url = "http://localhost/geoserver"
#deployment_settings.gis.geoserver_username = "admin"
#deployment_settings.gis.geoserver_password = "password"

# Twitter settings:
# Register an app at http://twitter.com/apps
# (select Aplication Type: Client)
# You'll get your consumer_key and consumer_secret from Twitter
# You can keep these empty if you don't need Twitter integration
deployment_settings.twitter.oauth_consumer_key = ""
deployment_settings.twitter.oauth_consumer_secret = ""

# Use 'soft' deletes
deployment_settings.security.archive_not_delete = True

# AAA Settings

# Security Policy
# http://eden.sahanafoundation.org/wiki/S3AAA#System-widePolicy
# 1: Simple (default): Global as Reader, Authenticated as Editor
# 2: Editor role required for Update/Delete, unless record owned by session
# 3: Apply Controller ACLs
# 4: Apply both Controller & Function ACLs
# 5: Apply Controller, Function & Table ACLs
# 6: Apply Controller, Function, Table & Organisation ACLs
# 7: Apply Controller, Function, Table, Organisation & Facility ACLs
#
deployment_settings.security.policy = 5 # Table ACLs
#acl = deployment_settings.aaa.acl
#deployment_settings.aaa.default_uacl =  acl.READ   # User ACL
#deployment_settings.aaa.default_oacl =  acl.CREATE | acl.READ | acl.UPDATE # Owner ACL

# Lock-down access to Map Editing
#deployment_settings.security.map = True
# Allow non-MapAdmins to edit hierarchy locations? Defaults to True if not set.
# (Permissions can be set per-country within a gis_config)
#deployment_settings.gis.edit_Lx = False
# Allow non-MapAdmins to edit group locations? Defaults to False if not set.
#deployment_settings.gis.edit_GR = True
# Note that editing of locations used as regions for the Regions menu is always
# restricted to MapAdmins.

# Audit settings
# We Audit if either the Global or Module asks us to
# (ignore gracefully if module author hasn't implemented this)
# NB Auditing (especially Reads) slows system down & consumes diskspace
#deployment_settings.security.audit_write = False
#deployment_settings.security.audit_read = False

# UI/Workflow options
# Should user be prompted to save before navigating away?
#deployment_settings.ui.navigate_away_confirm = False
# Should user be prompted to confirm actions?
#deployment_settings.ui.confirm = False
# Should potentially large dropdowns be turned into autocompletes?
# (unused currently)
#deployment_settings.ui.autocomplete = True
#deployment_settings.ui.update_label = T("Edit")
# Enable this for a UN-style deployment
deployment_settings.ui.cluster = True
# Enable this to use the label 'Camp' instead of 'Shelter'
deployment_settings.ui.camp = True
# Enable this to change the label for 'Mobile Phone'
#deployment_settings.ui.label_mobile_phone = T("Cell Phone")
# Enable this to change the label for 'Postcode'
#deployment_settings.ui.label_postcode = T("ZIP Code")

# Request
#deployment_settings.req.type_inv_label = T("Donations")
#deployment_settings.req.type_hrm_label = T("Volunteers")
# Allow the status for requests to be set manually,
# rather than just automatically from commitments and shipments
#deployment_settings.req.status_writable = False
#deployment_settings.req.quantities_writable = True
#deployment_settings.req.show_quantity_transit = False
#deployment_settings.req.multiple_req_items = False
#deployment_settings.req.use_commit = False

# Custom Crud Strings for specific req_req types
#deployment_settings.req.req_crud_strings = dict()
#ADD_ITEM_REQUEST = T("Make a Request for Donations")
#LIST_ITEM_REQUEST = T("List Requests for Donations")
# req_req Crud Strings for Item Request (type=1)
#deployment_settings.req.req_crud_strings[1] = Storage(
#    title_create = ADD_ITEM_REQUEST,
#    title_display = T("Request for Donations Details"),
#    title_list = LIST_ITEM_REQUEST,
#    title_update = T("Edit Request for Donations"),
#    title_search = T("Search Requests for Donations"),
#    subtitle_create = ADD_ITEM_REQUEST,
#    subtitle_list = T("Requests for Donations"),
#    label_list_button = LIST_ITEM_REQUEST,
#    label_create_button = ADD_ITEM_REQUEST,
#    label_delete_button = T("Delete Request for Donations"),
#    msg_record_created = T("Request for Donations Added"),
#    msg_record_modified = T("Request for Donations Updated"),
#    msg_record_deleted = T("Request for Donations Canceled"),
#    msg_list_empty = T("No Requests for Donations"))
#ADD_PEOPLE_REQUEST = T("Make a Request for Volunteers")
#LIST_PEOPLE_REQUEST = T("List Requests for Volunteers")
# req_req Crud Strings for People Request (type=3)
#deployment_settings.req.req_crud_strings[3] = Storage(
#    title_create = ADD_PEOPLE_REQUEST,
#    title_display = T("Request for Volunteers Details"),
#    title_list = LIST_PEOPLE_REQUEST,
#    title_update = T("Edit Request for Volunteers"),
#    title_search = T("Search Requests for Volunteers"),
#    subtitle_create = ADD_PEOPLE_REQUEST,
#    subtitle_list = T("Requests for Volunteers"),
#    label_list_button = LIST_PEOPLE_REQUEST,
#    label_create_button = ADD_PEOPLE_REQUEST,
#    label_delete_button = T("Delete Request for Volunteers"),
#    msg_record_created = T("Request for Volunteers Added"),
#    msg_record_modified = T("Request for Volunteers Updated"),
#    msg_record_deleted = T("Request for Volunteers Canceled"),
#    msg_list_empty = T("No Requests for Volunteers"))

# Inventory Management
deployment_settings.inv.collapse_tabs = False
# Use the term 'Order' instead of 'Shipment'
deployment_settings.inv.shipment_name = "order"

# Human Resource Management
#deployment_settings.hrm.email_required = False
# Uncomment to allow hierarchical categories of Skills, which each need their own set of competency levels.
#deployment_settings.hrm.skill_types = True

# Project Tracking
# Uncomment this to show DRR-related categories
#deployment_settings.project.drr = True

# Save Search Widget
deployment_settings.save_search.widget = False

# Terms of Service to be able to Register on the system
#deployment_settings.options.terms_of_service = T("Terms of Service\n\nYou have to be eighteen or over to register as a volunteer.")
# Should we use internal Support Requests?
#deployment_settings.options.support_requests = True

# Comment/uncomment modules here to disable/enable them
# Modules menu is defined in 01_menu.py
deployment_settings.modules = OrderedDict([
    # Core modules which shouldn't be disabled
    ("default", Storage(
            name_nice = "",
            restricted = True, # Use ACLs to control access to this module
            access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
            module_type = 1
        )),
    ("admin", Storage(
            name_nice = T("Administration"),
            description = T("Site Administration"),
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
            module_type = None  # This item is handled separately for the menu
        )),
    ("appadmin", Storage(
            name_nice = T("Administration"),
            description = T("Site Administration"),
            restricted = True,
            module_type = None  # No Menu
        )),
    ("errors", Storage(
            name_nice = T("Ticket Viewer"),
            description = T("Needed for Breadcrumbs"),
            restricted = False,
            module_type = None  # No Menu
        )),
    ("sync", Storage(
            name_nice = T("Synchronization"),
            description = T("Synchronization"),
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
            module_type = None  # This item is handled separately for the menu
        )),
    ("gis", Storage(
            name_nice = T("Map"),
            description = T("Situation Awareness & Geospatial Analysis"),
            restricted = True,
            module_type = 0,
        )),
    ("pr", Storage(
            name_nice = T("Person Registry"),
            description = T("Central point to record details on People"),
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
            module_type = 0
        )),
    ("org", Storage(
            name_nice = T("Organizations"),
            description = T('Lists "who is doing what & where". Allows relief agencies to coordinate their activities'),
            restricted = True,
            module_type = 0
        )),
    # All modules below here should be possible to disable safely
    #("hrm", Storage(
    #        name_nice = T("Staff & Volunteers"),
    #        description = T("Human Resource Management"),
    #        restricted = True,
    #        module_type = 0,
    #    )),
    #("doc", Storage(
    #        name_nice = T("Documents"),
    #        description = T("A library of digital resources, such as photos, documents and reports"),
    #        restricted = True,
    #        module_type = 0,
    #    )),
    #("msg", Storage(
    #        name_nice = T("Messaging"),
    #        description = T("Sends & Receives Alerts via Email & SMS"),
    #        restricted = True,
    #        module_type = None,
    #    )),
    ("supply", Storage(
            name_nice = T("Supply Chain Management"),
            description = T("Used within Inventory Management, Request Management and Asset Management"),
            restricted = True,
            module_type = None, # Not displayed
        )),
    ("inv", Storage(
            name_nice = T("Inventory"),
            description = T("Receiving and Sending Items"),
            restricted = True,
            module_type = 0
        )),
    ("proc", Storage(
            name_nice = T("Procurement"),
            description = T("Ordering & Purchasing of Goods & Services"),
            restricted = True,
            module_type = 0
        )),
    #("asset", Storage(
    #        name_nice = T("Assets"),
    #        description = T("Recording and Assigning Assets"),
    #        restricted = True,
    #        module_type = 5,
    #    )),
    # Vehicle depends on Assets
    #("vehicle", Storage(
    #        name_nice = T("Vehicles"),
    #        description = T("Manage Vehicles"),
    #        restricted = True,
    #        module_type = 10,
    #    )),
    #("req", Storage(
    #        name_nice = T("Requests"),
    #        description = T("Manage requests for supplies, assets, staff or other resources. Matches against Inventories where supplies are requested."),
    #        restricted = True,
    #        module_type = 10,
    #    )),
    #("project", Storage(
    #        name_nice = T("Projects"),
    #        description = T("Tracking of Projects, Activities and Tasks"),
    #        restricted = True,
    #        module_type = 2
    #    )),
    #("survey", Storage(
    #        name_nice = T("Surveys"),
    #        description = T("Create, enter, and manage surveys."),
    #        restricted = True,
    #        module_type = 5,
    #    )),
    #("cr", Storage(
    #        name_nice = T("Shelters"),
    #        description = T("Tracks the location, capacity and breakdown of victims in Shelters"),
    #        restricted = True,
    #        module_type = 10
    #    )),
    #("hms", Storage(
    #        name_nice = T("Hospitals"),
    #        description = T("Helps to monitor status of hospitals"),
    #        restricted = True,
    #        module_type = 10
    #    )),
    #("irs", Storage(
    #        name_nice = T("Incidents"),
    #        description = T("Incident Reporting System"),
    #        restricted = False,
    #        module_type = 10
    #    )),
    #("impact", Storage(
    #        name_nice = T("Impacts"),
    #        description = T("Used by Assess"),
    #        restricted = True,
    #        module_type = None,
    #    )),
    # Assess currently depends on CR, IRS & Impact
    # Deprecated by Surveys module
    #("assess", Storage(
    #        name_nice = T("Assessments"),
    #        description = T("Rapid Assessments & Flexible Impact Assessments"),
    #        restricted = True,
    #        module_type = 10,
    #    )),
    # Scenario depends on HRM
    #("scenario", Storage(
    #        name_nice = T("Scenarios"),
    #        description = T("Define Scenarios for allocation of appropriate Resources (Human, Assets & Facilities)."),
    #        restricted = True,
    #        module_type = 10,
    #    )),
    # Event depends on HRM
    #("event", Storage(
    #        name_nice = T("Events"),
    #        description = T("Activate Events (e.g. from Scenario templates) for allocation of appropriate Resources (Human, Assets & Facilities)."),
    #        restricted = True,
    #        module_type = 10,
    #    )),
    # NB Budget module depends on Project Tracking Module
    # @ToDo: Rewrite in a modern style
    #("budget", Storage(
    #        name_nice = T("Budgeting Module"),
    #        description = T("Allows a Budget to be drawn up"),
    #        restricted = True,
    #        module_type = 10
    #    )),
    # @ToDo: Port these Assessments to the Survey module
    #("building", Storage(
    #        name_nice = T("Building Assessments"),
    #        description = T("Building Safety Assessments"),
    #        restricted = True,
    #        module_type = 10,
    #    )),
    # These are specialist modules
    # Requires RPy2
    #("climate", Storage(
    #    name_nice = T("Climate"),
    #    description = T("Climate data portal"),
    #    restricted = True,
    #    module_type = 10,
    #)),
    #("delphi", Storage(
    #        name_nice = T("Delphi Decision Maker"),
    #        description = T("Supports the decision making of large groups of Crisis Management Experts by helping the groups create ranked list."),
    #        restricted = False,
    #        module_type = 10,
    #    )),
    #("dvi", Storage(
    #       name_nice = T("Disaster Victim Identification"),
    #       description = T("Disaster Victim Identification"),
    #       restricted = True,
    #       module_type = 10,
    #       #access = "|DVI|",      # Only users with the DVI role can see this module in the default menu & access the controller
    #       #audit_read = True,     # Can enable Audit for just an individual module here
    #       #audit_write = True
    #   )),
    #("mpr", Storage(
    #       name_nice = T("Missing Person Registry"),
    #       description = T("Helps to report and search for missing persons"),
    #       restricted = False,
    #       module_type = 10,
    #   )),
    #("fire", Storage(
    #       name_nice = T("Fire Stations"),
    #       description = T("Fire Station Management"),
    #       restricted = True,
    #       module_type = 1,
    #   )),
    #("ocr", Storage(
    #       name_nice = T("Optical Character Recognition"),
    #       description = T("Optical Character Recognition for reading the scanned handwritten paper forms."),
    #       restricted = False,
    #       module_type = 10
    #   )),
    #("patient", Storage(
    #        name_nice = T("Patient Tracking"),
    #        description = T("Tracking of Patients"),
    #        restricted = True,
    #        module_type = 10
    #    )),
    # These modules have very limited functionality
    #("dvr", Storage(
    #        name_nice = T("Disaster Victim Registry"),
    #        description = T("Traces internally displaced people (IDPs) and their needs"),
    #        module_type = 10
    #    )),
    #("flood", Storage(
    #        name_nice = T("Flood Alerts"),
    #        description = T("Flood Alerts show water levels in various parts of the country"),
    #        restricted = False,
    #        module_type = 10
    #    )),
    # @Deprecated by S3Import
    #("importer", Storage(
    #        name_nice = T("Spreadsheet Importer"),
    #        description = T("Used to import data from spreadsheets into the database"),
    #        restricted = False,
    #        module_type = 10,
    #    )),
    #("ticket", Storage(
    #        name_nice = T("Ticketing Module"),
    #        description = T("Master Message Log to process incoming reports & requests"),
    #        restricted = False,
    #        module_type = 10,
    #    )),
    # Vol depends on HRM
    #("vol", Storage(
    #        name_nice = T("Volunteers"),
    #        description = T("A portal for volunteers allowing them to amend their own data & view assigned tasks."),
    #        restricted = True,
    #        module_type = 10,
    #    )),
])
