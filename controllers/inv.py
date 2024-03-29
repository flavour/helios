# -*- coding: utf-8 -*-

"""
    Inventory Management

    @author: Michael Howden (michael@sahanafoundation.org)
    @date-created: 2010-08-16

    A module to record inventories of items at a locations (sites),
    including Warehouses, Offices, Shelters & Hospitals
"""

module = request.controller
resourcename = request.function

if not deployment_settings.has_module(module):
    raise HTTP(404, body="Module disabled: %s" % module)

s3_menu(module)

# Load Models
# @ToDo: Make this only happen for the relevant Tabs
s3mgr.load("inv_inv_item") # Also loads Supply & Requests
req_item_onaccept = response.s3.req_item_onaccept

# -----------------------------------------------------------------------------
def index():
    """
        Application Home page
        - custom View
    """

    # Load models
    s3mgr.load("cr_shelter") # Need CRUD String

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name
    return dict(module_name=module_name)

# =============================================================================
def office():
    """
        Required to ensure the tabs work from req_match
    """
    return warehouse()

def warehouse():
    """
        RESTful CRUD controller
        Filtered version of the org_office resource
    """

    module = "org"
    resourcename = "office"
    tablename = "org_office"
    table = db[tablename]

    if "viewing" in request.get_vars:
        viewing = request.get_vars.viewing
        tn, record = viewing.split(".", 1)
        if tn == "org_office":
            request.args.insert(0, record)

    s3.crud_strings[tablename] = s3_warehouse_crud_strings

    # Type is Warehouse
    table.type.default = 5 # Warehouse
    table.type.writable = False

    # Only show warehouses
    response.s3.filter = (db.org_office.type == 5)

    # Remove type from list_fields
    list_fields = s3mgr.model.get_config("org_office", "list_fields")
    try:
        list_fields.remove("type")
    except:
        # Already removed
        pass
    s3mgr.configure(tablename, list_fields=list_fields)

    warehouse_search = s3base.S3Search(
        advanced=(s3base.S3SearchSimpleWidget(
                    name="warehouse_search_text",
                    label=T("Search"),
                    comment=T("Search for warehouse by text."),
                    field=["name","comments", "email"]
                  ),
                  s3base.S3SearchOptionsWidget(
                    name="warehouse_search_org",
                    label=T("Organization"),
                    comment=T("Search for warehouse by organization."),
                    field=["organisation_id"],
                    represent ="%(name)s",
                    cols = 3
                  ),
                  s3base.S3SearchLocationHierarchyWidget(
                    gis,
                    name="warehouse_search_location",
                    comment=T("Search for warehouse by location."),
                    represent ="%(name)s",
                    cols = 3
                  ),
                  s3base.S3SearchLocationWidget(
                    name="warehouse_search_map",
                    label=T("Map"),
                  ),
        ))
    s3mgr.configure(tablename,
                    search_method = warehouse_search)
    def prep(r):
        if r.interactive:

            if r.method != "read":
                # Don't want to see in Create forms
                # inc list_create (list_fields over-rides)
                r.table.obsolete.writable = False
                r.table.obsolete.readable = False
                address_hide(table)
                # Process Base Location
                #s3mgr.configure(table._tablename,
                #                onaccept=address_onaccept)

            if r.component:
                if r.component.name == "inv_item" or \
                   r.component.name == "recv" or \
                   r.component.name == "send":
                    # Filter out items which are already in this inventory
                    response.s3.inv_prep(r)

                elif r.component.name == "human_resource":
                    # Filter out people which are already staff for this warehouse
                    s3_filter_staff(r)
                    # Cascade the organisation_id from the hospital to the staff
                    db.hrm_human_resource.organisation_id.default = r.record.organisation_id
                    db.hrm_human_resource.organisation_id.writable = False

                elif r.component.name == "req":
                    if r.method != "update" and r.method != "read":
                        # Hide fields which don't make sense in a Create form
                        # inc list_create (list_fields over-rides)
                        response.s3.req_create_form_mods()

        # "show_obsolete" var option can be added (btn?) later to
        # disable this filter
        if r.method in [None, "list"] and \
            not r.vars.get("show_obsolete", False):
            r.resource.add_filter((db.org_office.obsolete != True))
        return True
    response.s3.prep = prep

    rheader = office_rheader

    if "extra_data" in request.get_vars:
        csv_template = "inv_item"
    else:
        csv_template = "warehouse"
    csv_stylesheet = "%s.xsl" % csv_template

    output = s3_rest_controller(module, resourcename, rheader=rheader,
                                csv_template = csv_template,
                                csv_stylesheet = csv_stylesheet,
                                # Extra fields for CSV uploads:
                                csv_extra_fields = [
                                    dict(label="Organisation",
                                         field=organisation_id(comment=None)),
                                    dict(label="Test",
                                         value="MyTest")
                                ])

    return output

