# -*- coding: utf-8 -*-

""" Incident Reporting System - Controllers

    @author: Sahana Taiwan Team
    @author: Fran Boon

"""

module = request.controller
resourcename = request.function

if not deployment_settings.has_module(module):
    raise HTTP(404, body="Module disabled: %s" % module)

# Load Models
s3mgr.load("irs_ireport")

# Options Menu (available in all Functions' Views)
s3_menu(module)

# -----------------------------------------------------------------------------
def index():

    """ Custom View """

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name
    return dict(module_name=module_name)


# -----------------------------------------------------------------------------
@auth.s3_requires_membership(1)
def icategory():

    """
        Incident Categories, RESTful controller
        Note: This just defines which categories are visible to end-users
        The full list of hard-coded categories are visible to admins & should remain unchanged for sync
    """

    tablename = "%s_%s" % (module, resourcename)
    table = db[tablename]

    output = s3_rest_controller(module, resourcename)
    return output

# -----------------------------------------------------------------------------
def irs_rheader(r):

    """ Resource Headers for IRS """

    if r.representation == "html":
        if r.record is None:
            # List or Create form: rheader makes no sense here
            return None

        tabs = [(T("Report Details"), None),
                #(T("Photos"), "image")
                #(T("Documents"), "document"),
               ]
        if deployment_settings.has_module("vehicle"):
            tabs.append((T("Vehicles"), "vehicle"))

        if deployment_settings.has_module("hrm"):
            tabs.append((T("Staff"), "human_resource"))

        #if deployment_settings.has_module("project"):
        #    tabs.append((T("Tasks"), "task"))

        tabs.append((T("Dispatch"), "dispatch"))

        rheader_tabs = s3_rheader_tabs(r, tabs)

        if r.name == "ireport":
            report = r.record
            #reporter = report.person_id
            #if reporter:
            #    reporter = person_represent(reporter)
            location = report.location_id
            if location:
                location = gis_location_represent(location)
            #create_request = A(T("Create Request"),
            #                   _class="action-btn colorbox",
            #                   _href=URL(c="req", f="req",
            #                             args="create",
            #                             vars={"format":"popup",
            #                                   "caller":"irs_ireport"}),
            #                  _title=T("Add Request"))
            #create_task = A(T("Create Task"),
            #                _class="action-btn colorbox",
            #                _href=URL(c="project", f="task",
            #                          args="create",
            #                          vars={"format":"popup",
            #                                "caller":"irs_ireport"}),
            #                _title=T("Add Task"))
            
            category = report.category or ""
            if category:
                category = "%s: %s" % (category,
                                       response.s3.irs_incident_type_opts.get(int(category), ""))
            
            rheader = DIV(TABLE(
                            TR(
                                TH("%s: " % T("Short Description")), report.name,
                                TH("%s: " % T("Date")), report.datetime,
                            TR(
                                TH("%s: " % T("Category")), category,
                                TH("%s: " % T("Reporter")), report.person),
                                ),
                            TR(
                                TH("%s: " % T("Location")), location,
                                TH("%s: " % T("Contacts")), report.contact,
                                ),
                            TR(
                                TH("%s: " % T("Incident Commander")),
                                   TD(hr_represent(report.human_resource_id) or "",
                                      _rowspan=3),
                                ),
                            TR(
                                TH("%s: " % T("Details")), TD(report.message or "",
                                                              _rowspan=3),
                                )
                            ),
                          #DIV(P(), create_request, " ", create_task, P()),
                          rheader_tabs)

        return rheader

    else:
        return None

