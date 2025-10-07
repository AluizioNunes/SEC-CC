"""
Advanced Natural Language Processing Service
Provides advanced NLP capabilities including sentiment analysis, entity recognition, and text summarization
"""
import asyncio
import json
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ..ai_service import ultra_ai_service, AIProvider, PredictionRequest


class NLPAnalysisType(Enum):
    """NLP analysis type enumeration"""
    SENTIMENT = "sentiment"
    ENTITY_RECOGNITION = "entity_recognition"
    TEXT_SUMMARIZATION = "text_summarization"
    KEYWORD_EXTRACTION = "keyword_extraction"
    LANGUAGE_DETECTION = "language_detection"
    TOPIC_MODELING = "topic_modeling"


@dataclass
class NLPAnalysisRequest:
    """NLP analysis request"""
    text: str
    analysis_type: NLPAnalysisType
    language: str = "en"
    context: Optional[Dict[str, Any]] = None


@dataclass
class SentimentAnalysisResult:
    """Sentiment analysis result"""
    sentiment: str  # positive, negative, neutral
    confidence: float
    emotions: Dict[str, float]  # joy, anger, fear, sadness, surprise
    polarity_score: float  # -1 to 1


@dataclass
class EntityRecognitionResult:
    """Entity recognition result"""
    entities: List[Dict[str, Any]]  # List of entities with type, text, and confidence
    relations: List[Dict[str, Any]]  # Entity relationships


@dataclass
class TextSummarizationResult:
    """Text summarization result"""
    summary: str
    key_points: List[str]
    word_count: int
    compression_ratio: float


@dataclass
class KeywordExtractionResult:
    """Keyword extraction result"""
    keywords: List[Dict[str, Any]]  # List of keywords with importance score
    key_phrases: List[str]