# =============================================================================
def incoming():
    """ Incoming Shipments """

    return response.s3.inv_incoming()

# -----------------------------------------------------------------------------
def req_match():
    """ Match Requests """

    s3.crud_strings.org_office.title_display = T("Warehouse Details")
    return response.s3.req_match()

# =============================================================================
def inv_item():
    """ REST Controller """

    # Upload for configuration (add replace option)
    response.s3.importerPrep = lambda: dict(ReplaceOption=T("Remove existing data before import"))

    # Import pre-process
    def import_prep(data):
        """
            Deletes all Stock records of the organisation
            before processing a new data import, used for the import_prep
            hook in s3mgr
        """
        request = current.request
        resource, tree = data
        xml = s3mgr.xml
        tag = xml.TAG
        att = xml.ATTRIBUTE
        if response.s3.importerReplace:
            if tree is not None:
                root = tree.getroot()
                expr = "/%s/%s[@%s='org_organisation']/%s[@%s='name']" % \
                       (tag.root, tag.resource, att.name, tag.data, att.field)
                orgs = root.xpath(expr)
                for org in orgs:
                    org_name = org.get("value", None) or org.text
                    if org_name:
                        try:
                            org_name = json.loads(s3mgr.xml.xml_decode(org_name))
                        except:
                            pass
                    if org_name:
                        query = (db.org_organisation.name == org_name) & \
                                (db.org_site.organisation_id == db.org_organisation.id) & \
                                (db.inv_inv_item.site_id == db.org_site.id)
                        resource = s3mgr.define_resource("inv", "inv_item", filter=query)
                        ondelete = s3mgr.model.get_config("inv_inv_item", "ondelete")
                        resource.delete(ondelete=ondelete, format="xml")
            resource.skip_import = True
    s3mgr.import_prep = import_prep

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.inv_item_controller()

# -----------------------------------------------------------------------------
def inv_item_quantity():
    table = db.inv_inv_item
    query = (table.id == request.args[0]) & \
            (table.item_pack_id == db.supply_item_pack.id)
    record = db(query).select(table.quantity,
                              db.supply_item_pack.quantity,
                              limitby=(0, 1)).first()

    response.headers["Content-Type"] = "application/json"
    return json.dumps(record)

# -----------------------------------------------------------------------------
def inv_item_packs():
    """
        Called by S3FilterFieldChange to provide the pack options for a
            particular Item
    """
    table = db.inv_inv_item
    ptable = db.supply_item_pack
    query = (table.id == request.args[0]) & \
            (table.item_id == ptable.item_id)
    records = db(query).select(ptable.id,
                               ptable.name,
                               ptable.quantity)

    response.headers["Content-Type"] = "application/json"
    return records.json()

# =============================================================================
def recv():
    """ RESTful CRUD controller """

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.inv_recv_controller()

# -----------------------------------------------------------------------------
def recv_item():
    """ RESTful CRUD controller """

    output = s3_rest_controller(module, resourcename)
    return output

# =============================================================================
def send():
    """ RESTful CRUD controller """

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.inv_send_controller()

