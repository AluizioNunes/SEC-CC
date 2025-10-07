"""
Test Business Intelligence Services
"""
import asyncio
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .business_intelligence import business_intelligence_service
from .analytics_service import ultra_analytics_service


async def test_business_intelligence_services():
    """Test business intelligence services"""
    print("Testing Business Intelligence Services...")
    
    # Initialize services
    print("Initializing business intelligence services...")
    initialized = await business_intelligence_service.initialize_services()
    print(f"Services initialized: {initialized}")
    
    # Register default business metrics
    print("Registering default business metrics...")
    metrics_registered = await business_intelligence_service.register_default_business_metrics()
    print(f"Metrics registered: {metrics_registered}")
    
    # Get business intelligence status
    print("Getting business intelligence status...")
    status = await business_intelligence_service.get_business_intelligence_status()
    print(f"BI Status: {status}")
    
    # Get comprehensive business intelligence
    print("Getting comprehensive business intelligence...")
    bi_data = await business_intelligence_service.get_comprehensive_business_intelligence()
    print(f"BI Data keys: {bi_data.keys()}")
    
    print("Business Intelligence Services test completed!")


if __name__ == "__main__":
    asyncio.run(test_business_intelligence_services())