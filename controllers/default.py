# -*- coding: utf-8 -*-

"""
    Default Controllers

    @author: Fran Boon
"""

module = "default"
resourcename = request.function

# Options Menu (available in all Functions' Views)
# - can Insert/Delete items from default menus within a function, if required.
if auth.is_logged_in():
    s3_menu(module)

# -----------------------------------------------------------------------------
def call():
    "Call an XMLRPC, JSONRPC or RSS service"
    # If webservices don't use sessions, avoid cluttering up the storage
    #session.forget()
    return service()

# -----------------------------------------------------------------------------
def download():
    """ Download a file """

    # Load the Models
    # @ToDo: Make this just load the relevant models
    s3mgr.model.load_all_models()

    return response.download(request, db)

# =============================================================================
def register_validation(form):
    """ Validate the fields in registration form """
    # Mobile Phone
    if "mobile" in form.vars and form.vars.mobile:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(form.vars.mobile):
            form.errors.mobile = T("Invalid phone number")
    elif deployment_settings.get_auth_registration_mobile_phone_mandatory():
        form.errors.mobile = T("Phone number is required")
    return

# -----------------------------------------------------------------------------
def register_onaccept(form):
    """ Tasks to be performed after a new user registers """
    # Add newly-registered users to Person Registry, add 'Authenticated' role
    # If Organisation is provided, then: add HRM record & add to 'Org_X_Access' role
    person = auth.s3_register(form)

    if deployment_settings.has_module("delphi"):
        # Add user as a participant of the default problem group
        query = (db.pr_person.id == person) & \
            (db.pr_person.uuid == auth.settings.table_user.person_uuid)
        user_id = db(query).select(db.auth_user.id,
                                   limitby=(0, 1)).first().id
        s3mgr.load("delphi_group")
        table = db.delphi_group
        query = (table.deleted == False)
        group = db(query).select(table.id,
                                 limitby=(0, 1)).first()
        if group:
            table = db.delphi_membership
            table.insert(group_id=group.id,
                         user_id=user_id,
                         status=3)

# -----------------------------------------------------------------------------
auth.settings.register_onvalidation = register_validation
auth.settings.register_onaccept = register_onaccept

_table_user = auth.settings.table_user
_table_user.first_name.label = T("First Name")
_table_user.first_name.comment = SPAN("*", _class="req")
_table_user.last_name.label = T("Last Name")
if deployment_settings.get_L10n_mandatory_lastname():
    _table_user.last_name.comment = SPAN("*", _class="req")
_table_user.email.label = T("E-mail")
_table_user.email.comment = SPAN("*", _class="req")
_table_user.password.comment = SPAN("*", _class="req")
_table_user.language.label = T("Language")
_table_user.language.comment = DIV(_class="tooltip",
                                   _title="%s|%s" % (T("Language"),
                                                     T("The language you wish the site to be displayed in.")))
_table_user.language.represent = lambda opt: s3_languages.get(opt, UNKNOWN_OPT)

# Photo widget
if not deployment_settings.get_auth_registration_requests_image():
    _table_user.image.readable = _table_user.image.writable = False
else:
    _table_user.image.comment = DIV(_class="stickytip",
                                     _title="%s|%s" % (T("Image"),
                                                       T("You can either use %(gravatar)s or else upload a picture here. The picture will be resized to 50x50.") % \
                                                        dict(gravatar = A("Gravatar",
                                                                          _target="top",
                                                                          _href="http://gravatar.com"))))

# Organisation widget for use in Registration Screen
# NB User Profile is only editable by Admin - using User Management
org_widget = IS_ONE_OF(db, "org_organisation.id",
                       organisation_represent,
                       orderby="org_organisation.name",
                       sort=True)
if deployment_settings.get_auth_registration_organisation_mandatory():
    _table_user.organisation_id.requires = org_widget
else:
    _table_user.organisation_id.requires = IS_NULL_OR(org_widget)

# For the User Profile:
_table_user.utc_offset.comment = DIV(_class="tooltip",
                                     _title="%s|%s" % (auth.messages.label_utc_offset,
                                                       auth.messages.help_utc_offset))
_table_user.organisation_id.represent = organisation_represent
_table_user.organisation_id.comment = DIV(_class="tooltip",
                                          _title="%s|%s|%s" % (T("Organization"),
                                                               T("The default Organization for whom you are acting."),
                                                               T("This setting can only be controlled by the Administrator.")))

