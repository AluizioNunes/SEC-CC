"""
Ultra AI Service - Multi-Provider AI Integration
Integrates OpenAI, Google Gemini, and Anthropic Claude
"""
import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import AI providers - these might not be available in all environments
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    anthropic = None

from ..Redis.client import get_redis_client


class AIProvider(Enum):
    """AI provider enumeration"""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    AUTO = "auto"  # Automatically select best provider


@dataclass
class AIModel:
    """AI model information"""
    id: str
    name: str
    provider: AIProvider
    capabilities: List[str]
    version: str


@dataclass
class PredictionRequest:
    """AI prediction request"""
    model_id: str
    input_data: Dict[str, Any]
    context: Dict[str, Any]
    provider: AIProvider = AIProvider.AUTO


@dataclass
class PredictionResult:
    """AI prediction result"""
    prediction_id: str
    model_id: str
    provider: AIProvider
    result: Any
    confidence: float
    processing_time: float
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class UltraAIService:
    """Ultra-advanced AI service with multi-provider support"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.ai_prefix = "ultra_ai"

        # Initialize AI providers
        self.openai_client = None
        self.gemini_client = None
        self.claude_client = None

        # AI models registry
        self.models: Dict[str, AIModel] = {}
        self.model_performance: Dict[str, List[float]] = {}

        # Initialize providers
        self._initialize_providers()

        # Register available models
        self._register_models()

    def _initialize_providers(self):
        """Initialize AI providers"""
        # OpenAI
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")

        # Google Gemini
        if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini_client = genai
            except Exception as e:
                print(f"Gemini initialization failed: {e}")

        # Anthropic Claude
        if CLAUDE_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            except Exception as e:
                print(f"Claude initialization failed: {e}")

    def _register_models(self):
        """Register available AI models"""
        # OpenAI models
        if self.openai_client:
            self.models["gpt-4"] = AIModel(
                id="gpt-4",
                name="GPT-4",
                provider=AIProvider.OPENAI,
                capabilities=["text", "code", "reasoning"],
                version="latest"
            )
            self.models["gpt-3.5-turbo"] = AIModel(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider=AIProvider.OPENAI,
                capabilities=["text", "code"],
                version="latest"
            )

        # Google Gemini models
        if self.gemini_client:
            self.models["gemini-pro"] = AIModel(
                id="gemini-pro",
                name="Gemini Pro",
                provider=AIProvider.GEMINI,
                capabilities=["text", "code", "multimodal"],
                version="latest"
            )
            self.models["gemini-pro-vision"] = AIModel(
                id="gemini-pro-vision",
                name="Gemini Pro Vision",
                provider=AIProvider.GEMINI,
                capabilities=["text", "code", "vision"],
                version="latest"
            )

        # Anthropic Claude models
        if self.claude_client:
            self.models["claude-3-opus"] = AIModel(
                id="claude-3-opus",
                name="Claude 3 Opus",
                provider=AIProvider.CLAUDE,
                capabilities=["text", "code", "reasoning"],
                version="latest"
            )
            self.models["claude-3-sonnet"] = AIModel(
                id="claude-3-sonnet",
                name="Claude 3 Sonnet",
                provider=AIProvider.CLAUDE,
                capabilities=["text", "code"],
                version="latest"
            )

    async def make_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Make AI prediction using specified or auto-selected provider"""
        start_time = time.time()

        # Validate model
        model = self.models.get(request.model_id)
        if not model:
            raise ValueError(f"Model {request.model_id} not found")

        # Select provider
        provider = request.provider
        if provider == AIProvider.AUTO:
            provider = self._select_best_provider(model)

        # Make prediction based on provider
        result = None
        confidence = 0.95
        cost = None

        try:
            if provider == AIProvider.OPENAI and self.openai_client:
                result, confidence, cost = await self._predict_with_openai(model, request)
            elif provider == AIProvider.GEMINI and self.gemini_client:
                result, confidence, cost = await self._predict_with_gemini(model, request)
            elif provider == AIProvider.CLAUDE and self.claude_client:
                result, confidence, cost = await self._predict_with_claude(model, request)
            else:
                raise ValueError(f"Provider {provider} not available for model {request.model_id}")

            processing_time = time.time() - start_time

            prediction_result = PredictionResult(
                prediction_id=f"pred_{int(time.time() * 1000)}",
                model_id=request.model_id,
                provider=provider,
                result=result,
                confidence=confidence,
                processing_time=processing_time,
                cost=cost
            )

            # Cache result
            await self._cache_prediction(request, prediction_result)

            return prediction_result

        except Exception as e:
            processing_time = time.time() - start_time
            print(f"AI prediction error: {e}")
            raise

    def _select_best_provider(self, model: AIModel) -> AIProvider:
        """Select best provider based on model capabilities and performance"""
        # For now, prefer providers in this order: OpenAI, Gemini, Claude
        # In production, this would use performance metrics and cost optimization
        if model.provider != AIProvider.AUTO:
            return model.provider

        if self.openai_client:
            return AIProvider.OPENAI
        elif self.gemini_client:
            return AIProvider.GEMINI
        elif self.claude_client:
            return AIProvider.CLAUDE
        else:
            raise ValueError("No AI providers available")

    async def _predict_with_openai(self, model: AIModel, request: PredictionRequest) -> tuple:
        """Make prediction using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        try:
            # Handle different model types
            if model.id.startswith("gpt-"):
                response = self.openai_client.chat.completions.create(
                    model=model.id,
                    messages=[
                        {"role": "system", "content": "You are an ultra-advanced AI assistant."},
                        {"role": "user", "content": json.dumps(request.input_data)}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                result = response.choices[0].message.content
                confidence = 0.95
                cost = response.usage.completion_tokens * 0.00003 if response.usage else None
                return result, confidence, cost

        except Exception as e:
            print(f"OpenAI prediction error: {e}")
            raise

    async def _predict_with_gemini(self, model: AIModel, request: PredictionRequest) -> tuple:
        """Make prediction using Google Gemini"""
        if not self.gemini_client:
            raise ValueError("Gemini client not initialized")

        try:
            gemini_model = self.gemini_client.GenerativeModel(model.id)
            response = await gemini_model.generate_content_async(
                json.dumps(request.input_data),
                generation_config=self.gemini_client.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            result = response.text
            confidence = 0.93
            # Gemini pricing is more complex, simplified here
            cost = len(result) * 0.0000005 if result else None
            return result, confidence, cost

        except Exception as e:
            print(f"Gemini prediction error: {e}")
            raise

    async def _predict_with_claude(self, model: AIModel, request: PredictionRequest) -> tuple:
        """Make prediction using Anthropic Claude"""
        if not self.claude_client:
            raise ValueError("Claude client not initialized")

        try:
            response = self.claude_client.messages.create(
                model=model.id,
                messages=[
                    {"role": "user", "content": json.dumps(request.input_data)}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            result = response.content[0].text if response.content else ""
            confidence = 0.94
            cost = response.usage.output_tokens * 0.000015 if response.usage else None
            return result, confidence, cost

        except Exception as e:
            print(f"Claude prediction error: {e}")
            raise

    async def _cache_prediction(self, request: PredictionRequest, result: PredictionResult):
        """Cache prediction result"""
        try:
            cache_key = f"{self.ai_prefix}:prediction:{result.prediction_id}"
            cache_data = {
                "request": asdict(request),
                "result": asdict(result),
                "cached_at": time.time()
            }
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour cache
                json.dumps(cache_data, default=str)
            )
        except Exception as e:
            print(f"Prediction caching error: {e}")

    async def get_cached_prediction(self, prediction_id: str) -> Optional[PredictionResult]:
        """Get cached prediction result"""
        try:
            cache_key = f"{self.ai_prefix}:prediction:{prediction_id}"
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                cache_info = json.loads(cached_data)
                result_data = cache_info["result"]
                return PredictionResult(**result_data)
            return None
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        return [asdict(model) for model in self.models.values()]

    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of AI providers"""
        return {
            "openai": self.openai_client is not None,
            "gemini": self.gemini_client is not None,
            "claude": self.claude_client is not None
        }


# Global AI service instance
ultra_ai_service = UltraAIService()