# -----------------------------------------------------------------------------
def req_items_for_inv(site_id, quantity_type):
    """
        used by recv_process & send_process
        returns a dict of unique req items (with min  db.req_req.date_required | db.req_req.date)
        key = item_id
        @param site_id: The inventory to find the req_items from
        @param quantity_type: str ("commit", "transit" or "fulfil) The
                              quantity type which will be used to determine if this item is still outstanding
    """
    if not deployment_settings.has_module("req"):
        return Storage()

    s3mgr.load("req_req")
    table = db.req_req
    itable = db.req_req_item
    query = ( table.site_id == site_id ) & \
            ( table.id == itable.req_id) & \
            ( itable.item_pack_id == itable.item_pack_id) & \
            ( itable["quantity_%s" % quantity_type] < itable.quantity) & \
            ( table.cancel == False ) & \
            ( table.deleted == False ) & \
            ( itable.deleted == False )
    req_items = db(query).select(itable.id,
                                 itable.req_id,
                                 itable.item_id,
                                 itable.quantity,
                                 itable["quantity_%s" % quantity_type],
                                 itable.item_pack_id,
                                 orderby = table.date_required | table.date,
                                 #groupby = itable.item_id
                                )

    # Because groupby doesn't follow the orderby, this will remove any
    # duplicate req_item, using the first record according to the orderby
    # req_items = req_items.as_dict( key = "req_req_item.item_id") <- doensn't work
    # @todo: web2py Rows.as_dict function could be extended to enable this functionality instead
    req_item_ids = []
    unique_req_items = Storage()
    for req_item in req_items:
        if req_item.item_id not in req_item_ids:
            # This item is not already in the dict
            unique_req_items[req_item.item_id] = Storage( req_item.as_dict() )
            req_item_ids.append(req_item.item_id)

    return unique_req_items

# -----------------------------------------------------------------------------
def req_item_in_shipment( shipment_item,
                          shipment_type,
                          req_items,
                         ):
    """
        Checks if a shipment item is in a request and updates req_item
        and the shipment.
    """

    shipment_item_table = "inv_%s_item" % shipment_type
    try:
        item_id = shipment_item[shipment_item_table].item_id
    except:
        item_id = shipment_item.inv_inv_item.item_id

    # Check for req_items
    if item_id in req_items:
        shipment_to_req_type = dict(recv = "fulfil",
                                    send = "transit")
        quantity_req_type = "quantity_%s" % shipment_to_req_type[shipment_type]

        # This item has been requested from this inv
        req_item = req_items[item_id]
        req_item_id = req_item.id

        # Update the req quantity
        # convert the shipment items quantity into the req_tem.quantity_fulfil (according to pack)
        quantity = req_item[quantity_req_type] + \
                   (shipment_item[shipment_item_table].pack_quantity / \
                    req_item.pack_quantity) * \
                    shipment_item[shipment_item_table].quantity
        quantity = min(quantity, req_item.quantity)  #Cap at req. quantity
        db.req_req_item[req_item_id] = {quantity_req_type: quantity}

        # Link the shipment_item to the req_item
        db[shipment_item_table][shipment_item[shipment_item_table].id] = \
            dict(req_item_id = req_item_id)

        # Flag req record to update status_fulfil
        return req_item.req_id, req_item.id
    else:
        return None, None