_table_user.site_id.represent = org_site_represent
_table_user.site_id.comment = DIV(_class="tooltip",
                                  _title="%s|%s|%s" % (T("Facility"),
                                                       T("The default Facility for which you are acting."),
                                                       T("This setting can only be controlled by the Administrator.")))

# =============================================================================
def index():
    """ Main Home Page """

    if auth.is_logged_in():
        redirect(URL(f="item_entity"))

    title = deployment_settings.get_system_name()
    response.title = title

    datatable_ajax_source = ""
    # Check logged in AND permissions
    if AUTHENTICATED in session.s3.roles and \
       auth.s3_has_permission("read", db.org_organisation):
        org_items = organisation()
        datatable_ajax_source = "/%s/default/organisation.aaData" % \
                                request.application
        response.s3.actions = None
        response.view = "default/index.html"
        auth.permission.controller = "org"
        auth.permission.function = "site"
        permitted_facilities = auth.permission.permitted_facilities(redirect_on_error=False)
        manage_facility_box = ""
        if permitted_facilities:
            facility_list = s3_represent_facilities(db, permitted_facilities,
                                                    link=False)
            facility_opts = [OPTION(opt[1], _value = opt[0])
                             for opt in facility_list]
            if facility_list:
                manage_facility_box = DIV(H3(T("Jump to Office")),
                                    SELECT(_id = "manage_facility_select",
                                            _style = "max-width:400px;",
                                            *facility_opts
                                            ),
                                    A(T("Go"),
                                        _href = URL(c="default", f="office",
                                                    args=[facility_list[0][0]]),
                                        #_disabled = "disabled",
                                        _id = "manage_facility_btn",
                                        _class = "action-btn"
                                        ),
                                    _id = "manage_facility_box",
                                    _class = "menu_box fleft")
                response.s3.jquery_ready.append( """
$('#manage_facility_select').change(function() {
    $('#manage_facility_btn').attr('href', S3.Ap.concat('/default/office/',  $('#manage_facility_select').val()));
})""" )
            else:
                manage_facility_box = DIV()

    else:
        manage_facility_box = ""

    # @ToDo: Replace this with an easily-customisable section on the homepage
    #settings = db(db.s3_setting.id == 1).select(limitby=(0, 1)).first()
    #if settings:
    #    admin_name = settings.admin_name
    #    admin_email = settings.admin_email
    #    admin_tel = settings.admin_tel
    #else:
    #    # db empty and prepopulate is false
    #    admin_name = T("Sahana Administrator").xml(),
    #    admin_email = "support@Not Set",
    #    admin_tel = T("Not Set").xml(),

    # Login/Registration forms
    self_registration = deployment_settings.get_security_self_registration()
    registered = False
    login_form = None
    login_div = None
    register_form = None
    register_div = None
    if AUTHENTICATED not in session.s3.roles:
        # This user isn't yet logged-in
        if request.cookies.has_key("registered"):
            # This browser has logged-in before
            registered = True

        # Provide a login box on front page
        request.args = ["login"]
        auth.messages.submit_button = T("Login")
        login_form = auth()
        login_div = DIV(H3(T("Login")),
                        P(XML("%s <b>%s</b> %s" % (T("Registered users can"),
                                                   T("login"),
                                                   T("to access the system")))))

        if self_registration:
            # Provide a Registration box on front page
            request.args = ["register"]
            if deployment_settings.get_terms_of_service():
                auth.messages.submit_button = T("I accept. Create my account.")
            else:
                auth.messages.submit_button = T("Register")
            register_form = auth()
            register_div = DIV(H3(T("Register")),
                               P(XML("%s <b>%s</b>" % (T("If you would like to help, then please"),
                                                       T("sign-up now")))))

             # Add client-side validation
            s3_register_validation()

            if session.s3.debug:
                response.s3.scripts.append( "%s/jquery.validate.js" % s3_script_dir )
            else:
                response.s3.scripts.append( "%s/jquery.validate.min.js" % s3_script_dir )
            if request.env.request_method == "POST":
                post_script = """// Unhide register form
    $('#register_form').removeClass('hide');
    // Hide login form
    $('#login_form').addClass('hide');"""
            else:
                post_script = ""
            register_script = """
    // Change register/login links to avoid page reload, make back button work.
    $('#register-btn').attr('href', '#register');
    $('#login-btn').attr('href', '#login');
    %s
    // Redirect Register Button to unhide
    $('#register-btn').click(function() {
        // Unhide register form
        $('#register_form').removeClass('hide');
        // Hide login form
        $('#login_form').addClass('hide');
    });

    // Redirect Login Button to unhide
    $('#login-btn').click(function() {
        // Hide register form
        $('#register_form').addClass('hide');
        // Unhide login form
        $('#login_form').removeClass('hide');
    });""" % post_script
            response.s3.jquery_ready.append(register_script)

    if deployment_settings.frontpage.rss:
        response.s3.external_stylesheets.append( "http://www.google.com/uds/solutions/dynamicfeed/gfdynamicfeedcontrol.css" )
        response.s3.scripts.append( "http://www.google.com/jsapi?key=notsupplied-wizard" )
        response.s3.scripts.append( "http://www.google.com/uds/solutions/dynamicfeed/gfdynamicfeedcontrol.js" )
        counter = 0
        feeds = ""
        for feed in deployment_settings.frontpage.rss:
            counter += 1
            feeds = "".join((feeds,
                             "{title: '%s',\n" % feed["title"],
                             "url: '%s'}" % feed["url"]))
            # Don't add a trailing comma for old IEs
            if counter != len(deployment_settings.frontpage.rss):
                feeds += ",\n"
        feed_control = "".join(("""
function LoadDynamicFeedControl() {
  var feeds = [
    """, feeds, """
  ];
  var options = {
    // milliseconds before feed is reloaded (5 minutes)
    feedCycleTime : 300000,
    numResults : 5,
    stacked : true,
    horizontal : false,
    title : '""", str(T("News")), """'
  };
  new GFdynamicFeedControl(feeds, 'feed-control', options);
}
// Load the feeds API and set the onload callback.
google.load('feeds', '1');
google.setOnLoadCallback(LoadDynamicFeedControl);"""))
        response.s3.js_global.append( feed_control )

    return dict(title = title,

                #sit_dec_res_box = sit_dec_res_box,
                #facility_box = facility_box,
                manage_facility_box = manage_facility_box,
                #org_box = org_box,

                #r = None, # Required for dataTable to work
                #datatable_ajax_source = datatable_ajax_source,
                #admin_name=admin_name,
                #admin_email=admin_email,
                #admin_tel=admin_tel,
                self_registration=self_registration,
                registered=registered,
                login_form=login_form,
                login_div=login_div,
                register_form=register_form,
                register_div=register_div
                )

