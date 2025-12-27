from typing import Any, Dict, List, Optional
from data_sdk.ingestion import DataIngestor
from data_sdk.transformation import DataTransformer
from data_sdk.enrichment import DataEnricher
from data_sdk.export import DataExporter

class DataSDK:
    def __init__(self):
        self.ingestor = DataIngestor()
        self.transformer = DataTransformer()
        self.enricher = DataEnricher()
        self.exporter = DataExporter()

    async def process_pipeline(
        self, 
        source_data: Any, 
        pipeline_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        raw_data = await self.ingestor.ingest(source_data, pipeline_config.get("ingestion"))
        
        transformed_data = await self.transformer.transform(
            raw_data, 
            pipeline_config.get("transformation")
        )
        
        enriched_data = await self.enricher.enrich(
            transformed_data, 
            pipeline_config.get("enrichment")
        )
        
        return enriched_data

    async def ship_data(self, data: Any, destination: str, config: Dict[str, Any]):
        return await self.exporter.export(data, destination, config)

data_sdk = DataSDK()

__all__ = [
    "data_sdk",
    "DataIngestor",
    "DataTransformer",
    "DataEnricher",
    "DataExporter"
]