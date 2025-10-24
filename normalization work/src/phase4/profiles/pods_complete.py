from typing import Dict
from ..base_profile import BaseDocumentProfile

class PODsProfile(BaseDocumentProfile):
    @property
    def doc_type(self) -> str:
        return "PODs"

    @property
    def template_name(self) -> str:
        return "PODsMaster.docx"

    @property
    def filename_suffix(self) -> str:
        return "Discovery Propounded PODs"

    @property
    def first_set_only_flags(self) -> list[str]:
        return ["IsOwner", "IsManager"]  # No SROGsGeneral

    @property
    def interrogatory_counts(self) -> Dict[str, int]:
        return {
            # Profile-specific flags
            "IsOwner": 6,                     # Owner documents
            "IsManager": 1,                 # Manager documents
            "IsOwnerManager": 40,            # Combined owner/manager documents
            
            # Insects - Medium counts for PODs
            "HasAnts": 3,
            "HasRoaches": 4,                  # Roach documents
            "HasFlies": 2,
            "HasBedbugs": 4,                  # Bedbug documents
            "HasBees": 1,
            "HasWasps": 1,
            "HasHornets": 1,
            "HasSpiders": 2,
            "HasTermites": 2,
            "HasMosquitos": 1,

            # Vermin - Medium counts for PODs
            "HasRatsMice": 6,
            "HasSkunks": 2,
            "HasBats": 1,
            "HasRacoons": 2,
            "HasPigeons": 1,
            "HasOpossums": 1,
            "HasVermin": 8,                   # Aggregate

            # HVAC Issues
            "HasHeater": 5,                  # Heater documents
            "HasAC": 5,                      # AC documents
            "HasVentilation": 3,
            "HasHvac": 6,                    # Aggregate

            # Electrical Issues
            "HasOutlets": 2,
            "HasPanel": 1,
            "HasWallSwitches": 1,
            "HasExteriorLighting": 1,
            "HasInteriorLighting": 2,
            "HasLightFixtures": 1,
            "HasFans": 1,
            "HasElectrical": 3,              # Aggregate

            # Plumbing Issues
            "HasToilet": 1,
            "HasShower": 1,
            "HasBath": 1,
            "HasFixtures": 1,
            "HasLeaks": 2,
            "HasInsufficientWaterPressure": 1,
            "HasNoHotWater": 2,
            "HasSewageComingOut": 3,
            "HasCloggedToilet": 1,
            "HasCloggedBath": 1,
            "HasCloggedSink": 1,
            "HasCloggedShower": 1,
            "HasNoCleanWaterSupply": 2,
            "HasNoColdWater": 1,
            "HasUnsanitaryWater": 2,
            "HasClogs": 2,                   # Aggregate
            "HasPlumbing": 3,                # Aggregate

            # Fire Hazard Issues
            "HasSmokeAlarms": 1,
            "HasFireExtinguisher": 1,
            "HasNonCompliantElectricity": 2,
            "HasNonGfiElectricalOutlets": 1,
            "HasCarbonmonoxideDetectors": 1,
            "HasFireHazard": 3,              # Aggregate

            # Government Contact Issues
            "HasDepartmentOfEnvironmentalHealth": 1,
            "HasDepartmentOfPublicHealth": 1,
            "HasDepartmentOfHealthServices": 1,
            "HasFireDepartment": 1,
            "HasPoliceDepartment": 1,
            "HasCodeEnforcement": 1,
            "HasGovContact": 2,               # Aggregate

            # Appliance Issues
            "HasStove": 1,
            "HasDishwasher": 1,
            "HasWasherDryer": 2,
            "HasOven": 1,
            "HasMicrowave": 1,
            "HasGarbageDisposal": 1,
            "HasRefrigerator": 1,
            "HasAppliances": 2,              # Aggregate

            # Cabinet Issues
            "HasCabinets": 1,
            "HasCabinetsBroken": 1,
            "HasCabinetHinges": 1,
            "HasCabinetAlignment": 1,

            # Flooring Issues
            "HasUnevenFlooring": 1,
            "HasCarpet": 1,
            "HasTiles": 1,
            "HasNailsStickingOut": 1,
            "HasFloors": 2,                  # Aggregate

            # Window Issues
            "HasBrokenWindows": 2,
            "HasWindowScreens": 1,
            "HasWindowLeaks": 1,
            "HasWindowsDoNotLock": 1,
            "HasMissingWindows": 1,
            "HasBrokenMissingScreens": 1,
            "HasWindows": 2,                # Aggregate

            # Door Issues
            "HasBrokenDoors": 10,            # Door documents
            "HasDoorKnobs": 1,
            "HasDoorLocks": 1,
            "HasBrokenHinges": 1,
            "HasSlidingGlassDoors": 1,
            "HasIneffectiveWaterproofing": 1,
            "HasWaterIntrusionInsects": 1,
            "HasDoorsDoNotCloseProperly": 1,
            "HasDoors": 3,                   # Aggregate

            # Structure Issues
            "HasHoleInCeiling": 1,
            "HasBumpsInCeiling": 1,
            "HasWaterStainsOnCeiling": 1,
            "HasWaterStainsOnWall": 1,
            "HasHoleInWall": 1,
            "HasPaint": 1,
            "HasExteriorDeckPorch": 1,
            "HasWaterproofToilet": 1,
            "HasWaterproofTub": 1,
            "HasStaircase": 1,
            "HasBasementFlood": 1,
            "HasLeaksInGarage": 1,
            "HasIneffectiveWeatherproofingOfAnyWindowsDoors": 1,
            "HasIneffectiveWaterproofingOfTheTubsToilet": 1,
            "HasSoftSpotsDueToLeaks": 1,
            "HasHolesInCeilingWalls": 1,     # Aggregate
            "HasWaterStainsOnCeilingWalls": 1, # Aggregate
            "HasStructure": 2,               # Aggregate

            # Common Area Issues
            "HasMailboxBroken": 1,
            "HasParkingAreaIssues": 1,
            "HasDamageToCars": 1,
            "HasFlooding": 1,
            "HasEntrancesBlocked": 1,
            "HasSwimmingPool": 1,
            "HasJacuzzi": 1,
            "HasLaundryRoom": 1,
            "HasRecreationRoom": 1,
            "HasGym": 1,
            "HasBlockedAreasDoors": 1,
            "HasElevator": 4,                # Elevator documents
            "HasFilthRubbishGarbage": 1,
            "HasCommonAreaVermin": 1,
            "HasBrokenGate": 1,
            "HasCommonAreaInsects": 1,
            "HasCommonArea": 2,              # Aggregate

            # Nuisance Issues
            "HasDrugs": 1,
            "HasSmoking": 1,
            "HasNoisyNeighbors": 1,
            "HasGangs": 1,
            "HasNuisance": 2,                # Aggregate

            # Health Hazards
            "HasMold": 4,                    # Mold-related documents
            "HasMildew": 1,
            "HasMushrooms": 1,
            "HasRawSewageOnExterior": 1,
            "HasNoxiousFumes": 1,
            "HasChemicalsPaintContamination": 1,
            "HasToxicWaterPollution": 1,
            "HasOffensiveOdors": 1,
            "HasHealthHazards": 2,          # Aggregate

            # Harassment Issues
            "HasUnlawfulDetainer": 1,
            "HasEvictionThreat": 1,
            "HasHarrassmentByDefendants": 1,
            "HasHarrassmentMaintenanceManWorkers": 1,
            "HasHarrassmentManagerStaff": 1,
            "HasHarrassmentByOwnerAndTheirGuests": 1,
            "HasHarrassmentOtherTenants": 1,
            "HasIllegitimateNotices": 1,
            "HasRefusalToMakeTimelyRepairs": 1,
            "HasWrittenThreats": 1,
            "HasAggressiveInappropriateLanguage": 1,
            "HasPhysicalThreatsOrTouching": 1,
            "HasNoticesSinglingOutOneTenant": 1,
            "HasDuplicativeNotices": 1,
            "HasUntimelyResponseFromLandlord": 1,
            "HasHarassment": 2,              # Aggregate

            # Notice Issues
            "HasNotices": 1,
            "Has24HourNotices": 1,
            "Has3DayNotices": 1,
            "Has30DayNotices": 1,
            "Has60DayNotices": 1,
            "HasToQuitNotices": 1,
            "HasPerformOrQuit": 1,

            # Utility Issues
            "HasWaterShutoffs": 1,
            "HasGasLeaks": 1,
            "HasElectricityShutoffs": 1,
            "HasHeatShutoffs": 1,
            "HasGasShutoffs": 1,

            # Safety Issues
            "HasSafety": 1,
            "HasInoperableLocks": 1,
            "HasBrokenSecurityGate": 1,
            "HasSecurityCameras": 1,
            "HasBrokenBuzzerToGetIn": 1,

            # Miscellaneous Issues
            "HasInjury": 1,
            "HasNonresponsiveLandlord": 1,
            "HasUnauthorizedEntries": 1,
            "HasStolenItems": 1,
            "HasDamagedItems": 1,

            # Discrimination Issues
            "HasAgeDiscrimination": 1,
            "HasDisabilityDiscrimination": 1,
            "HasRacialDiscrimination": 1,
            "HasSecurityDeposit": 22,        # Security deposit documents

            # Trash Issues
            "HasTrashProblems": 1,
            "HasInadequateNumberOfTrashReceptacles": 1,
            "HasInadequateServicingAndEmptyingTrashReceptacles": 1,

            # City Issues
            "HasLosAngeles": 1,              # LA-specific
        }

    def add_profile_specific_flags(self, dataset: dict) -> dict:
        """Add PODs-specific flags."""
        flags = dataset['flags']

        # Remove SROGsGeneral if present
        flags.pop('SROGsGeneral', None)

        # Add defendant role flags
        defendant_role = dataset.get('defendant', {}).get('role', '')
        is_owner = defendant_role.lower() == 'owner'
        is_manager = defendant_role.lower() == 'manager'
        
        flags['IsOwner'] = is_owner
        flags['IsManager'] = is_manager
        flags['IsOwnerManager'] = is_owner or is_manager

        return dataset