# -----------------------------------------------------------------------------
def organisation():
    """
        Function to handle pagination for the org list on the homepage
        - this is overridden in HELIOS by new function lower down!
    """

    table = db.org_organisation
    table.id.label = T("Organization")
    table.id.represent = organisation_represent

    response.s3.dataTable_sPaginationType = "two_button"
    response.s3.dataTable_sDom = "rtip" #"frtip" - filter broken
    response.s3.dataTable_iDisplayLength = 25

    s3mgr.configure("org_organisation",
                    listadd = False,
                    addbtn = True,
                    super_entity = db.pr_pentity,
                    linkto = "/%s/org/organisation/%s" % (request.application,
                                                          "%s"),
                    list_fields = ["id",])

    return s3_rest_controller("org", resourcename)
# -----------------------------------------------------------------------------
def site():
    """
        @todo: Avoid redirect
    """
    if len(request.args):
        site_id = request.args[0]
        site_r = db.org_site[site_id]
        tablename = site_r.instance_type
        query = (db[tablename].site_id == site_id)
        id = db(query).select(db[tablename].id,
                              limitby = (0, 1)).first().id
        cf = tablename.split("_", 1)
        redirect(URL(c = cf[0],
                     f = cf[1],
                     args = [id]))
    else:
        raise HTTP(404)

# -----------------------------------------------------------------------------
def message():
    #if "verify_email_sent" in request.args:
    title = T("Account Registered - Please Check Your Email")
    message = T( "%(system_name)s has sent an email to %(email)s to verify your email address.\nPlease check your email to verify this address. If you do not receive this email please check you junk email or spam filters." )\
                 % {"system_name": deployment_settings.get_system_name(),
                    "email": request.vars.email}
    image = "email_icon.png"
    return dict(title = title,
                message = message,
                image_src = "/%s/static/img/%s" % (request.application, image)
                )

