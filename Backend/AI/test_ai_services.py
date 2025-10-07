"""
Test AI Services
"""
import asyncio
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .nlp.advanced_nlp import advanced_nlp_service, NLPAnalysisRequest, NLPAnalysisType
from .multimedia.content_generation import multimedia_content_service, ContentGenerationRequest, ContentGenerationType, MediaType
from .analysis.sentiment_behavior import sentiment_behavior_service, AnalysisRequest, AnalysisType


async def test_ai_services():
    """Test AI services"""
    print("Testing AI Services...")
    
    # Test NLP service
    print("Testing NLP Service...")
    nlp_request = NLPAnalysisRequest(
        text="I love this product! It's amazing and works perfectly.",
        analysis_type=NLPAnalysisType.SENTIMENT
    )
    nlp_result = await advanced_nlp_service.analyze_text(nlp_request)
    print(f"NLP Result: {nlp_result}")
    
    # Test Multimedia service
    print("Testing Multimedia Service...")
    multimedia_request = ContentGenerationRequest(
        generation_type=ContentGenerationType.TEXT_TO_IMAGE,
        prompt="A beautiful sunset over the mountains",
        media_type=MediaType.IMAGE
    )
    multimedia_result = await multimedia_content_service.generate_content(multimedia_request)
    print(f"Multimedia Result: {multimedia_result}")
    
    # Test Sentiment/Behavior service
    print("Testing Sentiment/Behavior Service...")
    behavior_request = AnalysisRequest(
        analysis_type=AnalysisType.SENTIMENT,
        text="I love this product! It's amazing and works perfectly."
    )
    behavior_result = await sentiment_behavior_service.analyze(behavior_request)
    print(f"Behavior Result: {behavior_result}")
    
    print("AI Services test completed!")


if __name__ == "__main__":
    asyncio.run(test_ai_services())