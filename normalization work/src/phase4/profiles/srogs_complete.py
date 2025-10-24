from typing import Dict
from ..base_profile import BaseDocumentProfile

class SROGsProfile(BaseDocumentProfile):
    @property
    def doc_type(self) -> str:
        return "SROGs"

    @property
    def template_name(self) -> str:
        return "SROGsMaster.docx"

    @property
    def filename_suffix(self) -> str:
        return "Discovery Propounded SROGs"

    @property
    def first_set_only_flags(self) -> list[str]:
        return ["SROGsGeneral", "IsOwner", "IsManager"]

    @property
    def interrogatory_counts(self) -> Dict[str, int]:
        return {
            # Profile-specific flags (Set 1 only)
            "SROGsGeneral": 56,              # General questions (Set 1 only)
            "IsOwner": 22,                  # Owner-specific questions
            "IsManager": 20,                # Manager-specific questions
            
            # Insects - Highest counts for SROGs
            "HasAnts": 12,
            "HasRoaches": 13,               # Roach infestation
            "HasFlies": 10,
            "HasBedbugs": 13,               # Bedbug infestation
            "HasBees": 4,
            "HasWasps": 6,
            "HasHornets": 5,
            "HasSpiders": 8,
            "HasTermites": 7,
            "HasMosquitos": 3,

            # Vermin - Highest counts for SROGs
            "HasRatsMice": 18,
            "HasSkunks": 6,
            "HasBats": 5,
            "HasRaccoons": 7,
            "HasPigeons": 4,
            "HasOpossums": 3,
            "HasVermin": 20,                # Aggregate

            # HVAC Issues
            "HasHeater": 7,                 # Heater issues
            "HasAC": 7,                     # AC issues
            "HasVentilation": 6,
            "HasHVAC": 8,                   # Aggregate

            # Electrical Issues
            "HasOutlets": 8,
            "HasPanel": 6,
            "HasWallSwitches": 5,
            "HasExteriorLighting": 4,
            "HasInteriorLighting": 6,
            "HasLightFixtures": 5,
            "HasFans": 3,
            "HasElectricalIssues": 10,            # Aggregate

            # Plumbing Issues
            "HasToilet": 6,
            "HasShower": 6,
            "HasBath": 4,
            "HasFixtures": 5,
            "HasLeaks": 12,
            "HasInsufficientWaterPressure": 8,
            "HasNoHotWater": 10,
            "HasSewageComingOut": 15,
            "HasCloggedToilets": 8,
            "HasCloggedBath": 6,
            "HasCloggedSinks": 7,
            "HasCloggedShower": 6,
            "HasNoCleanWaterSupply": 12,
            "HasNoColdWater": 8,
            "HasUnsanitaryWater": 14,
            "HasClogs": 9,                  # Aggregate
            "HasPlumbingIssues": 12,              # Aggregate

            # Fire Hazard Issues
            "HasSmokeAlarms": 8,
            "HasFireExtinguisher": 6,
            "HasNonCompliantElectricity": 10,
            "HasNonGFIOutletsNearWater": 8,
            "HasCarbonMonoxideDetectors": 7,
            "HasFireHazardIssues": 12,            # Aggregate

            # Government Contact Issues
            "HasDepartmentOfEnvironmentalHealth": 8,
            "HasDepartmentOfPublicHealth": 6,
            "HasDepartmentOfHealthServices": 5,
            "HasFireDepartment": 4,
            "HasPoliceDepartment": 6,
            "HasCodeEn": 7,
            "HasGovernmentEntityContacted": 10,            # Aggregate

            # Appliance Issues
            "HasStove": 6,
            "HasDishwasher": 5,
            "HasWasherDryer": 7,
            "HasOven": 4,
            "HasMicrowave": 4,
            "HasGarbageDisposal": 3,
            "HasRefrigerator": 6,
            "HasAppliances": 8,             # Aggregate

            # Cabinet Issues
            "HasCabinets": 3,
            "HasCabinetsBroken": 5,
            "HasCabinetHinges": 4,
            "HasCabinetAlignment": 3,

            # Flooring Issues
            "HasUnevenFlooring": 6,
            "HasCarpet": 4,
            "HasTiles": 3,
            "HasNailsStickingOut": 7,
            "HasFlooringIssues": 8,                 # Aggregate

            # Window Issues
            "HasBrokenWindows": 10,
            "HasWindowScreens": 4,
            "HasWindowLeaks": 8,
            "HasWindowsDoNotLock": 6,
            "HasMissingWindows": 7,
            "HasBrokenMissingScreens": 5,
            "HasWindowsIssues": 9,                # Aggregate

            # Door Issues
            "HasBrokenDoors": 17,           # Door issues
            "HasDoorKnobs": 4,
            "HasDoorLocks": 6,
            "HasBrokenHinges": 5,
            "HasSlidingGlassDoors": 4,
            "HasIneffectiveWaterproofing": 6,
            "HasWaterIntrusionInsects": 8,
            "HasDoorsDoNotCloseProperly": 7,
            "HasDoorIssues": 10,                  # Aggregate

            # Structure Issues
            "HasHoleInCeiling": 8,
            "HasBumpsInCeiling": 5,
            "HasWaterStainsOnCeiling": 7,
            "HasWaterStainsOnWall": 6,
            "HasHoleInWall": 7,
            "HasPaint": 4,
            "HasExteriorDeckPorch": 5,
            "HasWaterproofToilet": 3,
            "HasWaterproofTub": 3,
            "HasStaircase": 4,
            "HasBasementFlood": 8,
            "HasLeaksInGarage": 6,
            "HasIneffectiveWeatherproofingOfAnyWindowsDoors": 9,
            "HasIneffectiveWaterproofingOfTheTubsToilet": 7,
            "HasSoftSpotsDueToLeaks": 8,
            "HasHolesInCeilingWalls": 9,    # Aggregate
            "HasWaterStainsOnCeilingWalls": 8, # Aggregate
            "HasStructureIssues": 12,              # Aggregate

            # Common Area Issues
            "HasMailboxBroken": 3,
            "HasParkingAreaIssues": 4,
            "HasDamageToCars": 5,
            "HasFlooding": 8,
            "HasEntrancesBlocked": 6,
            "HasSwimmingPool": 3,
            "HasJacuzzi": 2,
            "HasLaundryRoom": 4,
            "HasRecreationRoom": 3,
            "HasGym": 2,
            "HasBlockedAreasDoors": 5,
            "HasElevator": 18,              # Elevator issues
            "HasFilthRubbishGarbage": 6,
            "HasCommonAreaVermin": 7,
            "HasBrokenGate": 4,
            "HasCommonAreaInsects": 5,
            "HasCommonAreasIssues": 10,            # Aggregate

            # Nuisance Issues
            "HasDrugs": 8,
            "HasSmoking": 6,
            "HasNoisyNeighbors": 7,
            "HasGangs": 9,
            "HasNuisanceIssues": 8,               # Aggregate

            # Health Hazards
            "HasMold": 24,                  # Mold investigation
            "HasMildew": 8,
            "HasMushrooms": 6,
            "HasRawSewageOnExterior": 12,
            "HasNoxiousFumes": 9,
            "HasChemicalsPaintContamination": 10,
            "HasToxicWaterPollution": 11,
            "HasOffensiveOdors": 7,
            "HasHealthHazardIssues": 15,         # Aggregate

            # Harassment Issues
            "HasUnlawfulDetainer": 12,
            "HasEvictionThreat": 10,
            "HasHarrassmentByDefendants": 14,
            "HasHarrassmentMaintenanceManWorkers": 12,
            "HasHarrassmentManagerStaff": 13,
            "HasHarrassmentByOwnerAndTheirGuests": 15,
            "HasHarrassmentOtherTenants": 11,
            "HasIllegitimateNotices": 9,
            "HasRefusalToMakeTimelyRepairs": 11,
            "HasWrittenThreats": 8,
            "HasAggressiveInappropriateLanguage": 9,
            "HasPhysicalThreatsOrTouching": 12,
            "HasNoticesSinglingOutOneTenant": 8,
            "HasDuplicativeNotices": 6,
            "HasUntimelyResponseFromLandlord": 7,
            "HasHarassmentIssues": 16,            # Aggregate

            # Notice Issues
            "HasNotices": 8,
            "Has24HourNotices": 6,
            "Has3DayNotices": 7,
            "Has30DayNotices": 5,
            "Has60DayNotices": 4,
            "HasToQuitNotices": 6,
            "HasPerformOrQuit": 5,

            # Utility Issues
            "HasWaterShutoffs": 8,
            "HasGasLeaks": 10,
            "HasElectricityShutoffs": 9,
            "HasHeatShutoffs": 7,
            "HasGasShutoffs": 6,

            # Safety Issues
            "HasSafety": 6,
            "HasInoperableLocks": 14,
            "HasBrokenSecurityGate": 5,
            "HasSecurityCameras": 3,
            "HasBrokenBuzzerToGetIn": 4,

            # Miscellaneous Issues
            "HasInjury": 8,
            "HasNonresponsiveLandlord": 7,
            "HasUnauthorizedEntries": 9,
            "HasStolenItems": 6,
            "HasDamagedItems": 5,

            # Discrimination Issues
            "HasAgeDiscrimination": 8,
            "HasDisabilityDiscrimination": 9,
            "HasRacialDiscrimination": 10,
            "HasSecurityDeposit": 20,       # Security deposit disputes

            # Trash Issues
            "HasTrashProblems": 6,
            "HasInadequateNumberOfTrashReceptacles": 4,
            "HasInadequateServicingAndEmptyingTrashReceptacles": 5,

            # City Issues
            "HasLosAngeles": 1,             # LA-specific (not Set 1 only for SROGs)
        }

    def add_profile_specific_flags(self, dataset: dict) -> dict:
        """Add SROGs-specific flags."""
        flags = dataset['flags']

        # Always add SROGsGeneral
        flags['SROGsGeneral'] = True

        # Add defendant role flags
        defendant_role = dataset.get('defendant', {}).get('role', '')
        flags['IsOwner'] = defendant_role.lower() == 'owner'
        flags['IsManager'] = defendant_role.lower() == 'manager'

        return dataset