# -----------------------------------------------------------------------------
def rapid():
    """ Set/remove rapid data entry flag """

    val = request.vars.get("val", True)
    if val == "0":
        val = False
    else:
        val = True
    session.s3.rapid_data_entry = val

    response.view = "xml.html"
    return dict(item=str(session.s3.rapid_data_entry))

# -----------------------------------------------------------------------------
def user():
    "Auth functions based on arg. See gluon/tools.py"

    auth.settings.on_failed_authorization = URL(f="error")

    _table_user = auth.settings.table_user
    if request.args and request.args(0) == "profile":
        #_table_user.organisation.writable = False
        _table_user.utc_offset.readable = True
        _table_user.utc_offset.writable = True

    login_form = register_form = None
    if request.args and request.args(0) == "login":
        auth.messages.submit_button = T("Login")
        form = auth()
        login_form = form
        if s3.crud.submit_style:
            form[0][-1][1][0]["_class"] = s3.crud.submit_style
    elif request.args and request.args(0) == "register":
        if deployment_settings.get_terms_of_service():
            auth.messages.submit_button = T("I accept. Create my account.")
        else:
            auth.messages.submit_button = T("Register")
        # Default the profile language to the one currently active
        _table_user.language.default = T.accepted_language
        form = auth()
        register_form = form
        # Add client-side validation
        s3_register_validation()
    else:
        form = auth()

    if request.args and request.args(0) == "profile" and \
       deployment_settings.get_auth_openid():
        form = DIV(form, openid_login_form.list_user_openids())

    self_registration = deployment_settings.get_security_self_registration()

    # Use Custom Ext views
    # Best to not use an Ext form for login: can't save username/password in browser & can't hit 'Enter' to submit!
    #if request.args(0) == "login":
    #    response.title = T("Login")
    #    response.view = "auth/login.html"

    return dict(form=form,
                login_form=login_form,
                register_form=register_form,
                self_registration=self_registration)

# -----------------------------------------------------------------------------
def source():
    """ RESTful CRUD controller """
    return s3_rest_controller("s3", resourcename)

# -----------------------------------------------------------------------------
# About Sahana
def apath(path=""):
    """ Application path """
    import os
    from gluon.fileutils import up
    opath = up(request.folder)
    #TODO: This path manipulation is very OS specific.
    while path[:3] == "../": opath, path=up(opath), path[3:]
    return os.path.join(opath,path).replace("\\", "/")

def about():
    """
        The About page provides details on the software dependencies and
        versions available to this instance of Sahana Eden.

        @ToDo: Avoid relying on Command Line tools which may not be in path
               - pull back info from Python modules instead?
    """
    import sys
    import subprocess
    import string
    python_version = sys.version
    web2py_version = open(apath("../VERSION"), "r").read()[8:]
    sahana_version = open(os.path.join(request.folder, "VERSION"), "r").read()
    # Database
    sqlite_version = None
    mysql_version = None
    mysqldb_version = None
    pgsql_version = None
    psycopg_version = None
    if db_string[0].find("sqlite") != -1:
        try:
            import sqlite3
            #sqlite_version = (subprocess.Popen(["sqlite3", "-version"], stdout=subprocess.PIPE).communicate()[0]).rstrip()
            sqlite_version = sqlite3.version
        except:
            sqlite_version = T("Unknown")
    elif db_string[0].find("mysql") != -1:
        try:
            mysql_version = (subprocess.Popen(["mysql", "--version"], stdout=subprocess.PIPE).communicate()[0]).rstrip()[10:]
        except:
            mysql_version = T("Unknown")
        try:
            import MySQLdb
            mysqldb_version = MySQLdb.__revision__
        except:
            mysqldb_version = T("Not installed or incorrectly configured.")
    else:
        # Postgres
        try:
            pgsql_reply = (subprocess.Popen(["psql", "--version"], stdout=subprocess.PIPE).communicate()[0])
            pgsql_version = string.split(pgsql_reply)[2]
        except:
            pgsql_version = T("Unknown")
        try:
            import psycopg2
            psycopg_version = psycopg2.__version__
        except:
            psycopg_version = T("Not installed or incorrectly configured.")
    # Libraries
    try:
        import reportlab
        reportlab_version = reportlab.Version
    except:
        reportlab_version = T("Not installed or incorrectly configured.")
    try:
        import xlwt
        xlwt_version = xlwt.__VERSION__
    except:
        xlwt_version = T("Not installed or incorrectly configured.")
    return dict(
                python_version=python_version,
                sahana_version=sahana_version,
                web2py_version=web2py_version,
                sqlite_version=sqlite_version,
                mysql_version=mysql_version,
                mysqldb_version=mysqldb_version,
                pgsql_version=pgsql_version,
                psycopg_version=psycopg_version,
                reportlab_version=reportlab_version,
                xlwt_version=xlwt_version
                )