# -----------------------------------------------------------------------------
def recv_process():
    """ Receive a Shipment """

    recv_id = request.args[0]
    if not auth.s3_has_permission("update",
                                  db.inv_recv,
                                  record_id=recv_id):
        session.error = T("You do not have permission to receive this shipment.")


    recv_record = db.inv_recv[recv_id]

    if recv_record.status != SHIP_STATUS_IN_PROCESS:
        session.error = T("This shipment has already been received.")

    if session.error:
        redirect(URL(c = "default",
                     f = "recv",
                     args = [recv_id]))

    site_id = recv_record.site_id

    # Get Recv & Inv Items
    table = db.inv_recv_item
    query = ( table.recv_id == recv_id ) & \
            ( table.deleted == False )
    recv_items = db(query).select(table.id,
                                  table.item_id,
                                  table.quantity,
                                  table.item_pack_id, # required by pack_quantity virtualfield
                                  )

    table = db.inv_inv_item
    query = ( table.site_id == site_id ) & \
            ( table.deleted == False )
    inv_items = db(query).select(table.id,
                                 table.item_id,
                                 table.quantity,
                                 table.item_pack_id) # required by pack_quantity virtualfield

    inv_items_dict = inv_items.as_dict(key = "item_id")

    req_items = req_items_for_inv(site_id, "fulfil")

    update_req_id = []

    for recv_item in recv_items:
        item_id = recv_item.item_id
        if item_id in inv_items_dict:
            # This item already exists in the inv, and the quantity must be incremented
            inv_item = Storage(inv_items_dict[item_id])

            inv_item_id = inv_item.id

            quantity = response.s3.supply_item_add(inv_item.quantity,
                                           inv_item.pack_quantity,
                                           recv_item.quantity,
                                           recv_item.pack_quantity)
            item = dict(quantity = quantity)
        else:
            # This item must be added to the inv
            inv_item_id = 0
            item = dict( site_id = site_id,
                         item_id = item_id,
                         quantity = recv_item.quantity,
                         item_pack_id = recv_item.item_pack_id)

        # Update Inv Item
        db.inv_inv_item[inv_item_id] = item

        # Check for req_items (-> fulfil)
        update_req_id.append( req_item_in_shipment(shipment_item = Storage(inv_recv_item = recv_item),
                                                   shipment_type = "recv",
                                                   req_items = req_items))

    # Update recv record & lock for editing
    db.inv_recv[recv_id] = dict(date = request.utcnow,
                                 status = SHIP_STATUS_RECEIVED,
                                 owned_by_user = None,
                                 owned_by_role = ADMIN )

    # Update status_fulfil of the req record(s)
    for req_id, req_item_id in update_req_id:
        if req_id:
            s3mgr.store_session("req", "req", req_id)
            s3mgr.store_session("req", "req_item", req_item_id)
            req_item_onaccept(None)

    session.confirmation = T("Shipment Items received by Inventory")

    # Go to the Inventory of the Site which has received these items
    (prefix, resourcename, id) = s3mgr.model.get_instance(db.org_site,
                                                          site_id)

    redirect(URL(c = "default",
                 f = resourcename,
                 args = [id, "inv_item"],
                 vars = dict(show_inv="True")))