# -----------------------------------------------------------------------------
def ireport():

    """ Incident Reports, RESTful controller """

    tablename = "%s_%s" % (module, resourcename)
    table = db[tablename]

    # Filter out Closed Reports
    response.s3.filter = (table.closed == False)

    # Non-Editors should only see a limited set of options
    #if not s3_has_role(EDITOR):
    #    irs_incident_type_opts = response.s3.irs_incident_type_opts
    #    allowed_opts = [irs_incident_type_opts.get(opt.code, opt.code) for opt in db().select(db.irs_icategory.code)]
    #    allowed_opts.sort()
    #    table.category.requires = IS_NULL_OR(IS_IN_SET(allowed_opts))

    type = request.get_vars.get("type", None)
    if type == "fire":
        table.category.default = 1100
    elif type == "rescue":
        table.category.default = 8201
    elif type == "hazmat":
        table.category.default = 6102

    # Pre-processor
    def prep(r):
        table = r.table
        if r.method == "ushahidi":
            auth.settings.on_failed_authorization = r.url(method="", vars=None)
            # Allow the 'XX' levels
            db.gis_location.level.requires = IS_NULL_OR(IS_IN_SET(
                gis.get_all_current_levels()))
        elif r.interactive:
            if r.method == "update":
                table.dispatch.writable = True
                table.verified.writable = True
                table.closed.writable = True
            elif r.method == "create" or r.method == None:
                table.datetime.default = request.utcnow
                #table.person_id.default = s3_logged_in_person()
            if r.component:
                if r.component_name == "image":
                    db.doc_image.date.default = r.record.datetime.date()
                    db.doc_image.location_id.default = r.record.location_id
                    db.doc_image.location_id.readable = db.doc_image.location_id.writable = False
                    db.doc_image.organisation_id.readable = db.doc_image.organisation_id.writable = False
                    db.doc_image.url.readable = db.doc_image.url.writable = False
                    db.doc_image.person_id.readable = db.doc_image.person_id.writable = False
                elif r.component_name == "human_resource":
                    # Filter Vehicle dropdown to just those vehicles assigned to this incident
                    s3mgr.load("asset_asset")
                    asset_represent = response.s3.asset_represent
                    atable = db.asset_asset
                    itable = db.irs_ireport_vehicle
                    query = (atable.id == itable.asset_id) & \
                            (itable.ireport_id == r.id) & \
                            (itable.deleted == False)
                    table = db.irs_ireport_vehicle_human_resource
                    table.asset_id.requires = IS_NULL_OR(IS_ONE_OF(db(query),
                                                         "asset_asset.id",
                                                         asset_represent,
                                                         sort=True))

                    s3.crud.submit_button = T("Assign")
                    s3.crud_strings["irs_ireport_vehicle_human_resource"] = Storage(
                        title_create = T("Assign Human Resource"),
                        title_display = T("Human Resource Details"),
                        title_list = T("List Assigned Human Resources"),
                        title_update = T("Edit Human Resource"),
                        title_search = T("Search Assigned Human Resources"),
                        subtitle_create = T("Assign New Human Resource"),
                        subtitle_list = T("Human Resource Assignments"),
                        label_list_button = T("List Assigned Human Resources"),
                        label_create_button = T("Assign Human Resource"),
                        label_delete_button = T("Remove Human Resource from this incident"),
                        msg_record_created = T("Human Resource assigned"),
                        msg_record_modified = T("Human Resource Assignment updated"),
                        msg_record_deleted = T("Human Resource unassigned"),
                        msg_list_empty = T("No Human Resources currently assigned to this incident"))
                elif r.component_name == "vehicle":

                    # Virtual Fields
                    class vehicle_virtualfields(dict, object):
                        # Fields to be loaded by sqltable as qfields
                        # without them being list_fields
                        # (These cannot contain VirtualFields)
                        extra_fields = [
                                    #"problem_id"
                                ]

                        def food(self):
                            itable = db.irs_ireport_vehicle
                            # Prevent recursive queries
                            try:
                                query = (itable.asset_id == self.irs_ireport_vehicle.asset_id) & \
                                        (itable.closed == False) & \
                                        (itable.deleted == False)
                            except AttributeError:
                                # We are being instantiated inside one of the other methods
                                return None
                            arrival = db(query).select(itable.datetime,
                                                       limitby=(0, 1)).first()
                            if arrival:
                                output = arrival.datetime
                            else:
                                output = UNKNOWN
                            return output

                        def fuel(self):
                            itable = db.irs_ireport_vehicle
                            # Prevent recursive queries
                            try:
                                query = (itable.asset_id == self.irs_ireport_vehicle.asset_id) & \
                                        (itable.closed == False) & \
                                        (itable.deleted == False)
                            except AttributeError:
                                # We are being instantiated inside one of the other methods
                                return None
                            vehicle = db(query).select(itable.asset_id,
                                                       limitby=(0, 1)).first()
                            if vehicle:
                                output = vehicle.asset_id
                            else:
                                output = UNKNOWN
                            return output

                    table.virtualfields.append(vehicle_virtualfields())

                    s3mgr.configure("irs_ireport_vehicle",
                                    list_fields=["id",
                                                 "asset_id",
                                                 "datetime",
                                                 "site_id",
                                                 "location_id",
                                                 "comments",
                                                 (T("Food"), "food"),
                                                 (T("Fuel"), "fuel")
                                                ])

                    s3.crud.submit_button = T("Assign")
                    s3.crud_strings["irs_ireport_vehicle"] = Storage(
                        title_create = T("Assign Vehicle"),
                        title_display = T("Vehicle Details"),
                        title_list = T("List Assigned Vehicles"),
                        title_update = T("Edit Vehicle Assignment"),
                        title_search = T("Search Vehicle Assignments"),
                        subtitle_create = T("Add New Vehicle Assignment"),
                        subtitle_list = T("Vehicle Assignments"),
                        label_list_button = T("List Vehicle Assignments"),
                        label_create_button = T("Add Vehicle Assignment"),
                        label_delete_button = T("Remove Vehicle from this incident"),
                        msg_record_created = T("Vehicle assigned"),
                        msg_record_modified = T("Vehicle Assignment updated"),
                        msg_record_deleted = T("Vehicle unassigned"),
                        msg_list_empty = T("No Vehicles currently assigned to this incident"))

        return True
    response.s3.prep = prep

    # Post-processor
    def user_postp(r, output):
        if not r.component:
            s3_action_buttons(r, deletable=False)
            if deployment_settings.has_module("assess"):
                response.s3.actions.append({"url" : URL(c="assess", f="basic_assess",
                                                        vars = {"ireport_id":"[id]"}),
                                            "_class" : "action-btn",
                                            "label" : "Assess"})
        return output
    response.s3.postp = user_postp

    output = s3_rest_controller(module, resourcename, rheader=irs_rheader)

    # @ToDo: Add 'Dispatch' button to send OpenGeoSMS
    #try:
    #    delete_btn = output["delete_btn"]
    #except:
    #    delete_btn = ""
    #buttons = DIV(delete_btn)
    #output.update(delete_btn=buttons)

    return output

# =============================================================================