# -----------------------------------------------------------------------------
def help():
    """ Custom View """
    response.title = T("Help")
    return dict()

# -----------------------------------------------------------------------------
def contact():
    """
        Give the user options to contact the site admins.
        Either:
            An internal Support Requests database
        or:
            Custom View
    """
    if auth.is_logged_in() and deployment_settings.get_options_support_requests():
        # Provide an internal Support Requests ticketing system.
        prefix = "support"
        resourcename = "req"
        tablename = "%s_%s" % (prefix, resourcename)
        table = db[tablename]

        # Pre-processor
        def prep(r):
            if r.interactive:
                # Only Admins should be able to update ticket status
                status = table.status
                actions = table.actions
                if not auth.s3_has_role(ADMIN):
                    status.writable = False
                    actions.writable = False
                if r.method != "update":
                    status.readable = False
                    status.writable = False
                    actions.readable = False
                    actions.writable = False
            return True
        response.s3.prep = prep

        output = s3_rest_controller(prefix, resourcename)
        return output
    else:
        # Default: Simple Custom View
        response.title = T("Contact us")
        return dict()

# =============================================================================
# HELIOS-specific
# =============================================================================
def office_onvalidation(form):
    """
        Populate the name & location fields
    """

    # Name
    table = db.org_organisation
    query = (table.id == form.vars.organisation_id)
    org = db(query).select(table.name,
                           limitby=(0, 1)).first()

    ltable = db.gis_location
    query = (ltable.id == form.vars.location_id)
    loc = db(query).select(ltable.name,
                           limitby=(0, 1)).first()

    try:
        form.vars.name = "%s %s" % (org.name,
                                    loc.name)
    except:
        # Bad Data
        if org:
            form.vars.name = "%s (%s)" % (org.name,
                                          T("Unknown Location"))
        elif loc:
            form.vars.name = "%s (%s)" % (T("Unknown Organisation"),
                                          loc.name)
        else:
            form.vars.name = "%s (%s)" % (T("Unknown Organisation"),
                                          T("Unknown Location"))

    # L0
    form.vars.L0 = loc.name

    # location_id
    table = db.org_office
    query = (table.id == form.vars.id)
    current_loc = db(query).select(table.location_id,
                                   limitby=(0, 1)).first()
    if current_loc:
        query = (ltable.id == current_loc.location_id)
        db(query).update(parent = form.vars.location_id)
        form.vars.location_id = current_loc.location_id
    else:
        loc_id = ltable.insert(name = form.vars.name,
                               parent = form.vars.location_id)
        form.vars.location_id = loc_id

    return

# -----------------------------------------------------------------------------
def office():
    """ RESTful CRUD controller """

    table = db.org_office
    table.name.readable = False
    table.name.writable = False
    s3mgr.configure(table,
                    create_next = URL(args=["[id]", "inv_item"]),
                    onvalidation = office_onvalidation)

    # Defined in the Model for use from Multiple Controllers for unified menus
    #return response.s3.office_controller()
    return office_controller()

# -----------------------------------------------------------------------------
def organisation():
    """ RESTful CRUD controller """

    s3mgr.configure("org_organisation",
                    create_next = URL(args=["[id]", "office"]))

    table = db.org_office
    table.name.readable = False
    table.name.writable = False
    s3mgr.configure(table,
                    create_next = URL(f="office", args=["[id]", "inv_item"]),
                    onvalidation = office_onvalidation)

    # Defined in the Model for use from Multiple Controllers for unified menus
    #return response.s3.organisation_controller()
    return organisation_controller()

# -----------------------------------------------------------------------------
def item():
    """ REST Controller """

    # Load Models
    s3mgr.load("supply_item")

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.supply_item_controller()

