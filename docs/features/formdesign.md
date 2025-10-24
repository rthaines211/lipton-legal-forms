# 📝 Auto-Population Form
Design Style:

Modern, geometric approach with clean lines

Professional and corporate aesthetic
---

## 1. Address of the Property
- **What is the property address (Line 1)?** *(Short text)*
- **Apartment/Unit # (Line 2), if any?** *(Short text)*
- **City?** *(Short text)*
- **State?** *(Dropdown — list of U.S. states)*
- **ZIP Code?** *(Short text — numeric)*
- **In which city will this case be filed (Filing City)?** *(Short text)*
- **In which county will this case be filed (Filing County)?** *(Short text)*

---

## 2. Plaintiff Details  
*(Repeatable section. Add with button: ➡️ **“Add Plaintiff”**)*
Each plaintiff block renders as an accessible accordion with its header button syncing aria-expanded and the associated category checkbox. A section-level “Collapse All” control expands or collapses every plaintiff panel.

### Basic Information (always shown)
- **Plaintiff’s first name?** *(Short text)*
- **Plaintiff’s last name?** *(Short text)*
- **Is the plaintiff an Individual or a Guardian?** *(Dropdown — Individual, Guardian)*
- **What is the plaintiff’s age category?** *(Radio button — Adult, Child)*
- **Is this plaintiff the Head of Household?** *(Yes/No toggle)*

---

### 🔒 Conditional Logic:  
**The following fields ONLY appear if “Head of Household = Yes.”**

#### Unit
- **What is the plaintiff’s unit number (if any)?** *(Short text)*

#### Issue Categories  
*(All categories are Yes/No toggles driven by accessible accordion headers. If **Yes**, show sub-options as checkboxes. If **No**, keep the panel collapsed.)*

##### Vermin Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Rats/Mice, Bats, Pigeons, Skunks, Raccoons, Opossums  

##### Insect Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Ants, Bedbugs, Spiders, Mosquitos, Roaches, Wasps, Termites, Bees, Flies, Hornets  

##### HVAC Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Air Conditioner, Heater, Ventilation  

##### Electrical Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Outlets, Wall Switches, Interior Lighting, Fans, Panel, Exterior Lighting, Light Fixtures  

##### Fire Hazard Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Smoke Alarms, Non-compliant electricity, Carbon monoxide detectors, Fire Extinguisher, Non-GFI outlets near water  

##### Government Entity Contacted *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Health Department, Police Department, Housing Authority, Dept. of Environmental Health, Code Enforcement, Dept. of Health Services, Fire Department  

##### Appliances Issues *(Yes/No toggle only)*  

##### Plumbing Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Toilet, Insufficient water pressure, Clogged bath, Clogged shower, Clogged sink, Clogged toilet, No hot water, No cold water, Sewage coming out, No clean water supply, Unsanitary water  

##### Cabinets Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Broken Hinges, Alignment  

##### Flooring Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Uneven, Carpet, Nails sticking out, Tiles  

##### Windows Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Broken, Leaks, Missing windows, Screens, Do not lock, Broken or missing screens  

##### Door Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Broken, Broken hinges, Water intrusion/insects, Knobs, Sliding glass doors, Do not close properly, Locks, Ineffective waterproofing  

##### Structure Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Bumps in ceiling, Hole in ceiling, Water stains on ceiling, Water stains on wall, Hole in wall, Basement flood, Exterior deck/porch, Leaks in garage, Soft spots due to leaks, Waterproof toilet, Waterproof tub, Ineffective weatherproofing (toilets, tubs, windows, doors), Staircase  

##### Common Areas Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Mailbox broken, Parking area issues, Damage to cars, Flooding, Entrances blocked, Swimming pool, Jacuzzi, Laundry room, Recreation room, Gym, Broken Gate, Elevator, Blocked areas/doors, Filth, Rubbish, Garbage, Vermin, Insects  

##### Trash Problems *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Inadequate number of receptacles, Improper servicing/emptying  

##### Nuisance Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Drugs, Smoking, Noisy neighbors, Gangs  

##### Health Hazard Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Mold, Mildew, Mushrooms, Noxious fumes, Toxic water pollution, Raw sewage on exterior, Chemical/paint contamination, Offensive odors  

##### Harassment Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* By manager/building staff (unlawful detainer, refusal to repair), By owner (eviction threats, written threats, duplicative notices), By tenants (aggressive language, physical threats), By maintenance staff (inappropriate behavior, untimely response), Notices singling out one tenant, Illegitimate notices  

##### Notices Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* 3-day, 24-hour, 30-day, 60-day, To quit, Perform or quit  

##### Utility Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Gas leak, Gas shutoff, Electricity shutoffs, Water shutoffs, Heat shutoff  

##### Safety Issues *(Yes/No toggle)*
- If Yes → *(Checkbox list)* Broken/inoperable security gate, Unauthorized entries, Security cameras, Broken doors, Broken buzzer to get in, Inoperable locks  

##### Direct Toggles *(Yes/No only — no sub-list)*
- Injury Issues  
- Nonresponsive Landlord Issues  
- Unauthorized Entries  
- Stolen Items  
- Disability Discrimination  
- Damaged Items  
- Age Discrimination  
- Racial Discrimination  
- Security Deposit Issues  

---

## 3. Defendant Details  
*(Repeatable section. Add with button: ➡️ **“Add Defendant”**)*

- **Defendant’s first name?** *(Short text)*
- **Defendant’s last name?** *(Short text)*
- **What is the defendant’s entity type?** *(Dropdown — e.g., California LLC, California Corporation, California Limited Partnership)*
- **Is this person the Manager or the Owner?** *(Radio button — Manager, Owner)*
