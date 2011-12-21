# -*- coding: utf-8 -*-

""" Incident Reporting System - Model

    @author: Sahana Taiwan Team
    @author: Fran Boon
"""

if deployment_settings.has_module("irs"):

    # Staff as component of Incident Reports
    if deployment_settings.has_module("vehicle"):
        link_table = "irs_ireport_vehicle_human_resource"
    else:
        link_table = "irs_ireport_human_resource"
    s3mgr.model.add_component("hrm_human_resource",
                              irs_ireport=Storage(
                                    link=link_table,
                                    joinby="ireport_id",
                                    key="human_resource_id",
                                    # Dispatcher doesn't need to Add/Edit records, just Link
                                    actuate="link",
                                    autocomplete="name",
                                    autodelete=False))

    def ireport_tables():
        """ Load the Incident Report Tables when required """

        module = "irs"

        # ---------------------------------------------------------------------
        # List of Incident Categories
        # The keys are based on the Canadian ems.incident hierarchy, with a few extra general versions added to 'other'
        # The values are meant for end-users, so can be customised as-required
        # NB It is important that the meaning of these entries is not changed as otherwise this hurts our ability to do synchronisation
        # Entries can be hidden from user view in the controller.
        # Additional sets of 'translations' can be added to the tuples.
        irs_incident_type_opts = {
            "animalHealth.animalDieOff": T("Animal Die Off"),
            "animalHealth.animalFeed": T("Animal Feed"),
            "aviation.aircraftCrash": T("Aircraft Crash"),
            "aviation.aircraftHijacking": T("Aircraft Hijacking"),
            "aviation.airportClosure": T("Airport Closure"),
            "aviation.airspaceClosure": T("Airspace Closure"),
            "aviation.noticeToAirmen": T("Notice to Airmen"),
            "aviation.spaceDebris": T("Space Debris"),
            "civil.demonstrations": T("Demonstrations"),
            "civil.dignitaryVisit": T("Dignitary Visit"),
            "civil.displacedPopulations": T("Displaced Populations"),
            "civil.emergency": T("Civil Emergency"),
            "civil.looting": T("Looting"),
            "civil.publicEvent": T("Public Event"),
            "civil.riot": T("Riot"),
            "civil.volunteerRequest": T("Volunteer Request"),
            "crime": T("Crime"),
            "crime.bomb": T("Bomb"),
            "crime.bombExplosion": T("Bomb Explosion"),
            "crime.bombThreat": T("Bomb Threat"),
            "crime.dangerousPerson": T("Dangerous Person"),
            "crime.drugs": T("Drugs"),
            "crime.homeCrime": T("Home Crime"),
            "crime.illegalImmigrant": T("Illegal Immigrant"),
            "crime.industrialCrime": T("Industrial Crime"),
            "crime.poisoning": T("Poisoning"),
            "crime.retailCrime": T("Retail Crime"),
            "crime.shooting": T("Shooting"),
            "crime.stowaway": T("Stowaway"),
            "crime.terrorism": T("Terrorism"),
            "crime.vehicleCrime": T("Vehicle Crime"),
            "fire": T("Fire"),
            "fire.forestFire": T("Forest Fire"),
            "fire.hotSpot": T("Hot Spot"),
            "fire.industryFire": T("Industry Fire"),
            "fire.smoke": T("Smoke"),
            "fire.urbanFire": T("Urban Fire"),
            "fire.wildFire": T("Wild Fire"),
            "flood": T("Flood"),
            "flood.damOverflow": T("Dam Overflow"),
            "flood.flashFlood": T("Flash Flood"),
            "flood.highWater": T("High Water"),
            "flood.overlandFlowFlood": T("Overland Flow Flood"),
            "flood.tsunami": T("Tsunami"),
            "geophysical.avalanche": T("Avalanche"),
            "geophysical.earthquake": T("Earthquake"),
            "geophysical.lahar": T("Lahar"),
            "geophysical.landslide": T("Landslide"),
            "geophysical.magneticStorm": T("Magnetic Storm"),
            "geophysical.meteorite": T("Meteorite"),
            "geophysical.pyroclasticFlow": T("Pyroclastic Flow"),
            "geophysical.pyroclasticSurge": T("Pyroclastic Surge"),
            "geophysical.volcanicAshCloud": T("Volcanic Ash Cloud"),
            "geophysical.volcanicEvent": T("Volcanic Event"),
            "hazardousMaterial": T("Hazardous Material"),
            "hazardousMaterial.biologicalHazard": T("Biological Hazard"),
            "hazardousMaterial.chemicalHazard": T("Chemical Hazard"),
            "hazardousMaterial.explosiveHazard": T("Explosive Hazard"),
            "hazardousMaterial.fallingObjectHazard": T("Falling Object Hazard"),
            "hazardousMaterial.infectiousDisease": T("Infectious Disease (Hazardous Material)"),
            "hazardousMaterial.poisonousGas": T("Poisonous Gas"),
            "hazardousMaterial.radiologicalHazard": T("Radiological Hazard"),
            "health.infectiousDisease": T("Infectious Disease"),
            "health.infestation": T("Infestation"),
            "ice.iceberg": T("Iceberg"),
            "ice.icePressure": T("Ice Pressure"),
            "ice.rapidCloseLead": T("Rapid Close Lead"),
            "ice.specialIce": T("Special Ice"),
            "marine.marineSecurity": T("Marine Security"),
            "marine.nauticalAccident": T("Nautical Accident"),
            "marine.nauticalHijacking": T("Nautical Hijacking"),
            "marine.portClosure": T("Port Closure"),
            "marine.specialMarine": T("Special Marine"),
            "meteorological.blizzard": T("Blizzard"),
            "meteorological.blowingSnow": T("Blowing Snow"),
            "meteorological.drought": T("Drought"),
            "meteorological.dustStorm": T("Dust Storm"),
            "meteorological.fog": T("Fog"),
            "meteorological.freezingDrizzle": T("Freezing Drizzle"),
            "meteorological.freezingRain": T("Freezing Rain"),
            "meteorological.freezingSpray": T("Freezing Spray"),
            "meteorological.hail": T("Hail"),
            "meteorological.hurricane": T("Hurricane"),
            "meteorological.rainFall": T("Rain Fall"),
            "meteorological.snowFall": T("Snow Fall"),
            "meteorological.snowSquall": T("Snow Squall"),
            "meteorological.squall": T("Squall"),
            "meteorological.stormSurge": T("Storm Surge"),
            "meteorological.thunderstorm": T("Thunderstorm"),
            "meteorological.tornado": T("Tornado"),
            "meteorological.tropicalStorm": T("Tropical Storm"),
            "meteorological.waterspout": T("Waterspout"),
            "meteorological.winterStorm": T("Winter Storm"),
            "missingPerson": T("Missing Person"),
            "missingPerson.amberAlert": T("Child Abduction Emergency"),   # http://en.wikipedia.org/wiki/Amber_Alert
            "missingPerson.missingVulnerablePerson": T("Missing Vulnerable Person"),
            "missingPerson.silver": T("Missing Senior Citizen"),          # http://en.wikipedia.org/wiki/Silver_Alert
            "publicService.emergencySupportFacility": T("Emergency Support Facility"),
            "publicService.emergencySupportService": T("Emergency Support Service"),
            "publicService.schoolClosure": T("School Closure"),
            "publicService.schoolLockdown": T("School Lockdown"),
            "publicService.serviceOrFacility": T("Service or Facility"),
            "publicService.transit": T("Transit"),
            "railway.railwayAccident": T("Railway Accident"),
            "railway.railwayHijacking": T("Railway Hijacking"),
            "roadway.bridgeClosure": T("Bridge Closed"),
            "roadway.hazardousRoadConditions": T("Hazardous Road Conditions"),
            "roadway.roadwayAccident": T("Road Accident"),
            "roadway.roadwayClosure": T("Road Closed"),
            "roadway.roadwayDelay": T("Road Delay"),
            "roadway.roadwayHijacking": T("Road Hijacking"),
            "roadway.roadwayUsageCondition": T("Road Usage Condition"),
            "roadway.trafficReport": T("Traffic Report"),
            "temperature.arcticOutflow": T("Arctic Outflow"),
            "temperature.coldWave": T("Cold Wave"),
            "temperature.flashFreeze": T("Flash Freeze"),
            "temperature.frost": T("Frost"),
            "temperature.heatAndHumidity": T("Heat and Humidity"),
            "temperature.heatWave": T("Heat Wave"),
            "temperature.windChill": T("Wind Chill"),
            "wind.galeWind": T("Gale Wind"),
            "wind.hurricaneForceWind": T("Hurricane Force Wind"),
            "wind.stormForceWind": T("Storm Force Wind"),
            "wind.strongWind": T("Strong Wind"),
            "other.buildingCollapsed": T("Building Collapsed"),
            "other.peopleTrapped": T("People Trapped"),
            "other.powerFailure": T("Power Failure"),
        }

        # This Table defines which Categories are visible to end-users
        tablename = "irs_icategory"
        table = db.define_table(tablename,
                                Field("code", label = T("Category"),
                                      requires = IS_IN_SET_LAZY(lambda: \
                                        sort_dict_by_values(irs_incident_type_opts)),
                                      represent = lambda opt: \
                                        irs_incident_type_opts.get(opt, opt)),
                                 *s3_timestamp())

        def irs_icategory_onvalidation(form):
            """
                Incident Category Validation:
                    Prevent Duplicates

                Done here rather than in .requires to maintain the dropdown.
            """

            table = db.irs_icategory
            category, error = IS_NOT_ONE_OF(db, "irs_icategory.code")(form.vars.code)
            if error:
                form.errors.code = error

            return False

        s3mgr.configure(tablename,
                        onvalidation=irs_icategory_onvalidation,
                        list_fields=[ "code" ])

        # ---------------------------------------------------------------------
        # Reports
        # This is a report of an Incident
        #
        # Incident Reports can be linked to Incidents through the event_incident_report table
        #
        # @ToDo: If not using the Events module, we could have a 'lead incident' to track duplicates?
        #

        # Porto codes
        irs_incident_type_opts = {
            1100:T("Fire"),
            6102:T("Hazmat"),
            8201:T("Rescue")
        }
        resourcename = "ireport"
        tablename = "%s_%s" % (module, resourcename)
        table = db.define_table(tablename,
                                super_link(db.sit_situation),
                                Field("name", label = T("Short Description"),
                                      requires = IS_NOT_EMPTY()),
                                Field("message", "text", label = T("Message"),
                                      represent = lambda text: \
                                        s3_truncate(text, length=48, nice=True)),
                                Field("category", label = T("Category"),
                                      # The full set available to Admins & Imports/Exports
                                      # (users use the subset by over-riding this in the Controller)
                                      #requires = IS_NULL_OR(IS_IN_SET_LAZY(lambda: \
                                      #   sort_dict_by_values(irs_incident_type_opts))),
                                      # Use this instead if a simpler set of Options required
                                      requires = IS_NULL_OR(IS_IN_SET(irs_incident_type_opts)),
                                      represent = lambda opt: \
                                            irs_incident_type_opts.get(opt, opt)),
                                # Better to use a plain text field than to clutter the PR
                                Field("person", label = T("Reporter Name"),
                                      comment = (T("At/Visited Location (not virtual)"))),
                                #person_id(label = T("Reporter Name"),
                                #          comment = (T("At/Visited Location (not virtual)"),
                                #                     s3_person_comment(T("Reporter Name"),
                                #                                       T("The person at the location who is reporting this incident (optional)")))),
                                Field("contact", label = T("Contact Details")),
                                #organisation_id(label = T("Assign to Org.")),
                                Field("datetime", "datetime",
                                      label = T("Date/Time of Alert"),
                                      widget = S3DateTimeWidget(future=0),
                                      requires = [IS_NOT_EMPTY(),
                                                  IS_UTC_DATETIME(allow_future=False)]),
                                location_id(),
                                human_resource_id(label=T("Incident Commander")),
                                Field("dispatch", "datetime",
                                      # We don't want these visible in Create forms
                                      # (we override in Update forms in controller)
                                      writable = False, readable = False,
                                      label = T("Date/Time of Dispatch"),
                                      widget = S3DateTimeWidget(future=0),
                                      requires = IS_EMPTY_OR(IS_UTC_DATETIME(allow_future=False))),
                                Field("verified", "boolean",    # Ushahidi-compatibility
                                      # We don't want these visible in Create forms
                                      # (we override in Update forms in controller)
                                      writable = False, readable = False,
                                      label = T("Verified?"),
                                      represent = lambda verified: \
                                            (T("No"),
                                             T("Yes"))[verified == True]),
                                Field("closed", "boolean",
                                      # We don't want these visible in Create forms
                                      # (we override in Update forms in controller)
                                      default = False,
                                      writable = False, readable = False,
                                      label = T("Closed?"),
                                      represent = lambda closed: \
                                            (T("No"),
                                             T("Yes"))[closed == True]),
                                s3_comments(),
                                *s3_meta_fields())

        # CRUD strings
        ADD_INC_REPORT = T("Add Incident Report")
        LIST_INC_REPORTS = T("List Incident Reports")
        s3.crud_strings[tablename] = Storage(
            title_create = ADD_INC_REPORT,
            title_display = T("Incident Report Details"),
            title_list = LIST_INC_REPORTS,
            title_update = T("Edit Incident Report"),
            title_search = T("Search Incident Reports"),
            subtitle_create = T("Add New Incident Report"),
            subtitle_list = T("Incident Reports"),
            label_list_button = LIST_INC_REPORTS,
            label_create_button = ADD_INC_REPORT,
            label_delete_button = T("Delete Incident Report"),
            msg_record_created = T("Incident Report added"),
            msg_record_modified = T("Incident Report updated"),
            msg_record_deleted = T("Incident Report deleted"),
            msg_list_empty = T("No Incident Reports currently registered"))

        s3mgr.configure(tablename,
                        super_entity = db.sit_situation,
                        # Open tabs after creation
                        create_next = URL(args=["[id]", "update"]),
                        update_next = URL(args=["[id]", "update"]),
                        list_fields = ["id",
                                       "name",
                                       "category",
                                       "location_id",
                                       #"organisation_id",
                                       "verified",
                                       "message",
                                    ])

        ireport_id = S3ReusableField("ireport_id", table,
                                      requires = IS_NULL_OR(IS_ONE_OF(db, "irs_ireport.id", "%(name)s")),
                                      represent = lambda id: (id and [db.irs_ireport[id].name] or [NONE])[0],
                                      label = T("Incident"),
                                      ondelete = "RESTRICT")

        # ---------------------------------------------------------------------
        @auth.s3_requires_membership(1) # must be Administrator
        def irs_ushahidi_import(r, **attr):
            """
                Import Incident Reports from Ushahidi

                @ToDo: Deployment setting for Ushahidi instance URL
            """

            if r.representation == "html" and \
               r.name == "ireport" and not r.component and not r.id:

                url = r.get_vars.get("url", "http://")

                title = T("Incident Reports")
                subtitle = T("Import from Ushahidi Instance")

                form = FORM(TABLE(TR(
                            TH("URL: "),
                            INPUT(_type="text", _name="url", _size="100", _value=url,
                                  requires=[IS_URL(), IS_NOT_EMPTY()]),
                            TH(DIV(SPAN("*", _class="req", _style="padding-right: 5px;")))),
                            TR(TD("Ignore Errors?: "),
                            TD(INPUT(_type="checkbox", _name="ignore_errors", _id="ignore_errors"))),
                            TR("", INPUT(_type="submit", _value=T("Import")))))

                label_list_btn = s3base.S3CRUD.crud_string(r.tablename, "title_list")
                list_btn = A(label_list_btn,
                             _href=r.url(method="", vars=None),
                             _class="action-btn")

                rheader = DIV(P("%s: http://wiki.ushahidi.com/doku.php?id=ushahidi_api" % T("API is documented here")),
                              P("%s URL: http://ushahidi.my.domain/api?task=incidents&by=all&resp=xml&limit=1000" % T("Example")))

                output = dict(title=title, form=form, subtitle=subtitle, list_btn=list_btn, rheader=rheader)

                if form.accepts(request.vars, session):

                    # "Exploit" the de-duplicator hook to count import items
                    import_count = [0]
                    def count_items(job, import_count = import_count):
                        if job.tablename == "irs_ireport":
                            import_count[0] += 1
                    s3mgr.configure("irs_report", deduplicate=count_items)

                    ireports = r.resource
                    ushahidi = form.vars.url

                    ignore_errors = form.vars.get("ignore_errors", None)

                    stylesheet = os.path.join(request.folder, "static", "formats", "ushahidi", "import.xsl")

                    if os.path.exists(stylesheet) and ushahidi:
                        try:
                            success = ireports.import_xml(ushahidi,
                                                          stylesheet=stylesheet,
                                                          ignore_errors=ignore_errors)
                        except:
                            import sys
                            e = sys.exc_info()[1]
                            response.error = e
                        else:
                            if success:
                                count = import_count[0]
                                if count:
                                    response.flash = "%s %s" % (import_count[0],
                                                                T("reports successfully imported."))
                                else:
                                    response.flash = T("No reports available.")
                            else:
                                response.error = s3mgr.error


                response.view = "create.html"
                return output

            else:
                raise HTTP(501, BADMETHOD)

        s3mgr.model.set_method(module, "ireport",
                               method="ushahidi",
                               action=irs_ushahidi_import)

        # ---------------------------------------------------------------------
        def irs_dispatch(r, **attr):
            """
                Send a Dispatch notice from an Incident Report
                - this will be formatted as an OpenGeoSMS
            """

            if r.representation == "html" and \
               r.name == "ireport" and r.id and not r.component:

                s3mgr.load("msg_outbox")
                msg_compose = response.s3.msg_compose

                record = r.record
                text = "%s %s:%s; %s" % (record.name,
                                         T("Contact"),
                                         record.contact,
                                         record.message)

                message = msg.prepare_opengeosms(record.location_id,
                                                 code="ST",
                                                 map="google",
                                                 text=text)

                output = msg_compose(type="SMS",
                                     recipient_type = "pr_person",
                                     message = message,
                                     redirect_module = "irs",
                                     redirect_function = "ireport",
                                     redirect_args = r.id)

                # Maintain RHeader for consistency
                rheader = irs_rheader(r)

                title = T("Send Dispatch Update")

                output.update(title=title,
                              rheader=rheader)

                #if form.accepts(request.vars, session):

                response.view = "msg/compose.html"
                return output

            else:
                raise HTTP(501, BADMETHOD)

        s3mgr.model.set_method(module, "ireport",
                               method="dispatch",
                               action=irs_dispatch)

        # ---------------------------------------------------------------------
        # Link Tables for iReports
        # @ToDo: Make these conditional on Event not being activated?
        # ---------------------------------------------------------------------
        if deployment_settings.has_module("hrm"):
            tablename = "irs_ireport_human_resource"
            table = db.define_table(tablename,
                                    ireport_id(),
                                    # Simple dropdown is faster for a small team
                                    human_resource_id(widget=None),
                                    *s3_meta_fields())

        if deployment_settings.has_module("vehicle"):
            s3mgr.load("asset_asset")
            asset_id = response.s3.asset_id
            asset_represent = response.s3.asset_represent
            tablename = "irs_ireport_vehicle"
            table = db.define_table(tablename,
                                    ireport_id(),
                                    asset_id(label = T("Vehicle")),
                                    Field("datetime", "datetime",
                                          label=T("Dispatch Time"),
                                          widget = S3DateTimeWidget(future=0),
                                          requires = IS_EMPTY_OR(IS_UTC_DATETIME(allow_future=False)),
                                          default = request.utcnow),
                                    site_id,
                                    location_id(label=T("Destination")),
                                    Field("closed",
                                          # @ToDo: Close all assignments when Incident closed
                                          readable=False,
                                          writable=False),
                                    s3_comments(),
                                    *s3_meta_fields())

            atable = db.asset_asset
            query = (atable.type == s3.asset.ASSET_TYPE_VEHICLE) & \
                    (atable.deleted == False) & \
                    ((table.id == None) | \
                     (table.closed == True) | \
                     (table.deleted == True))
            left = table.on(atable.id == table.asset_id)
            table.asset_id.requires = IS_NULL_OR(IS_ONE_OF(db(query),
                                                           "asset_asset.id",
                                                           asset_represent,
                                                           left=left,
                                                           sort=True))
            table.site_id.label = T("Fire Station")
            table.site_id.readable = True
            # Populated from fire_station_vehicle
            #table.site_id.writable = True

            def ireport_onaccept(form):
                """
                    Assign the appropriate vehicle & on-shift team to the incident
                    @ToDo: Specialist teams
                    @ToDo: Make more generic
                """
                
                vars = form.vars
                ireport = vars.id
                category = vars.category
                if category == "1100":
                    # Fire
                    types = ["VUCI", "ABSC"]
                elif category == "6102":
                    # Hazmat
                    types = ["VUCI", "VCOT"]
                elif category == "8201":
                    # Rescue
                    types = ["VLCI", "ABSC"]
                else:
                    types = ["VLCI"]

                # 1st unassigned vehicle
                # @ToDo: Filter by Org/Base
                # @ToDo: Filter by those which are under repair (asset_log)
                s3mgr.load("fire_station_vehicle")
                table = db.irs_ireport_vehicle
                atable = db.asset_asset
                vtable = db.vehicle_vehicle
                for type in types:
                    query = (atable.type == s3.asset.ASSET_TYPE_VEHICLE) & \
                            (vtable.type == type) & \
                            (vtable.asset_id == atable.id) & \
                            (atable.deleted == False) & \
                            ((table.id == None) | \
                             (table.closed == True) | \
                             (table.deleted == True))
                    left = table.on(atable.id == table.asset_id)
                    vehicle = db(query).select(atable.id,
                                               left=left,
                                               limitby=(0, 1)).first()
                    if vehicle:
                        s3mgr.load("vehicle_vehicle")
                        vehicle = vehicle.id
                        query = (vtable.asset_id == vehicle) & \
                                (db.fire_station_vehicle.vehicle_id == vtable.id) & \
                                (db.fire_station.id == db.fire_station_vehicle.station_id) & \
                                (db.org_site.id == db.fire_station.site_id)
                        site = db(query).select(db.org_site.id,
                                                limitby=(0, 1)).first()
                        if site:
                            site = site.id
                        db.irs_ireport_vehicle.insert(ireport_id=ireport,
                                                      asset_id=vehicle,
                                                      site_id=site)
                        if deployment_settings.has_module("hrm"):
                            # Assign 1st 5 human resources on-shift
                            # @ToDo: Filter by Base
                            table = db.irs_ireport_vehicle_human_resource
                            htable = db.hrm_human_resource
                            on_shift = response.s3.fire_staff_on_duty()
                            query = on_shift & \
                                    ((table.id == None) | \
                                     (table.closed == True) | \
                                     (table.deleted == True))
                            left = table.on(htable.id == table.human_resource_id)
                            people = db(query).select(htable.id,
                                                      left=left,
                                                      limitby=(0, 5))
                            # @ToDo: Find Ranking person to be team leader
                            leader = people.first()
                            if leader:
                                leader = leader.id
                            query = (db.irs_ireport.id == ireport)
                            db(query).update(human_resource_id=leader)
                            for person in people:
                                table.insert(ireport_id=ireport,
                                             asset_id=vehicle,
                                             human_resource_id=person.id)
                
            s3mgr.configure("irs_ireport",
                            create_onaccept=ireport_onaccept,
                            create_next=URL(args=["[id]", "human_resource"]),
                            update_next=URL(args=["[id]", "update"]))

            if deployment_settings.has_module("hrm"):
                tablename = "irs_ireport_vehicle_human_resource"
                table = db.define_table(tablename,
                                        ireport_id(),
                                        # Simple dropdown is faster for a small team
                                        human_resource_id(represent=hr_represent,
                                                          requires = IS_ONE_OF(db,
                                                                               "hrm_human_resource.id",
                                                                               hr_represent,
                                                                               #orderby="pr_person.first_name"
                                                                               ),
                                                          widget=None),
                                        asset_id(label = T("Vehicle")),
                                        Field("closed",
                                              # @ToDo: Close all assignments when Incident closed
                                              readable=False,
                                              writable=False),
                                        *s3_meta_fields())
            
        # ---------------------------------------------------------------------
        # Pass variables back to global scope (response.s3.*)
        return dict(
            ireport_id = ireport_id,
            irs_incident_type_opts = irs_incident_type_opts,
            )

    # Provide a handle to this load function
    s3mgr.loader(ireport_tables,
                 "irs_icategory",
                 "irs_ireport",
                 # @ToDo: Make this optional when Vehicle module is active
                 "irs_ireport_vehicle")
else:
    def ireport_id(**arguments):
        """ Allow FKs to be added safely to other models in case module disabled """
        return Field("ireport_id", "integer", readable=False, writable=False)
    response.s3.ireport_id = ireport_id

# END =========================================================================