# -----------------------------------------------------------------------------
def recv_cancel():
    """ Cancel a Received Shipment """

    recv_id = request.args[0]
    if not auth.s3_has_permission("delete",
                                  db.inv_recv,
                                  record_id=recv_id):
        session.error = T("You do not have permission to cancel this received shipment.")


    recv_record = db.inv_recv[recv_id]

    if recv_record.status != SHIP_STATUS_RECEIVED:
        session.error = T("This shipment has not been received - it has NOT been canceled because can still be edited.")

    if session.error:
        redirect(URL(c = "default",
                     f = "recv",
                     args = [recv_id]))

    site_id = recv_record.site_id

    # Get Recv & Inv Items
    table = db.inv_recv_item
    query = ( table.recv_id == recv_id ) & \
            ( table.deleted == False )
    recv_items = db(query).select(table.id,
                                  table.item_id,
                                  table.quantity,
                                  table.item_pack_id, # required by pack_quantity virtualfield
                                  table.req_item_id)

    table = db.inv_inv_item
    query = ( table.site_id == site_id ) & \
            ( table.deleted == False )
    inv_items = db(query).select(table.id,
                                 table.item_id,
                                 table.quantity,
                                 table.item_pack_id) # required by pack_quantity virtualfield

    inv_items_dict = inv_items.as_dict(key = "item_id")

    req_items = req_items_for_inv(site_id, "fulfil")

    update_req_id = []

    for recv_item in recv_items:
        item_id = recv_item.item_id
        # All Items received *should* exist in the inv.
        if item_id in inv_items_dict:
            # Decrease the inv_item.quantity
            inv_item = Storage(inv_items_dict[item_id])

            inv_item_id = inv_item.id

            quantity = response.s3.supply_item_add(inv_item.quantity,
                                           inv_item.pack_quantity,
                                           -recv_item.quantity,
                                           recv_item.pack_quantity)

            item = dict(quantity = quantity)
        else:
            # This Value should be added with a negative value
            inv_item_id = 0
            item = dict( site_id = site_id,
                         item_id = item_id,
                         quantity = -recv_item.quantity,
                         item_pack_id = recv_item.item_pack_id )

        # Update Inv Item
        db.inv_inv_item[inv_item_id] = item

        # Remove the link from the recv_item to the req_item
        db.inv_recv_item[recv_item.id] = dict(req_item_id = None)

        if deployment_settings.has_module("req"):
            # Reduce any req_item
            req_item_id = recv_item.req_item_id
            table = db.req_req_item
            query = (table.id == recv_item.req_item_id) & \
                    (table.deleted == False)
            r_req_item = db(query).select(table.quantity_fulfil,
                                          table.item_pack_id, # required by pack_quantity virtualfield
                                          limitby = (0, 1)).first()
            if r_req_item:
                quantity_fulfil = response.s3.supply_item_add(r_req_item.quantity_fulfil,
                                                      r_req_item.pack_quantity,
                                                      -recv_item.quantity,
                                                      recv_item.pack_quantity)
                db.req_req_item[req_item_id] = dict(quantity_fulfil=quantity_fulfil)

                # Check for req_items (-> fulfil)
                update_req_id.append( [r_req_item.req_id, req_item_id] )

    # Update recv record & lock for editing
    db.inv_recv[recv_id] = dict(date = request.utcnow,
                                status = SHIP_STATUS_CANCEL,
                                owned_by_user = None,
                                owned_by_role = ADMIN)

    # Update status_fulfil of the req record(s)
    for req_id, req_item_id in update_req_id:
        if req_id:
            s3mgr.store_session("req", "req", req_id)
            s3mgr.store_session("req", "req_item", req_item_id)
            req_item_onaccept(None)

    session.confirmation = T("Received Shipment canceled and items removed from Inventory")

    redirect(URL(c = "default",
                 f = "recv",
                 args = [recv_id]))

# -----------------------------------------------------------------------------
def send_process():
    """ Send a Shipment """

    send_id = request.args[0]
    if not auth.s3_has_permission("update",
                                  db.inv_send,
                                  record_id=send_id):
        session.error = T("You do not have permission to send this shipment.")

    send_record = db.inv_send[send_id]

    if send_record.status != SHIP_STATUS_IN_PROCESS:
        session.error = T("This shipment has already been sent.")

    if session.error:
        redirect(URL(c = "inv",
                     f = "send",
                     args = [send_id]))

    site_id = send_record.site_id

    cancel_send = False
    invalid_send_item_ids = []

    # Get Send & Inv Items
    stable = db.inv_send_item
    itable = db.inv_inv_item
    query = ( stable.send_id == send_id ) & \
            ( stable.deleted == False )
    send_items = db(query).select(stable.id,
                                  stable.quantity,
                                  stable.item_pack_id,
                                  itable.id,
                                  itable.item_id,
                                  itable.quantity,
                                  itable.item_pack_id, # required by pack_quantity virtualfield
                                  itable.deleted,
                                  left=itable.on(stable.inv_item_id == itable.id),
                                  # To ensure that all send items are selected, even if the inv item has been deleted.
                                )

    # Filter for inv site records (separate due to left-join)
    send_items.exclude(lambda row: row.inv_inv_item.id and \
                                   row.inv_inv_item.deleted == True)

    to_site_id = send_record.to_site_id

    req_items = req_items_for_inv(to_site_id, "transit")

    update_req_id = []

    for send_item in send_items:
        item_id = send_item.inv_inv_item.item_id
        send_item_id = send_item.inv_send_item.id
        inv_item_id = send_item.inv_inv_item.id

        new_inv_quantity = response.s3.supply_item_add(send_item.inv_inv_item.quantity,
                                               send_item.inv_inv_item.pack_quantity,
                                               -send_item.inv_send_item.quantity,
                                               send_item.inv_send_item.pack_quantity)

        if new_inv_quantity < 0:
            # This shipment is invalid
            # flag this item
            invalid_send_item_ids.append(send_item_id)

            # Cancel this processing
            cancel_send = True
        else:
            # Update the Inv Item Quantity
            db.inv_inv_item[inv_item_id] = dict(quantity = new_inv_quantity)

        # Check for req_items (-> transit)
        update_req_id.append(req_item_in_shipment(shipment_item = send_item,
                                                  shipment_type = "send",
                                                  req_items = req_items))

    if cancel_send:
        db.rollback()
        for invalid_send_item_id in invalid_send_item_ids:
            db.inv_send_item[invalid_send_item_id] = dict(status = 1)

        session.error = T("There are insufficient items in the Inventory to send this shipment") #@todo: list the items and the quantities in the error message
        redirect(URL(c = "inv",
                     f = "send",
                     args = [send_id, "send_item"]))
    else:
        # Update Send record & lock for editing
        db.inv_send[send_id] = dict(date = request.utcnow,
                                     status = SHIP_STATUS_SENT,
                                     owned_by_user = None,
                                     owned_by_role = ADMIN
                                     )
        session.confirmation = T("Shipment Items sent from Inventory")

        # Update status_fulfil of the req record(s)
        for req_id, req_item_id in update_req_id:
            if req_id:
                s3mgr.store_session("req", "req", req_id)
                s3mgr.store_session("req", "req_item", req_item_id)
                req_item_onaccept(None)

        # Go to the Site which has sent these items
        (prefix, resourcename, id) = s3mgr.model.get_instance(db.org_site,
                                                              site_id)

        redirect(URL(c = prefix,
                     f = resourcename,
                     args = [id, "inv_item"]))

