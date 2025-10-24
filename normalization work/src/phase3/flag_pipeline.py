"""
Flag Processor Pipeline for Phase 3: Flag Processors

This module orchestrates all flag processors to transform discovery data
into 180+ individual boolean flags.
"""

from typing import List, Dict, Any
from .base_processor import BaseFlagProcessor
from .processors.vermin import VerminProcessor
from .processors.insects import InsectProcessor
from .processors.plumbing import PlumbingProcessor
from .processors.hvac import HVACProcessor
from .processors.electrical import ElectricalProcessor
from .processors.fire_hazard import FireHazardProcessor
from .processors.government import GovernmentProcessor
from .processors.appliances import AppliancesProcessor
from .processors.cabinets import CabinetsProcessor
from .processors.flooring import FlooringProcessor
from .processors.windows import WindowsProcessor
from .processors.doors import DoorsProcessor
from .processors.structure import StructureProcessor
from .processors.common_areas import CommonAreasProcessor
from .processors.trash import TrashProcessor
from .processors.nuisance import NuisanceProcessor
from .processors.health_hazard import HealthHazardProcessor
from .processors.harassment import HarassmentProcessor
from .processors.notices import NoticesProcessor
from .processors.utility import UtilityProcessor
from .processors.safety import SafetyProcessor
from .processors.discrimination import DiscriminationProcessor
from .processors.defendant_role import DefendantRoleProcessor
from .processors.geography import GeographyProcessor
from .processors.direct_boolean import DirectBooleanProcessor


class FlagProcessorPipeline:
    """
    Orchestrates all flag processors to transform discovery data into flags.
    
    This pipeline processes datasets through all flag processors to generate
    180+ individual boolean flags from discovery arrays and boolean fields.
    """

    def __init__(self):
        """Initialize the pipeline with all processors."""
        self.processors = self._initialize_processors()

    def _initialize_processors(self) -> List[BaseFlagProcessor]:
        """
        Initialize all processors in processing order.
        
        Returns:
            List of all flag processors
        """
        return [
            VerminProcessor(),
            InsectProcessor(),
            HVACProcessor(),
            ElectricalProcessor(),
            FireHazardProcessor(),
            GovernmentProcessor(),
            AppliancesProcessor(),
            PlumbingProcessor(),
            CabinetsProcessor(),
            FlooringProcessor(),
            WindowsProcessor(),
            DoorsProcessor(),
            StructureProcessor(),
            CommonAreasProcessor(),
            TrashProcessor(),
            NuisanceProcessor(),
            HealthHazardProcessor(),
            HarassmentProcessor(),
            NoticesProcessor(),
            UtilityProcessor(),
            SafetyProcessor(),
            DiscriminationProcessor(),
            DefendantRoleProcessor(),
            GeographyProcessor(),
            DirectBooleanProcessor()
        ]

    def process_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single dataset through all flag processors.
        
        Args:
            dataset: Dataset from Phase 2
            
        Returns:
            Dataset enriched with 180+ flags
            
        Example:
            >>> pipeline = FlagProcessorPipeline()
            >>> dataset = {
            ...     "dataset_id": "test",
            ...     "discovery_data": {
            ...         "vermin": ["Rats/Mice", "Bedbugs"],
            ...         "has_injury": True
            ...     }
            ... }
            >>> result = pipeline.process_dataset(dataset)
            >>> result["flags"]["HasRatsMice"]
            True
            >>> result["flags"]["HasInjury"]
            True
        """
        flags = {}
        discovery_data = dataset.get('discovery_data', {})

        # Run each processor
        for processor in self.processors:
            try:
                # Some processors need the full dataset, others just discovery_data
                if isinstance(processor, (DefendantRoleProcessor, GeographyProcessor)):
                    processor_flags = processor.process(dataset)
                else:
                    processor_flags = processor.process(discovery_data)
                flags.update(processor_flags)
            except Exception as e:
                # Log error but continue processing
                print(f"Warning: Error in {processor.__class__.__name__}: {e}")
                continue

        # Add flags to dataset
        enriched_dataset = dataset.copy()
        enriched_dataset['flags'] = flags

        return enriched_dataset

    def process_all_datasets(self, dataset_collection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all datasets in collection.
        
        Args:
            dataset_collection: Output from Phase 2
            
        Returns:
            Collection with all datasets enriched with flags
            
        Example:
            >>> pipeline = FlagProcessorPipeline()
            >>> collection = {
            ...     "datasets": [dataset1, dataset2],
            ...     "metadata": {"total_datasets": 2}
            ... }
            >>> result = pipeline.process_all_datasets(collection)
            >>> len(result["datasets"])
            2
            >>> "flags" in result["datasets"][0]
            True
        """
        enriched_datasets = []

        for dataset in dataset_collection.get('datasets', []):
            enriched = self.process_dataset(dataset)
            enriched_datasets.append(enriched)

        # Calculate flag statistics
        total_flags = len(enriched_datasets[0]['flags']) if enriched_datasets else 0
        
        return {
            'datasets': enriched_datasets,
            'metadata': {
                **dataset_collection.get('metadata', {}),
                'flags_generated': total_flags,
                'processors_used': len(self.processors)
            }
        }

    def get_processor_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all processors.
        
        Returns:
            List of processor information dictionaries
        """
        return [processor.get_processor_info() for processor in self.processors]

    def get_total_expected_flags(self) -> int:
        """
        Get total number of expected flags across all processors.
        
        Returns:
            Total number of expected flags
        """
        total = 0
        for processor in self.processors:
            total += len(processor.get_expected_flags())
        return total

    def validate_pipeline(self) -> Dict[str, Any]:
        """
        Validate that the pipeline is properly configured.
        
        Returns:
            Validation results dictionary
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "total_processors": len(self.processors),
            "total_expected_flags": self.get_total_expected_flags()
        }

        # Check for duplicate flag names
        all_flags = []
        for processor in self.processors:
            all_flags.extend(processor.get_expected_flags())
        
        duplicate_flags = [flag for flag in set(all_flags) if all_flags.count(flag) > 1]
        if duplicate_flags:
            results["valid"] = False
            results["errors"].append(f"Duplicate flag names: {duplicate_flags}")

        # Check for processors with no flags
        for processor in self.processors:
            if len(processor.get_expected_flags()) == 0:
                results["warnings"].append(f"{processor.__class__.__name__} has no flags")

        return results
