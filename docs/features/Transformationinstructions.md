# Additional Boolean & Flag Generators

These functions take normalized discovery inputs and create boolean flags that power the interrogatory counts.

---

## Plumbing
- **Reads:** `Plumbing` (multi-select)
- **Sets:**
  - `HasToilet`, `HasShower`, `HasBath`, `HasFixtures`, `HasLeaks`
  - `HasInsufficientWaterPressure`, `HasNoHotWater`, `HasSewageComingOut`
  - `HasCloggedToilet`, `HasCloggedBath`, `HasCloggedSink`, `HasCloggedShower`
  - `HasNoCleanWaterSupply`, `HasNoColdWater`, `HasUnsanitaryWater`
- **Aggregates:**  
  - `HasPlumbing` → true if any plumbing issue selected  
  - `HasClogs` → true if any clog flag is true

---

## Cabinets
- **Reads:** `Cabinets Issues` (Yes/No), `Cabinets` (multi-select)
- **Sets:**
  - `HasCabinets` (Yes/No)
  - `HasCabinetsBroken`, `HasCabinetHinges`, `HasCabinetAlignment`

---

## Flooring
- **Reads:** `Flooring` (multi-select)
- **Sets:**
  - `HasUnevenFlooring`, `HasCarpet`, `HasTiles`, `HasNailsStickingOut`
- **Aggregate:** `HasFloors`

---

## Windows
- **Reads:** `Windows` (multi-select)
- **Sets:**
  - `HasBrokenWindows`, `HasWindowScreens`, `HasWindowLeaks`
  - `HasWindowsDoNotLock`, `HasMissingWindows`, `HasBrokenMissingScreens`
- **Aggregate:** `HasWindows`

---

## Doors
- **Reads:** `Doors` (multi-select)
- **Sets:**
  - `HasBrokenDoors`, `HasDoorKnobs`, `HasDoorLocks`, `HasBrokenHinges`
  - `HasSlidingGlassDoors`, `HasIneffectiveWaterproofing`
  - `HasWaterIntrusionInsects`, `HasDoorsDoNotCloseProperly`
- **Aggregate:** `HasDoors`

---

## Structure
- **Reads:** `Structure` (multi-select)
- **Sets:**
  - `HasHoleInCeiling`, `HasBumpsInCeiling`, `HasWaterStainsOnCeiling`
  - `HasWaterStainsOnWall`, `HasHoleInWall`, `HasPaint`
  - `HasExteriorDeckPorch`, `HasWaterproofToilet`, `HasWaterproofTub`
  - `HasStaircase`, `HasBasementFlood`, `HasLeaksInGarage`
  - `HasIneffectiveWeatherproofingOfAnyWindowsDoors`
  - `HasIneffectiveWaterproofingOfTheTubsToilet`
  - `HasSoftSpotsDueToLeaks`
- **Aggregates:**
  - `HasHolesInCeilingWalls`
  - `HasWaterStainsOnCeilingWalls`
  - `HasStructure`

---

## Common Areas
- **Reads:** `Common areas` (multi-select)
- **Sets:**
  - `HasMailboxBroken`, `HasParkingAreaIssues`, `HasDamageToCars`
  - `HasFlooding`, `HasEntrancesBlocked`, `HasSwimmingPool`, `HasJacuzzi`
  - `HasLaundryRoom`, `HasRecreationRoom`, `HasGym`, `HasBlockedAreasDoors`
  - `HasElevator`, `HasFilthRubbishGarbage`, `HasCommonAreaVermin`
  - `HasBrokenGate`, `HasCommonAreaInsects`
- **Aggregate:** `HasCommonArea`

---

## Nuisance
- **Reads:** `Nuisance` (multi-select)
- **Sets:**
  - `HasDrugs`, `HasSmoking`, `HasNoisyNeighbors`, `HasGangs`
- **Aggregate:** `HasNuisance`

---

## Health Hazards
- **Reads:** `Health hazard` (multi-select)
- **Sets:**
  - `HasMold`, `HasMildew`, `HasMushrooms`, `HasRawSewageOnExterior`
  - `HasNoxiousFumes`, `HasChemicalsPaintContamination`
  - `HasToxicWaterPollution`, `HasOffensiveOdors`
- **Aggregate:** `HasHealthHazards`

---

## Harassment
- **Reads:** `Harassment` (multi-select)
- **Sets:**
  - `HasUnlawfulDetainer`, `HasEvictionThreat`
  - `HasHarrassmentByDefendants`, `HasHarrassmentMaintenanceManWorkers`
  - `HasHarrassmentManagerStaff`, `HasHarrassmentByOwnerAndTheirGuests`
  - `HasHarrassmentOtherTenants`, `HasIllegitimateNotices`
  - `HasRefusalToMakeTimelyRepairs`, `HasWrittenThreats`
  - `HasAggressiveInappropriateLanguage`, `HasPhysicalThreatsOrTouching`
  - `HasNoticesSinglingOutOneTenant`, `HasDuplicativeNotices`
  - `HasUntimelyResponseFromLandlord`
- **Aggregate:** `HasHarassment`

---

## Notices
- **Reads:**  
  - `Notices Issues` (Yes/No)  
  - `Select Notices Issues:` (multi-select)
- **Sets:**
  - `HasNotices`
  - `Has24HourNotices`, `Has3DayNotices`, `Has30DayNotices`
  - `Has60DayNotices`, `HasToQuitNotices`, `HasPerformOrQuit`

---

## Safety
- **Reads:**  
  - `Safety` (Yes/No)  
  - `Select Safety Issues:` (multi-select)
- **Sets:**
  - `HasSafety`
  - `HasInoperableLocks`, `HasBrokenSecurityGate`
  - `HasSecurityCameras`, `HasBrokenBuzzerToGetIn`

---

## Discrimination & Deposits
- **Reads:**  
  - `Age discrimination`, `Disability discrimination`  
  - `Racial Discrimination`, `Security Deposit`
- **Sets:**
  - `HasAgeDiscrimination`, `HasDisabilityDiscrimination`
  - `HasRacialDiscrimination`, `HasSecurityDeposit`

---

## Appliances (bonus)
- **Reads:** `Appliances` (multi-select)
- **Sets:**
  - `HasStove`, `HasDishwasher`, `HasWasherDryer`
  - `HasOven`, `HasMicrowave`, `HasGarbageDisposal`
  - `HasRefrigerator`
- **Aggregate:** `HasAppliances`