# -----------------------------------------------------------------------------
def send_cancel():
    """
        Could we reuse recv_cancel? Challenges:
         * errors
         * sent_items query
          * Different query
          * two tables in rows result
    """
    send_id = request.args[0]
    if not auth.s3_has_permission("delete",
                                  db.inv_send,
                                  record_id=send_id):
        session.error = T("You do not have permission to cancel this sent shipment.")


    send_record = db.inv_send[send_id]

    if send_record.status != SHIP_STATUS_SENT:
        session.error = T("This shipment has not been sent - it has NOT been canceled because can still be edited.")

    if session.error:
        redirect(URL(c = "inv",
                     f = "send",
                     args = [send_id],
                     )
                 )

    site_id = send_record.site_id

    # Get Send & Inv Items
    stable = db.inv_send_item
    itable = db.inv_inv_item
    query = ( stable.send_id == send_id ) & \
            ( stable.inv_item_id == itable.id ) & \
            ( stable.deleted == False ) & \
            ( itable.deleted == False )
    send_items = db(query).select(stable.id,
                                  itable.item_id,
                                  stable.quantity,
                                  stable.item_pack_id, # required by pack_quantity virtualfield
                                  stable.req_item_id)

    query = ( itable.site_id == site_id ) & \
            ( itable.deleted == False )
    inv_items = db(query).select(itable.id,
                                 itable.item_id,
                                 itable.quantity,
                                 itable.item_pack_id, # required by pack_quantity virtualfield
                                )

    inv_items_dict = inv_items.as_dict(key = "item_id")

    req_items = req_items_for_inv(site_id, "transit")

    update_req_id = []

    for send_item in send_items:
        item_id = send_item.inv_inv_item.item_id
        # All Items received *should* exist in the inv.
        if item_id in inv_items_dict:
            # Decrease the inv_item.quantity
            inv_item = Storage(inv_items_dict[item_id])

            inv_item_id = inv_item.id

            quantity = response.s3.supply_item_add(inv_item.quantity,
                                           inv_item.pack_quantity,
                                           send_item.inv_send_item.quantity,
                                           send_item.inv_send_item.pack_quantity)

            item = dict(quantity = quantity)
        else:
            # This Value should be added with a negative value
            inv_item_id = 0
            item = dict( site_id = site_id,
                         item_id = item_id,
                         quantity = send_item.inv_send_item.quantity,
                         item_pack_id = send_item.inv_send_item.item_pack_id
                         )

        # Update Inv Item
        db.inv_inv_item[inv_item_id] = item

        # Remove the link from the recv_item to the req_item
        db.inv_recv_item[send_item.inv_send_item.id] = dict(req_item_id = None)

        if deployment_settings.has_module("req"):
            # Reduce any req_item
            req_item_id = send_item.inv_send_item.req_item_id
            table = db.req_req_item
            query = (table.id == req_item_id) & \
                    (table.deleted == False)
            r_req_item = db(query).select(table.quantity_fulfil,
                                          table.item_pack_id, # required by pack_quantity virtualfield
                                          limitby = (0, 1)).first()
            if r_req_item:
                quantity_fulfil = response.s3.supply_item_add(r_req_item.quantity_fulfil,
                                                      r_req_item.pack_quantity,
                                                      -send_item.inv_send_item.quantity,
                                                      send_item.inv_send_item.pack_quantity)
                db.req_req_item[req_item_id] = dict(quantity_fulfil=quantity_fulfil)

                # Check for req_items (-> fulfil)
                update_req_id.append( [r_req_item.req_id, req_item_id] )

    # Update send record & lock for editing
    db.inv_send[send_id] = dict(date = request.utcnow,
                                status = SHIP_STATUS_CANCEL,
                                owned_by_user = None,
                                owned_by_role = ADMIN
                                )

    if deployment_settings.has_module("req"):
        # Update status_fulfil of the req record(s)
        for req_id, req_item_id in update_req_id:
            if req_id:
                s3mgr.store_session("req", "req", req_id)
                s3mgr.store_session("req", "req_item", req_item_id)
                req_item_onaccept(None)

    session.confirmation = T("Sent Shipment canceled and items returned to Inventory")

    redirect(URL(c = "inv",
                 f = "send",
                 args = [send_id]))

