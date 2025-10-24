#!/usr/bin/env python3
"""
Phase 4: Document Profiles Example

This example demonstrates how to use the Phase 4 document profile system
to create three different document types (SROGs, PODs, Admissions) from
a single enriched dataset.
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from phase4 import ProfilePipeline, SROGsProfile, PODsProfile, AdmissionsProfile


def create_sample_dataset():
    """Create a sample enriched dataset for demonstration."""
    return {
        'dataset_id': 'demo-case-001',
        'plaintiff': {
            'name': 'Maria Rodriguez',
            'address': '123 Oak Street, Los Angeles, CA 90210',
            'phone': '(323) 555-0123',
            'email': 'maria.rodriguez@email.com'
        },
        'defendant': {
            'name': 'Sunset Property Management LLC',
            'role': 'Manager',
            'address': '456 Business Plaza, Los Angeles, CA 90210',
            'phone': '(323) 555-0456',
            'email': 'contact@sunsetproperty.com'
        },
        'case_metadata': {
            'case_number': 'BC2024001234',
            'filing_city': 'Los Angeles',
            'filing_date': '2024-01-15',
            'court_name': 'Los Angeles Superior Court'
        },
        'flags': {
            # Environmental issues
            'HasMold': True,
            'HasLeadPaint': True,
            'HasWaterDamage': True,
            
            # Vermin issues
            'HasRatsMice': True,
            'HasBedbugs': False,
            'HasRoaches': True,
            
            # Housing issues
            'HasPlumbingIssues': True,
            'HasElectricalIssues': True,
            'HasHVACIssues': False,
            
            # Safety issues
            'HasInoperableLocks': True,
            'HasSmokeDetectorIssues': True,
            'HasFireHazards': False,
            
            # Legal issues
            'HasRetaliation': True,
            'HasDiscrimination': False,
            'HasHarassment': True,
            
            # Maintenance issues
            'HasTrashIssues': True,
            'HasPestControlIssues': True,
            'HasLandscapingIssues': False,
            
            # Utility issues
            'HasWaterIssues': True,
            'HasGasIssues': False,
            'HasElectricIssues': True,
            
            # Appliance issues
            'HasRefrigeratorIssues': True,
            'HasStoveIssues': False,
            'HasDishwasherIssues': True,
            
            # Structural issues
            'HasWindowIssues': True,
            'HasDoorIssues': True,
            'HasCabinetIssues': False,
            
            # Common area issues
            'HasHallwayIssues': True,
            'HasStairwayIssues': False,
            'HasElevatorIssues': True,
            
            # Government issues
            'HasCodeViolations': True,
            'HasPermitIssues': False,
            'HasInspectionIssues': True,
            
            # Notice issues
            'HasNoticeIssues': True,
            'HasRentIncreaseIssues': False,
            'HasLeaseIssues': True,
            
            # Nuisance issues
            'HasNuisanceIssues': True,
            'HasQuietEnjoymentIssues': False,
            'HasHabitabilityIssues': True
        }
    }


def demonstrate_individual_profiles():
    """Demonstrate individual profile usage."""
    print("=" * 60)
    print("INDIVIDUAL PROFILE DEMONSTRATION")
    print("=" * 60)
    
    dataset = create_sample_dataset()
    
    # Create individual profiles
    srogs_profile = SROGsProfile()
    pods_profile = PODsProfile()
    admissions_profile = AdmissionsProfile()
    
    # Apply each profile
    srogs_result = srogs_profile.apply_profile(dataset)
    pods_result = pods_profile.apply_profile(dataset)
    admissions_result = admissions_profile.apply_profile(dataset)
    
    print(f"\n1. SROGs Profile:")
    print(f"   Document Type: {srogs_result['doc_type']}")
    print(f"   Template: {srogs_result['template']}")
    print(f"   Filename Suffix: {srogs_result['filename_suffix']}")
    print(f"   Dataset ID: {srogs_result['dataset_id']}")
    print(f"   First Set Only Flags: {srogs_result['first_set_only_flags']}")
    print(f"   SROGsGeneral Flag: {srogs_result['flags'].get('SROGsGeneral', 'Not present')}")
    print(f"   IsOwner Flag: {srogs_result['flags'].get('IsOwner', 'Not present')}")
    print(f"   IsManager Flag: {srogs_result['flags'].get('IsManager', 'Not present')}")
    print(f"   Sample Interrogatory Counts:")
    for flag in ['HasMold', 'HasRatsMice', 'HasPlumbingIssues', 'HasRetaliation']:
        if flag in srogs_result['interrogatory_counts']:
            print(f"     {flag}: {srogs_result['interrogatory_counts'][flag]}")
    
    print(f"\n2. PODs Profile:")
    print(f"   Document Type: {pods_result['doc_type']}")
    print(f"   Template: {pods_result['template']}")
    print(f"   Filename Suffix: {pods_result['filename_suffix']}")
    print(f"   Dataset ID: {pods_result['dataset_id']}")
    print(f"   First Set Only Flags: {pods_result['first_set_only_flags']}")
    print(f"   SROGsGeneral Flag: {pods_result['flags'].get('SROGsGeneral', 'Not present')}")
    print(f"   IsOwnerManager Flag: {pods_result['flags'].get('IsOwnerManager', 'Not present')}")
    print(f"   Sample Interrogatory Counts:")
    for flag in ['HasMold', 'HasRatsMice', 'HasPlumbingIssues', 'HasRetaliation']:
        if flag in pods_result['interrogatory_counts']:
            print(f"     {flag}: {pods_result['interrogatory_counts'][flag]}")
    
    print(f"\n3. Admissions Profile:")
    print(f"   Document Type: {admissions_result['doc_type']}")
    print(f"   Template: {admissions_result['template']}")
    print(f"   Filename Suffix: {admissions_result['filename_suffix']}")
    print(f"   Dataset ID: {admissions_result['dataset_id']}")
    print(f"   First Set Only Flags: {admissions_result['first_set_only_flags']}")
    print(f"   AdmissionsGeneral Flag: {admissions_result['flags'].get('AdmissionsGeneral', 'Not present')}")
    print(f"   HasLosAngeles Flag: {admissions_result['flags'].get('HasLosAngeles', 'Not present')}")
    print(f"   Sample Interrogatory Counts:")
    for flag in ['HasMold', 'HasRatsMice', 'HasPlumbingIssues', 'HasRetaliation']:
        if flag in admissions_result['interrogatory_counts']:
            print(f"     {flag}: {admissions_result['interrogatory_counts'][flag]}")


def demonstrate_profile_pipeline():
    """Demonstrate the profile pipeline usage."""
    print("\n" + "=" * 60)
    print("PROFILE PIPELINE DEMONSTRATION")
    print("=" * 60)
    
    dataset = create_sample_dataset()
    pipeline = ProfilePipeline()
    
    # Apply all profiles at once
    result = pipeline.apply_profiles(dataset)
    
    print(f"\nApplied all three profiles to dataset: {dataset['dataset_id']}")
    print(f"Generated {len(result)} profile datasets:")
    
    for profile_name, profile_data in result.items():
        print(f"\n{profile_name.upper()} Profile:")
        print(f"  Document Type: {profile_data['doc_type']}")
        print(f"  Template: {profile_data['template']}")
        print(f"  Dataset ID: {profile_data['dataset_id']}")
        print(f"  Total Flags: {len(profile_data['flags'])}")
        print(f"  Interrogatory Mappings: {len(profile_data['interrogatory_counts'])}")
        
        # Show some key flags
        key_flags = ['SROGsGeneral', 'AdmissionsGeneral', 'IsOwnerManager', 'HasLosAngeles']
        present_flags = [flag for flag in key_flags if flag in profile_data['flags']]
        if present_flags:
            print(f"  Key Flags: {present_flags}")


def demonstrate_collection_processing():
    """Demonstrate processing a collection of datasets."""
    print("\n" + "=" * 60)
    print("COLLECTION PROCESSING DEMONSTRATION")
    print("=" * 60)
    
    # Create a collection of datasets
    collection = {
        'datasets': [
            create_sample_dataset(),
            {
                **create_sample_dataset(),
                'dataset_id': 'demo-case-002',
                'defendant': {'name': 'Property Owner LLC', 'role': 'Owner'},
                'case_metadata': {'filing_city': 'San Francisco'}
            },
            {
                **create_sample_dataset(),
                'dataset_id': 'demo-case-003',
                'defendant': {'name': 'Management Corp', 'role': 'Manager'},
                'case_metadata': {'filing_city': 'Oakland'}
            }
        ],
        'metadata': {
            'total_datasets': 3,
            'created_at': '2024-01-15T10:00:00Z',
            'phase': 3
        }
    }
    
    pipeline = ProfilePipeline()
    result = pipeline.apply_profiles_to_collection(collection)
    
    print(f"\nProcessed collection with {len(collection['datasets'])} datasets")
    print(f"Generated {result['metadata']['total_profile_datasets']} total profile datasets")
    print(f"Profiles applied: {result['metadata']['profiles_applied']}")
    
    # Show results for each dataset
    for i, dataset in enumerate(result['datasets']):
        print(f"\nDataset {i+1}:")
        for profile_name, profile_data in dataset.items():
            print(f"  {profile_name.upper()}: {profile_data['dataset_id']} ({profile_data['doc_type']})")


def demonstrate_profile_info():
    """Demonstrate getting profile information."""
    print("\n" + "=" * 60)
    print("PROFILE INFORMATION DEMONSTRATION")
    print("=" * 60)
    
    pipeline = ProfilePipeline()
    info = pipeline.get_profile_info()
    
    for profile_name, profile_info in info.items():
        print(f"\n{profile_name.upper()} Profile Info:")
        print(f"  Document Type: {profile_info['doc_type']}")
        print(f"  Template: {profile_info['template']}")
        print(f"  Filename Suffix: {profile_info['filename_suffix']}")
        print(f"  First Set Only Flags: {profile_info['first_set_only_flags']}")
        print(f"  Total Interrogatory Mappings: {profile_info['total_interrogatory_mappings']}")


def demonstrate_validation():
    """Demonstrate profile validation."""
    print("\n" + "=" * 60)
    print("PROFILE VALIDATION DEMONSTRATION")
    print("=" * 60)
    
    pipeline = ProfilePipeline()
    dataset = create_sample_dataset()
    result = pipeline.apply_profiles(dataset)
    
    # Validate the profiles
    validation_results = pipeline.validate_profile_datasets(result)
    
    print(f"\nValidation Results:")
    for profile_name, missing_fields in validation_results.items():
        if missing_fields:
            print(f"  {profile_name}: Missing fields: {missing_fields}")
        else:
            print(f"  {profile_name}: ✅ All required fields present")


def demonstrate_interrogatory_count_comparison():
    """Demonstrate interrogatory count differences between profiles."""
    print("\n" + "=" * 60)
    print("INTERROGATORY COUNT COMPARISON")
    print("=" * 60)
    
    pipeline = ProfilePipeline()
    dataset = create_sample_dataset()
    result = pipeline.apply_profiles(dataset)
    
    # Compare counts for key flags
    key_flags = ['HasMold', 'HasRatsMice', 'HasPlumbingIssues', 'HasRetaliation', 'HasDiscrimination']
    
    print(f"\nInterrogatory Count Comparison:")
    print(f"{'Flag':<20} {'SROGs':<8} {'PODs':<8} {'Admissions':<12}")
    print("-" * 50)
    
    for flag in key_flags:
        srogs_count = result['srogs']['interrogatory_counts'].get(flag, 'N/A')
        pods_count = result['pods']['interrogatory_counts'].get(flag, 'N/A')
        admissions_count = result['admissions']['interrogatory_counts'].get(flag, 'N/A')
        
        print(f"{flag:<20} {srogs_count:<8} {pods_count:<8} {admissions_count:<12}")


def main():
    """Run all demonstrations."""
    print("PHASE 4: DOCUMENT PROFILES DEMONSTRATION")
    print("This example shows how to create three different document types")
    print("(SROGs, PODs, Admissions) from a single enriched dataset.")
    
    try:
        demonstrate_individual_profiles()
        demonstrate_profile_pipeline()
        demonstrate_collection_processing()
        demonstrate_profile_info()
        demonstrate_validation()
        demonstrate_interrogatory_count_comparison()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("All Phase 4 functionality demonstrated successfully!")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
