"""
Sentiment and Behavior Analysis Service
Provides advanced sentiment analysis and behavior prediction capabilities
"""
import asyncio
import json
import time
import statistics
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ..ai_service import ultra_ai_service, AIProvider, PredictionRequest
from ..nlp.advanced_nlp import advanced_nlp_service, NLPAnalysisType, NLPAnalysisRequest


class AnalysisType(Enum):
    """Analysis type enumeration"""
    SENTIMENT = "sentiment"
    BEHAVIOR = "behavior"
    PREDICTION = "prediction"
    TREND = "trend"


class SentimentType(Enum):
    """Sentiment type enumeration"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class BehaviorPattern(Enum):
    """Behavior pattern enumeration"""
    ENGAGED = "engaged"
    DISENGAGED = "disengaged"
    INDECISIVE = "indecisive"
    DECISIVE = "decisive"
    EXPLORATORY = "exploratory"
    TRANSACTIONAL = "transactional"


@dataclass
class SentimentAnalysisResult:
    """Sentiment analysis result"""
    sentiment: SentimentType
    confidence: float
    emotions: Dict[str, float]  # joy, anger, fear, sadness, surprise, disgust
    polarity_score: float  # -1 to 1
    subjectivity_score: float  # 0 to 1


@dataclass
class BehaviorAnalysisResult:
    """Behavior analysis result"""
    pattern: BehaviorPattern
    confidence: float
    engagement_score: float  # 0 to 1
    decision_confidence: float  # 0 to 1
    exploration_tendency: float  # 0 to 1
    purchase_likelihood: float  # 0 to 1


@dataclass
class PredictionResult:
    """Prediction result"""
    prediction_type: str
    predicted_value: Any
    confidence: float
    timeframe: str
    factors: List[str]


@dataclass
class AnalysisRequest:
    """Analysis request"""
    analysis_type: AnalysisType
    text: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    timeframe: Optional[str] = None


class SentimentBehaviorAnalysisService:
    """Advanced sentiment and behavior analysis service"""

    def __init__(self):
        self.analysis_prefix = "sentiment_behavior_analysis"
        
        # Initialize with ultra AI service and NLP service
        self.ai_service = ultra_ai_service
        self.nlp_service = advanced_nlp_service

    async def analyze(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Perform sentiment or behavior analysis"""
        try:
            if request.analysis_type == AnalysisType.SENTIMENT:
                return await self._analyze_sentiment(request)
            elif request.analysis_type == AnalysisType.BEHAVIOR:
                return await self._analyze_behavior(request)
            elif request.analysis_type == AnalysisType.PREDICTION:
                return await self._predict_behavior(request)
            elif request.analysis_type == AnalysisType.TREND:
                return await self._analyze_trends(request)
            else:
                raise ValueError(f"Unsupported analysis type: {request.analysis_type}")

        except Exception as e:
            return {"error": str(e)}

    async def _analyze_sentiment(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze sentiment from text"""
        try:
            if not request.text:
                return {"error": "Text is required for sentiment analysis"}

            # Use NLP service for sentiment analysis
            nlp_request = NLPAnalysisRequest(
                text=request.text,
                analysis_type=NLPAnalysisType.SENTIMENT,
                context=request.context
            )
            
            result = await self.nlp_service.analyze_text(nlp_request)
            
            if "error" in result:
                return result

            # Extract sentiment data
            sentiment_data = result.get("result", {})
            
            return {
                "analysis_type": "sentiment",
                "sentiment": sentiment_data.get("sentiment", "neutral"),
                "confidence": result.get("confidence", 0.0),
                "emotions": sentiment_data.get("emotions", {}),
                "polarity_score": sentiment_data.get("polarity_score", 0.0),
                "processing_time": result.get("processing_time", 0.0),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Sentiment analysis failed: {str(e)}"}

    async def _analyze_behavior(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            user_data = request.user_data or {}
            
            # Extract behavioral indicators
            engagement_score = self._calculate_engagement_score(user_data)
            decision_confidence = self._calculate_decision_confidence(user_data)
            exploration_tendency = self._calculate_exploration_tendency(user_data)
            purchase_likelihood = self._calculate_purchase_likelihood(user_data)
            
            # Determine behavior pattern
            behavior_pattern = self._determine_behavior_pattern(
                engagement_score, decision_confidence, exploration_tendency
            )
            
            # Calculate overall confidence
            confidence = statistics.mean([
                engagement_score, 
                decision_confidence, 
                exploration_tendency, 
                purchase_likelihood
            ])
            
            return {
                "analysis_type": "behavior",
                "pattern": behavior_pattern.value,
                "confidence": confidence,
                "engagement_score": engagement_score,
                "decision_confidence": decision_confidence,
                "exploration_tendency": exploration_tendency,
                "purchase_likelihood": purchase_likelihood,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Behavior analysis failed: {str(e)}"}

    def _calculate_engagement_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate user engagement score based on activity data"""
        try:
            # Extract engagement indicators
            session_duration = user_data.get("session_duration", 0)
            page_views = user_data.get("page_views", 0)
            interactions = user_data.get("interactions", 0)
            return_time = user_data.get("return_time", 0)
            
            # Normalize and combine indicators (0 to 1 scale)
            duration_score = min(1.0, session_duration / 300)  # 5 minutes max
            views_score = min(1.0, page_views / 10)  # 10 pages max
            interactions_score = min(1.0, interactions / 20)  # 20 interactions max
            return_score = 1.0 if return_time > 0 else 0.0  # Binary return indicator
            
            # Weighted average
            engagement_score = (
                duration_score * 0.3 +
                views_score * 0.2 +
                interactions_score * 0.4 +
                return_score * 0.1
            )
            
            return min(1.0, max(0.0, engagement_score))
            
        except Exception:
            return 0.5  # Default neutral score

    def _calculate_decision_confidence(self, user_data: Dict[str, Any]) -> float:
        """Calculate decision confidence based on user actions"""
        try:
            # Extract decision indicators
            time_on_page = user_data.get("time_on_page", 0)
            scroll_depth = user_data.get("scroll_depth", 0)
            comparisons = user_data.get("comparisons", 0)
            reviews_read = user_data.get("reviews_read", 0)
            
            # Normalize and combine indicators
            time_score = min(1.0, time_on_page / 120)  # 2 minutes max
            scroll_score = scroll_depth  # Already 0-1
            comparisons_score = min(1.0, comparisons / 5)  # 5 comparisons max
            reviews_score = min(1.0, reviews_read / 10)  # 10 reviews max
            
            # Weighted average
            decision_score = (
                time_score * 0.25 +
                scroll_score * 0.25 +
                comparisons_score * 0.25 +
                reviews_score * 0.25
            )
            
            return min(1.0, max(0.0, decision_score))
            
        except Exception:
            return 0.5  # Default neutral score

    def _calculate_exploration_tendency(self, user_data: Dict[str, Any]) -> float:
        """Calculate exploration tendency based on navigation patterns"""
        try:
            # Extract exploration indicators
            pages_visited = user_data.get("pages_visited", 0)
            categories_viewed = user_data.get("categories_viewed", 0)
            search_queries = user_data.get("search_queries", 0)
            filters_used = user_data.get("filters_used", 0)
            
            # Normalize and combine indicators
            pages_score = min(1.0, pages_visited / 20)  # 20 pages max
            categories_score = min(1.0, categories_viewed / 5)  # 5 categories max
            search_score = min(1.0, search_queries / 10)  # 10 searches max
            filters_score = min(1.0, filters_used / 5)  # 5 filters max
            
            # Weighted average
            exploration_score = (
                pages_score * 0.3 +
                categories_score * 0.3 +
                search_score * 0.2 +
                filters_score * 0.2
            )
            
            return min(1.0, max(0.0, exploration_score))
            
        except Exception:
            return 0.5  # Default neutral score

    def _calculate_purchase_likelihood(self, user_data: Dict[str, Any]) -> float:
        """Calculate purchase likelihood based on shopping signals"""
        try:
            # Extract purchase indicators
            cart_additions = user_data.get("cart_additions", 0)
            wishlist_additions = user_data.get("wishlist_additions", 0)
            product_views = user_data.get("product_views", 0)
            checkout_attempts = user_data.get("checkout_attempts", 0)
            
            # Normalize and combine indicators
            cart_score = min(1.0, cart_additions / 5)  # 5 items max
            wishlist_score = min(1.0, wishlist_additions / 10)  # 10 items max
            product_views_score = min(1.0, product_views / 20)  # 20 products max
            checkout_score = 1.0 if checkout_attempts > 0 else 0.0  # Binary indicator
            
            # Weighted average
            purchase_score = (
                cart_score * 0.3 +
                wishlist_score * 0.2 +
                product_views_score * 0.3 +
                checkout_score * 0.2
            )
            
            return min(1.0, max(0.0, purchase_score))
            
        except Exception:
            return 0.1  # Default low score

    def _determine_behavior_pattern(self, engagement: float, decision: float, exploration: float) -> BehaviorPattern:
        """Determine behavior pattern based on scores"""
        try:
            # High engagement + high decision = DECISIVE
            if engagement >= 0.7 and decision >= 0.7:
                return BehaviorPattern.DECISIVE
            
            # High engagement + high exploration = EXPLORATORY
            if engagement >= 0.7 and exploration >= 0.7:
                return BehaviorPattern.EXPLORATORY
            
            # Low engagement + low decision + low exploration = DISENGAGED
            if engagement <= 0.3 and decision <= 0.3 and exploration <= 0.3:
                return BehaviorPattern.DISENGAGED
            
            # High engagement + low decision = INDECISIVE
            if engagement >= 0.7 and decision <= 0.3:
                return BehaviorPattern.INDECISIVE
            
            # Low engagement + high decision = TRANSACTIONAL
            if engagement <= 0.3 and decision >= 0.7:
                return BehaviorPattern.TRANSACTIONAL
            
            # Default pattern
            return BehaviorPattern.ENGAGED
            
        except Exception:
            return BehaviorPattern.ENGAGED

    async def _predict_behavior(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Predict future behavior or trends"""
        try:
            # Create AI request for behavior prediction
            ai_request = PredictionRequest(
                model_id="gpt-4",
                provider=AIProvider.OPENAI,
                input_data={
                    "task": "behavior_prediction",
                    "user_data": request.user_data or {},
                    "context": request.context or {},
                    "timeframe": request.timeframe or "next_30_days",
                    "instruction": "Predict user behavior based on provided data and context."
                },
                context=request.context or {}
            )

            # Get AI prediction
            result = await self.ai_service.make_prediction(ai_request)
            
            return {
                "analysis_type": "prediction",
                "prediction": result.result,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Behavior prediction failed: {str(e)}"}

    async def _analyze_trends(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze trends in user data or market data"""
        try:
            user_data = request.user_data or {}
            
            # Extract trend data
            historical_data = user_data.get("historical_data", [])
            
            if not historical_data:
                return {"error": "Historical data required for trend analysis"}
            
            # Calculate trends
            trend_direction = self._calculate_trend_direction(historical_data)
            trend_magnitude = self._calculate_trend_magnitude(historical_data)
            trend_confidence = self._calculate_trend_confidence(historical_data)
            
            return {
                "analysis_type": "trend",
                "trend_direction": trend_direction,
                "trend_magnitude": trend_magnitude,
                "confidence": trend_confidence,
                "data_points": len(historical_data),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}

    def _calculate_trend_direction(self, data: List[float]) -> str:
        """Calculate trend direction (increasing, decreasing, stable)"""
        try:
            if len(data) < 2:
                return "insufficient_data"
            
            # Simple linear regression slope
            n = len(data)
            x_values = list(range(n))
            y_values = data
            
            # Calculate means
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            # Calculate slope
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            if denominator == 0:
                return "stable"
            
            slope = numerator / denominator
            
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"
                
        except Exception:
            return "unknown"

    def _calculate_trend_magnitude(self, data: List[float]) -> float:
        """Calculate trend magnitude (0 to 1)"""
        try:
            if len(data) < 2:
                return 0.0
            
            # Calculate percentage change
            first_value = data[0]
            last_value = data[-1]
            
            if first_value == 0:
                return 0.0
            
            percentage_change = abs((last_value - first_value) / first_value)
            
            # Normalize to 0-1 scale (capped at 100%)
            return min(1.0, percentage_change)
            
        except Exception:
            return 0.0

    def _calculate_trend_confidence(self, data: List[float]) -> float:
        """Calculate trend confidence based on data consistency"""
        try:
            if len(data) < 3:
                return 0.5  # Low confidence with insufficient data
            
            # Calculate standard deviation as measure of consistency
            mean_val = sum(data) / len(data)
            variance = sum((x - mean_val) ** 2 for x in data) / len(data)
            std_dev = variance ** 0.5
            
            # Lower standard deviation = higher confidence
            # Normalize based on mean value
            if mean_val == 0:
                return 0.5
            
            coefficient_of_variation = std_dev / abs(mean_val)
            
            # Inverse relationship: lower CV = higher confidence
            confidence = max(0.0, min(1.0, 1.0 - coefficient_of_variation))
            
            return confidence
            
        except Exception:
            return 0.5

    async def batch_analyze(self, requests: List[AnalysisRequest]) -> List[Dict[str, Any]]:
        """Perform batch analysis on multiple requests"""
        try:
            results = []
            for request in requests:
                result = await self.analyze(request)
                results.append(result)
            return results
        except Exception as e:
            return [{"error": f"Batch analysis failed: {str(e)}"}]

    async def get_analysis_service_status(self) -> Dict[str, Any]:
        """Get analysis service status"""
        try:
            nlp_status = await self.nlp_service.get_nlp_service_status()
            
            return {
                "status": "operational",
                "ai_provider_status": self.ai_service.get_provider_status(),
                "nlp_service_status": nlp_status,
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": f"Status check failed: {str(e)}"}


# Global sentiment and behavior analysis service instance
sentiment_behavior_service = SentimentBehaviorAnalysisService()