#==============================================================================
def recv_sent():
    """ function to copy data from a shipment which was sent to the warehouse to a recv shipment """

    send_id = request.args[0]
    # This is more explicit than getting the site_id from the inv_send.to_site_id
    # As there may be multiple sites per location.
    site_id = request.vars.site_id

    r_send = db.inv_send[send_id]

    if r_send.status != SHIP_STATUS_SENT:
        session.error = T("This shipment has already been received.")

    if not auth.s3_has_permission("update",
                                  db.org_site,
                                  record_id=site_id):
        session.error = T("You do not have permission to receive this shipment.")

    if session.error:
        redirect(URL(c = "inv",
                     f = "send",
                     args = [send_id]))

    # Create a new recv record
    recv_id = db.inv_recv.insert( type = 1, # 1:"Another Inventory",
                                  site_id = site_id,
                                  recipient_id = s3_logged_in_person(),
                                  from_site_id = r_send.site_id,
#                                  organisation_id = r_send.organisation_id,
                                  sender_id = r_send.sender_id)

    stable = db.inv_send_item
    itable = db.inv_inv_item
    query = (stable.send_id == send_id) & \
            (stable.inv_item_id == itable.id) & \
            (stable.deleted == False)
    sent_items = db(query).select(itable.item_id,
                                  stable.item_pack_id,
                                  stable.quantity,
                                  stable.req_item_id)

    # Copy items from send to recv
    for sent_item in sent_items:
        db.inv_recv_item.insert(recv_id = recv_id,
                                item_id = sent_item.inv_inv_item.item_id,
                                item_pack_id = sent_item.inv_send_item.item_pack_id,
                                quantity = sent_item.inv_send_item.quantity,
                                req_item_id = sent_item.inv_send_item.req_item_id)

    # Flag shipment as received as received
    db.inv_send[send_id] = dict(status = SHIP_STATUS_RECEIVED)

    # Redirect to rec
    redirect(URL(c = "inv",
                 f = "recv",
                 args = [recv_id, "recv_item"]))