class AdvancedNLPService:
    """Advanced natural language processing service"""

    def __init__(self):
        self.nlp_prefix = "nlp_service"
        self.supported_languages = ["en", "pt", "es", "fr", "de", "it", "ja", "zh"]
        
        # Initialize with ultra AI service
        self.ai_service = ultra_ai_service

    async def analyze_text(self, request: NLPAnalysisRequest) -> Dict[str, Any]:
        """Perform NLP analysis on text"""
        try:
            if request.analysis_type == NLPAnalysisType.SENTIMENT:
                return await self._perform_sentiment_analysis(request)
            elif request.analysis_type == NLPAnalysisType.ENTITY_RECOGNITION:
                return await self._perform_entity_recognition(request)
            elif request.analysis_type == NLPAnalysisType.TEXT_SUMMARIZATION:
                return await self._perform_text_summarization(request)
            elif request.analysis_type == NLPAnalysisType.KEYWORD_EXTRACTION:
                return await self._perform_keyword_extraction(request)
            elif request.analysis_type == NLPAnalysisType.LANGUAGE_DETECTION:
                return await self._perform_language_detection(request)
            elif request.analysis_type == NLPAnalysisType.TOPIC_MODELING:
                return await self._perform_topic_modeling(request)
            else:
                raise ValueError(f"Unsupported analysis type: {request.analysis_type}")

        except Exception as e:
            return {"error": str(e)}

    async def _perform_sentiment_analysis(self, request: NLPAnalysisRequest) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        try:
            # Create AI request for sentiment analysis
            ai_request = PredictionRequest(
                model_id="gpt-4",  # Use advanced model for sentiment analysis
                provider=AIProvider.OPENAI,
                input_data={
                    "task": "sentiment_analysis",
                    "text": request.text,
                    "language": request.language,
                    "instruction": "Analyze the sentiment of the provided text. Return a JSON object with sentiment (positive/negative/neutral), confidence score (0-1), emotions (joy, anger, fear, sadness, surprise with scores), and polarity score (-1 to 1)."
                },
                context=request.context or {}
            )

            # Get AI prediction
            result = await self.ai_service.make_prediction(ai_request)
            
            # Parse the result
            try:
                sentiment_data = json.loads(result.result)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic result
                sentiment_data = {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "emotions": {
                        "joy": 0.5,
                        "anger": 0.1,
                        "fear": 0.1,
                        "sadness": 0.1,
                        "surprise": 0.2
                    },
                    "polarity_score": 0.0
                }

            return {
                "analysis_type": "sentiment",
                "result": sentiment_data,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Sentiment analysis failed: {str(e)}"}

    async def _perform_entity_recognition(self, request: NLPAnalysisRequest) -> Dict[str, Any]:
        """Perform entity recognition"""
        try:
            # Create AI request for entity recognition
            ai_request = PredictionRequest(
                model_id="gpt-4",  # Use advanced model for entity recognition
                provider=AIProvider.OPENAI,
                input_data={
                    "task": "entity_recognition",
                    "text": request.text,
                    "language": request.language,
                    "instruction": "Identify named entities in the provided text. Return a JSON object with entities (list of {type, text, confidence}) and relations (list of {subject, relation, object})."
                },
                context=request.context or {}
            )

            # Get AI prediction
            result = await self.ai_service.make_prediction(ai_request)
            
            # Parse the result
            try:
                entity_data = json.loads(result.result)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic result
                entity_data = {
                    "entities": [],
                    "relations": []
                }

            return {
                "analysis_type": "entity_recognition",
                "result": entity_data,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Entity recognition failed: {str(e)}"}

    async def _perform_text_summarization(self, request: NLPAnalysisRequest) -> Dict[str, Any]:
        """Perform text summarization"""
        try:
            # Create AI request for text summarization
            ai_request = PredictionRequest(
                model_id="gpt-4",  # Use advanced model for summarization
                provider=AIProvider.OPENAI,
                input_data={
                    "task": "text_summarization",
                    "text": request.text,
                    "language": request.language,
                    "instruction": "Summarize the provided text. Return a JSON object with summary (concise summary), key_points (list of main points), word_count (of summary), and compression_ratio (summary_length/original_length)."
                },
                context=request.context or {}
            )

            # Get AI prediction
            result = await self.ai_service.make_prediction(ai_request)
            
            # Parse the result
            try:
                summary_data = json.loads(result.result)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic result
                summary_data = {
                    "summary": "Summary not available",
                    "key_points": [],
                    "word_count": 0,
                    "compression_ratio": 0.0
                }

            return {
                "analysis_type": "text_summarization",
                "result": summary_data,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Text summarization failed: {str(e)}"}

    async def _perform_keyword_extraction(self, request: NLPAnalysisRequest) -> Dict[str, Any]:
        """Perform keyword extraction"""
        try:
            # Create AI request for keyword extraction
            ai_request = PredictionRequest(
                model_id="gpt-4",  # Use advanced model for keyword extraction
                provider=AIProvider.OPENAI,
                input_data={
                    "task": "keyword_extraction",
                    "text": request.text,
                    "language": request.language,
                    "instruction": "Extract important keywords and key phrases from the provided text. Return a JSON object with keywords (list of {text, importance_score}) and key_phrases (list of strings)."
                },
                context=request.context or {}
            )

            # Get AI prediction
            result = await self.ai_service.make_prediction(ai_request)
            
            # Parse the result
            try:
                keyword_data = json.loads(result.result)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic result
                keyword_data = {
                    "keywords": [],
                    "key_phrases": []
                }

            return {
                "analysis_type": "keyword_extraction",
                "result": keyword_data,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Keyword extraction failed: {str(e)}"}

    async def _perform_language_detection(self, request: NLPAnalysisRequest) -> Dict[str, Any]:
        """Perform language detection"""
        try:
            # Simple language detection based on common words and patterns
            # In production, this would use a more sophisticated approach
            
            # Count characters from different language sets
            text = request.text.lower()
            
            # Basic language detection heuristics
            language_scores = {}
            
            # Portuguese indicators
            pt_words = ["o", "a", "que", "de", "e", "do", "da", "em", "um", "para", "com", "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como", "mas", "ao", "ele", "das", "seu", "sua", "ou", "quando", "muito", "sem", "nos", "já", "também", "só", "pelo", "pela", "até", "isso", "ela", "entre", "era", "depois", "sem", "mesmo", "aos", "ter", "seus", "quem", "nas", "me", "esse", "eles", "está", "você", "tinha", "foram", "essa", "num", "nem", "suas", "meu", "às", "minha", "têm", "numa", "pelos", "elas", "havia", "seja", "qual", "será", "nós", "tenho", "lhe", "deles", "essas", "esses", "pelas", "este", "fosse", "dele"]
            pt_score = sum(1 for word in pt_words if word in text)
            language_scores["pt"] = pt_score
            
            # English indicators
            en_words = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their"]
            en_score = sum(1 for word in en_words if word in text)
            language_scores["en"] = en_score
            
            # Spanish indicators
            es_words = ["de", "que", "no", "a", "la", "el", "es", "y", "en", "lo", "un", "por", "qué", "me", "una", "te", "los", "se", "con", "para", "mi", "está", "si", "bien", "pero", "yo", "eso", "las", "sí", "su", "tu", "del", "al", "como", "le", "más", "dos", "hacer", "o", "fue", "sin", "cuando", "muy", "sobre", "también", "mejor", "años", "ellos", "usted", "otro", "donde", "mismo", "ese", "ahora", "entonces", "tiempo", "verdad", "vida", "caso", "cosa", "tan", "ser", "así", "todo", "hasta", "otra", "desde", "muy", "era", "ni", "siempre", "entre", "tres"]
            es_score = sum(1 for word in es_words if word in text)
            language_scores["es"] = es_score
            
            # Handle case where no words matched
            if not language_scores:
                return {
                    "analysis_type": "language_detection",
                    "result": {
                        "language": "unknown",
                        "confidence": 0.0,
                        "scores": {}
                    },
                    "confidence": 0.0,
                    "processing_time": 0.01,
                    "timestamp": time.time()
                }
            
            # Determine most likely language
            detected_language = max(language_scores.keys(), key=lambda x: language_scores[x])
            total_score = sum(language_scores.values())
            confidence = language_scores[detected_language] / total_score if total_score > 0 else 0.5
            
            return {
                "analysis_type": "language_detection",
                "result": {
                    "language": detected_language,
                    "confidence": confidence,
                    "scores": language_scores
                },
                "confidence": confidence,
                "processing_time": 0.01,  # Very fast processing
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Language detection failed: {str(e)}"}

    async def _perform_topic_modeling(self, request: NLPAnalysisRequest) -> Dict[str, Any]:
        """Perform topic modeling"""
        try:
            # Create AI request for topic modeling
            ai_request = PredictionRequest(
                model_id="gpt-4",  # Use advanced model for topic modeling
                provider=AIProvider.OPENAI,
                input_data={
                    "task": "topic_modeling",
                    "text": request.text,
                    "language": request.language,
                    "instruction": "Identify main topics in the provided text. Return a JSON object with topics (list of {name, relevance_score, keywords}) and overall_theme."
                },
                context=request.context or {}
            )

            # Get AI prediction
            result = await self.ai_service.make_prediction(ai_request)
            
            # Parse the result
            try:
                topic_data = json.loads(result.result)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic result
                topic_data = {
                    "topics": [],
                    "overall_theme": "Unknown"
                }

            return {
                "analysis_type": "topic_modeling",
                "result": topic_data,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Topic modeling failed: {str(e)}"}

    async def batch_analyze_texts(self, requests: List[NLPAnalysisRequest]) -> List[Dict[str, Any]]:
        """Perform batch NLP analysis on multiple texts"""
        try:
            results = []
            for request in requests:
                result = await self.analyze_text(request)
                results.append(result)
            return results
        except Exception as e:
            return [{"error": f"Batch analysis failed: {str(e)}"}]

    async def get_nlp_service_status(self) -> Dict[str, Any]:
        """Get NLP service status"""
        try:
            provider_status = self.ai_service.get_provider_status()
            available_models = self.ai_service.get_available_models()
            
            return {
                "status": "operational",
                "supported_languages": self.supported_languages,
                "available_models": [model["id"] for model in available_models],
                "ai_provider_status": provider_status,
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": f"Status check failed: {str(e)}"}


# Global advanced NLP service instance
advanced_nlp_service = AdvancedNLPService()