# -----------------------------------------------------------------------------
def inv_item():
    """ REST Controller """

    # Load Models
    s3mgr.load("inv_inv_item")

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.inv_item_controller()

# -----------------------------------------------------------------------------
def recv():
    """ REST Controller """

    # Load Models
    s3mgr.load("inv_recv")

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.inv_recv_controller()

# -----------------------------------------------------------------------------
def recv_item():
    """
        REST Controller
        - exposed just for Imports
    """

    # Load Models
    s3mgr.load("inv_recv_item")

    output = s3_rest_controller("inv", resourcename)
    return output

# -----------------------------------------------------------------------------
def supplier():
    """ RESTful CRUD controller """

    # Load Models
    s3mgr.load("proc_supplier")

    return s3_rest_controller("proc", resourcename)

# -----------------------------------------------------------------------------
def plan():
    """ RESTful CRUD controller """

    # Load Models
    s3mgr.load("proc_plan")

    rheader = response.s3.plan_rheader
    return s3_rest_controller("proc", resourcename,
                              rheader=rheader)

# -----------------------------------------------------------------------------
def item_entity():
    """
        REST Controller
        - consolidated report of inv_item & recv_item
    """

    # Load Models
    s3mgr.load("supply_item")

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.item_entity_controller()

# =============================================================================
def import_file():
    """
        Simple Import Tool
        - interim functionality until the proper interactive import tool is built.

        @ToDo: Instructions on how to fill-out CSV file
    """

    tablename = "admin_import_file"
    table = db[tablename]

    table.type.default = "helios"
    table.type.readable = False
    table.type.writable = False
    table.file.comment = A(T("Download Template"),
                           _href=URL(c="static", f="formats",
                                     args=["s3csv", "helios.csv"]),
                           _id="dl_template"),

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
        title_create = T("Import New File"),
        title_display = T("Import File Details"),
        #title_list = T("List Import Files"),
        title_list = T("Upload Spreadsheet"),
        title_update = T("Edit Import File"),
        title_search = T("Search Import Files"),
        subtitle_create = T("Import New File"),
        subtitle_list = T("Import Files"),
        label_list_button = T("List Import Files"),
        label_create_button = T("Import New File"),
        msg_record_created = T("File Imported"),
        msg_record_modified = T("File Imported"),
        msg_record_deleted = T("Import File deleted"),
        msg_list_empty = T("No Import Files currently uploaded"))

    s3.crud.submit_button = T("Import")
    
    s3mgr.configure(tablename,
                    onvalidation=import_file_onvalidation,
                    onaccept=import_file_onaccept,
                    create_next = URL(f="item_entity"),
                    list_fields = ["id",
                                   #"type",
                                   "filename",
                                   "modified_on",
                                   "comments"
                                ])

    response.s3.jquery_ready.append( """
$('#dl_template').click(function(evt) {
    S3ClearNavigateAwayConfirm();
    return true;
})
""" )

    
    def postp(r, output):
        if r.interactive:
            if isinstance(output, dict):
                # Hide the list of previously-uploaded files
                try:
                    output.pop("items")
                    output.pop("subtitle")
                except:
                    # Create form
                    pass
        return output
    response.s3.postp = postp
    
    return s3_rest_controller("admin", resourcename)

# -----------------------------------------------------------------------------
def import_file_onvalidation(form):
    """
        Populate the filename field
    """

    form.vars.filename = form.vars.file.filename
    return