#==============================================================================
def send_commit():
    """
        function to send items according to a commit.
        copy data from a commit into a send
        arg: commit_id
        @ToDo: This function needs to be able to detect the site to send the items from,
        site_id is currently undefined and this will not work.
    """

    commit_id = request.args[0]
    r_commit = db.req_commit[commit_id]
    r_req = db.req_req[r_commit.req_id]

    # User must have permissions over site which is sending
    (prefix, resourcename, id) = s3mgr.model.get_instance(db.org_site,
                                                          r_commit.site_id)
    if not auth.s3_has_permission("update",
                                  db["%s_%s" % (prefix, resourcename)],
                                  record_id=id):
        session.error = T("You do not have permission to send a shipment from this site.")
        redirect(URL(c = "req",
                     f = "commit",
                     args = [commit_id]))

    #rtable = db.req_req
    #stable = db.org_site
    #query = (rtable.id == r_commit.req_id) & \
    #        (stable.id == rtable.site_id)
    #to_location_id = db(query).select(stable.location_id,
    #                                  limitby = (0, 1)).first().location_id

    # Create a new send record
    send_id = db.inv_send.insert( date = request.utcnow,
                                  site_id = r_commit.site_id,
                                  to_site_id = r_req.site_id )

    # Only select items which are in the warehouse
    ctable = db.req_commit_item
    rtable = db.req_req_item
    itable = db.inv_inv_item
    query = (ctable.commit_id == commit_id) & \
            (ctable.req_item_id == rtable.id) & \
            (rtable.item_id == itable.item_id) & \
            (itable.site_id == r_commit.site_id) & \
            (ctable.deleted == False) & \
            (rtable.deleted == False) & \
            (itable.deleted == False)
    commit_items = db(query).select(itable.id,
                                    ctable.quantity,
                                    ctable.item_pack_id,
                                    ctable.req_item_id)

    for commit_item in commit_items:
        send_item_id = db.inv_send_item.insert( send_id = send_id,
                                                inv_item_id = commit_item.inv_inv_item.id,
                                                quantity = commit_item.req_commit_item.quantity,
                                                item_pack_id = commit_item.req_commit_item.item_pack_id,
                                                req_item_id = commit_item.req_commit_item.req_item_id)

    # Redirect to send
    redirect(URL(c = "inv",
                 f = "send",
                 args = [send_id, "send_item"]))

# =============================================================================
def recv_item_json():
    db.inv_recv.date.represent = lambda dt: dt[:10]
    rtable = db.inv_recv
    itable = db.inv_recv_item
    query = (itable.req_item_id == request.args[0]) & \
            (rtable.id == itable.recv_id) & \
            (rtable.site_id == db.org_site.id) & \
            (rtable.status == SHIP_STATUS_RECEIVED) & \
            (itable.deleted == False )
    records = db(query).select(rtable.id,
                               rtable.date,
                               db.org_site.name,
                               itable.quantity)

    json_str = "[%s,%s" % ( json.dumps(dict(id = str(T("Received")),
                                            quantity = "#"
                                            )) ,
                            records.json()[1:])

    response.headers["Content-Type"] = "application/json"
    return json_str

# =============================================================================
def send_item_json():
    db.inv_send.date.represent = lambda dt: dt[:10]
    stable = db.inv_send
    itable = db.inv_send_item
    query = (itable.req_item_id == request.args[0]) & \
            (stable.id == itable.send_id) & \
            (stable.site_id == db.org_site.id) & \
            ((stable.status == SHIP_STATUS_SENT) | \
             (stable.status == SHIP_STATUS_RECEIVED)) & \
            (itable.deleted == False)
    records =  db(query).select(stable.id,
                                stable.date,
                                db.org_site.name,
                                itable.quantity)

    json_str = "[%s,%s" % ( json.dumps(dict(id = str(T("Sent")),
                                            quantity = "#"
                                            )) ,
                            records.json()[1:])

    response.headers["Content-Type"] = "application/json"
    return json_str

# END =========================================================================
