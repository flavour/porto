# -*- coding: utf-8 -*-

module = request.controller
resourcename = request.function

s3_menu("fire")

# -----------------------------------------------------------------------------
def index():
    """ Module Homepage """

    # @todo: have a link to the fire station the current user works at

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name

    return dict(module_name=module_name)


# -----------------------------------------------------------------------------
def station():
    """ Fire Station """

    tabs =[
            (T("Station Details"), None),
            (T("Vehicles"), "vehicle"),
            (T("Staff"), "human_resource"),
            #(T("Shifts"), "shift"),
            (T("Roster"), "shift_staff"),
            (T("Vehicle Deployments"), "vehicle_report"),
          ]

    csv_template = "station"
    csv_extra_fields = [
        dict(label="Country",
             field=location_id("country_id",
                               label=T("Country"),
                               requires = IS_NULL_OR(
                                            IS_ONE_OF(db,
                                                      "gis_location.id",
                                                      "%(name)s",
                                                      filterby = "level",
                                                      filter_opts = ["L0"],
                                                      sort=True)),
                                widget = None)),
        dict(label="Organisation",
             field=organisation_id())
    ]

    return s3_rest_controller("fire", "station",
                              rheader=lambda r: fire_rheader(r, tabs=tabs),
                              csv_template = csv_template,
                              csv_extra_fields = csv_extra_fields)

# -----------------------------------------------------------------------------
def station_vehicle():
    """ Vehicles of Fire Stations """

    response.s3.prep = lambda r: r.method == "import"

    csv_template = "station_vehicle"
    return s3_rest_controller("fire", "station_vehicle",
                              csv_template = csv_template)

# -----------------------------------------------------------------------------
def water_source():
    """ Water Sources """

    return s3_rest_controller("fire", "water_source")


# -----------------------------------------------------------------------------
def hazard_point():
    """ Hazard Points """

    return s3_rest_controller("fire", "hazard_point")

# -----------------------------------------------------------------------------
def person():
    """ Person Controller for Ajax Requests """

    return s3_rest_controller("pr", "person")

# -----------------------------------------------------------------------------
def ireport_vehicle():

    return s3_rest_controller("irs", "ireport_vehicle")

# -----------------------------------------------------------------------------
def fire_rheader(r, tabs=[]):
    """ Resource headers for component views """

    rheader = None
    rheader_tabs = s3_rheader_tabs(r, tabs)

    if r.representation == "html":

        if r.name == "station":
            station = r.record
            if station:
                rheader = DIV(rheader_tabs)

    return rheader

# -----------------------------------------------------------------------------