# -----------------------------------------------------------------------------
def inv_item_import_prep(import_data):
    """
        Delete all:
        - inv_inv_item
        - inv_recv_item
        - inv_recv
        - proc_plan_item
        - proc_plan
        - org_office
        - org_organisation (unless still present due to another office)

        Match the offices by organisation+country (or office name?)
    """

    resource, tree = import_data

    root = tree.getroot()
    offices = root.findall(".//resource[@name='org_office']")
    for office in offices:
        name = office.findall("./data[@field='name']")[0]

        # Get the office record matching the name
        # (maybe should get the office record matching organisation+country here?)
        otable = db.org_office
        query = (otable.name == name.text) & (otable.deleted != True)
        rows = db(query).select()
        for row in rows:

            # Remove all inv_inv_item with that site_id
            itable = db.inv_inv_item
            ondelete = s3mgr.model.get_config("inv_inv_item", "ondelete")
            resource = s3mgr.define_resource("inv", "inv_item",
                                             filter=itable.site_id == row.site_id)
            resource.delete(ondelete=ondelete, cascade=True)

            # Remove all inv_inv_recv with that site_id
            # This will cascade to inv_recv_item
            itable = db.inv_recv
            ondelete = s3mgr.model.get_config("inv_recv", "ondelete")
            resource = s3mgr.define_resource("inv", "recv",
                                             filter=itable.site_id == row.site_id)
            resource.delete(ondelete=ondelete, cascade=True)

            if deployment_settings.has_module("proc"):
                # Remove all proc_plan with that site_id
                # This will cascade to proc_plan_item
                s3mgr.load("proc_plan")
                ptable = db.proc_plan
                ondelete = s3mgr.model.get_config("proc_plan", "ondelete")
                resource = s3mgr.define_resource("proc", "plan",
                                                 filter=ptable.site_id == row.site_id)
                resource.delete(ondelete=ondelete, cascade=True)

            # Remove this office
            #ondelete = s3mgr.model.get_config("org_office", "ondelete")
            #resource = s3mgr.define_resource("org", "office", id=row.id)
            #resource.delete(ondelete=ondelete)

            # Remove the org
            # This may be impossible if there are other records referencing
            # the organisation record, because organisation_id has ondelete=RESTRICT
            # However, this method will not throw any error in this case, but
            # just not delete (return value of resource.delete would be 0, though)
            #ondelete = s3mgr.model.get_config("org_organisation", "ondelete")
            #resource = s3mgr.define_resource("org", "organisation", id=row.organisation_id)
            #resource.delete(ondelete=ondelete)

    return

# -----------------------------------------------------------------------------
def helios():
    """
        Custom controller to process an upload file of stock and order items
        REST clients can come direct here
    """

    content_type = request.env.get("content_type", None)
    if content_type and content_type.startswith("multipart/"):
        p = request.vars.file
        import cgi
        if isinstance(p, cgi.FieldStorage) and p.filename:
            openfile = p.file
            openfile.seek(0)
        else:
            session.error = T("No file to import")
            redirect(URL(c="default", f="import_file"))
    elif "filename" in request.get_vars:
        filename = request.get_vars["filename"]
        openfile = open(filename, "r")
    else:
        openfile = request.body
        openfile.seek(0)

    # Convert the CSV into a tree
    xml = s3mgr.xml
    tree = xml.csv2tree(openfile)
    if not tree:
        db.rollback()
        session.error = xml.error
        redirect(URL(c="default", f="import_file"))

    # Stylesheet in the formats/s3csv folder
    stylesheet = os.path.join(request.folder,
                              "static",
                              "formats",
                              "s3csv",
                              "helios.xsl")

    # Process Stock Items
    s3mgr.import_prep = inv_item_import_prep
    resource = s3mgr.define_resource("inv", "inv_item")
    result = resource.import_xml(tree,
                                 stylesheet=stylesheet)
    if resource.error:
        db.rollback()
        session.error = "%s: %s" % (resource.error,
                                    result)
        redirect(URL(c="default", f="import_file"))

    # Process Order Items
    s3mgr.import_prep = None
    resource = s3mgr.define_resource("inv", "recv_item")
    result = resource.import_xml(tree,
                                 stylesheet=stylesheet)
    if resource.error:
        db.rollback()
        session.error = "%s: %s"  % (resource.error,
                                     result)
        redirect(URL(c="default", f="import_file"))

    if deployment_settings.has_module("proc"):
        # Process Planned Procurements
        s3mgr.import_prep = None
        resource = s3mgr.define_resource("proc", "plan_item")
        result = resource.import_xml(tree,
                                     stylesheet=stylesheet)
        if resource.error:
            db.rollback()
            session.error = "%s: %s"  % (resource.error,
                                         result)
            redirect(URL(c="default", f="import_file"))

    return xml.json_message(True, 200, "File imported successfully.")

# -----------------------------------------------------------------------------
def import_file_onaccept(form):
    """
        When the import file is uploaded, do the import into the database
    """

    table = db.admin_import_file

    uploadfolder = table.file.uploadfolder
    filename = form.vars.file

    filepath = os.path.join(uploadfolder, filename)
    response.s3.filepath = filepath
    helios()

# END =========================================================================
