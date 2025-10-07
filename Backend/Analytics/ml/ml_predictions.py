"""
Machine Learning Predictions Service
Advanced ML predictions with time series forecasting and anomaly detection
"""
import asyncio
import json
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ...Redis.client import get_redis_client
from ..analytics_service import UltraAnalyticsService


class PredictionModel(Enum):
    """Prediction model enumeration"""
    LINEAR_REGRESSION = "linear_regression"
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"


class PredictionHorizon(Enum):
    """Prediction horizon enumeration"""
    SHORT_TERM = "short_term"  # 1 hour
    MEDIUM_TERM = "medium_term"  # 1 day
    LONG_TERM = "long_term"  # 1 week


@dataclass
class PredictionModelConfig:
    """Prediction model configuration"""
    model_id: str
    name: str
    description: str
    model_type: PredictionModel
    target_metric: str
    features: List[str]
    horizon: PredictionHorizon
    training_window_days: int = 30
    retrain_interval_hours: int = 24
    created_at: float = time.time()


@dataclass
class PredictionResult:
    """Prediction result"""
    prediction_id: str
    model_id: str
    predicted_values: Dict[str, Any]
    confidence_intervals: Optional[Dict[str, Tuple[float, float]]] = None
    feature_importance: Optional[Dict[str, float]] = None
    model_accuracy: Optional[float] = None
    generated_at: float = time.time()


class MLPredictionsService:
    """Advanced machine learning predictions service"""

    def __init__(self, analytics_service: UltraAnalyticsService):
        self.redis_client = get_redis_client()
        self.analytics_service = analytics_service
        self.ml_prefix = "ml_predictions"

        # Model configurations
        self.model_configs: Dict[str, PredictionModelConfig] = {}

        # Prediction results
        self.prediction_results: Dict[str, PredictionResult] = {}

        # ML statistics
        self.stats = {
            "models_trained": 0,
            "predictions_made": 0,
            "models_deployed": 0,
            "errors": 0
        }

        # Start model training and prediction tasks
        asyncio.create_task(self.start_model_training())

    async def create_model(
        self,
        name: str,
        description: str,
        model_type: PredictionModel,
        target_metric: str,
        features: List[str],
        horizon: PredictionHorizon,
        training_window_days: int = 30,
        retrain_interval_hours: int = 24
    ) -> str:
        """Create prediction model"""
        try:
            model_id = f"model_{int(time.time() * 1000)}"

            model_config = PredictionModelConfig(
                model_id=model_id,
                name=name,
                description=description,
                model_type=model_type,
                target_metric=target_metric,
                features=features,
                horizon=horizon,
                training_window_days=training_window_days,
                retrain_interval_hours=retrain_interval_hours
            )

            # Store model configuration in Redis
            await self.redis_client.setex(
                f"{self.ml_prefix}:model:{model_id}",
                86400 * 365,  # 1 year
                json.dumps(asdict(model_config), default=str)
            )

            # Add to local cache
            self.model_configs[model_id] = model_config

            # Schedule model training
            asyncio.create_task(self.schedule_model_training(model_id))

            self.stats["models_deployed"] += 1

            return model_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Model creation error: {e}")
            raise

    async def train_model(self, model_id: str) -> bool:
        """Train prediction model"""
        try:
            # Get model configuration
            model_config = self.model_configs.get(model_id)
            if not model_config:
                # Try to get from Redis
                model_data = await self.redis_client.get(f"{self.ml_prefix}:model:{model_id}")
                if not model_data:
                    raise ValueError(f"Model not found: {model_id}")
                model_config = PredictionModelConfig(**json.loads(model_data))
                self.model_configs[model_id] = model_config

            # Get training data
            training_data = await self.get_training_data(model_config)

            # Train model based on type (simplified for demo)
            if model_config.model_type == PredictionModel.LINEAR_REGRESSION:
                model_result = await self.train_linear_regression(model_config, training_data)
            elif model_config.model_type == PredictionModel.TIME_SERIES:
                model_result = await self.train_time_series(model_config, training_data)
            elif model_config.model_type == PredictionModel.ANOMALY_DETECTION:
                model_result = await self.train_anomaly_detection(model_config, training_data)
            elif model_config.model_type == PredictionModel.CLUSTERING:
                model_result = await self.train_clustering(model_config, training_data)
            elif model_config.model_type == PredictionModel.CLASSIFICATION:
                model_result = await self.train_classification(model_config, training_data)
            else:
                raise ValueError(f"Unsupported model type: {model_config.model_type}")

            # Store model result
            await self.redis_client.setex(
                f"{self.ml_prefix}:result:{model_id}",
                86400 * 7,  # 1 week
                json.dumps(asdict(model_result), default=str)
            )

            # Update active predictions
            self.prediction_results[model_id] = model_result

            self.stats["models_trained"] += 1

            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Model training error: {e}")
            return False

    async def get_training_data(self, model_config: PredictionModelConfig) -> List[Dict[str, Any]]:
        """Get training data for model"""
        try:
            training_data = []
            
            # Get historical data for target metric
            metric_history = self.analytics_service.metric_values.get(model_config.target_metric, [])
            
            # Get data for feature metrics
            feature_data = {}
            for feature in model_config.features:
                feature_history = self.analytics_service.metric_values.get(feature, [])
                feature_data[feature] = feature_history
            
            # Combine data (simplified for demo)
            for i, (timestamp, value) in enumerate(metric_history):
                data_point = {
                    "timestamp": timestamp,
                    "target": value
                }
                
                # Add feature values
                for feature, history in feature_data.items():
                    if i < len(history):
                        data_point[feature] = history[i][1]
                    else:
                        data_point[feature] = 0  # Default value
                
                training_data.append(data_point)
            
            return training_data

        except Exception as e:
            print(f"Training data retrieval error: {e}")
            return []

    async def train_linear_regression(self, model_config: PredictionModelConfig, training_data: List[Dict[str, Any]]) -> PredictionResult:
        """Train linear regression model (simplified)"""
        try:
            # Simplified linear regression for demo
            prediction_id = f"pred_{int(time.time() * 1000)}_{model_config.model_id}"
            
            # Generate mock predictions
            predicted_values = {}
            confidence_intervals = {}
            feature_importance = {}
            
            # For each feature, generate a mock coefficient
            for feature in model_config.features:
                coefficient = random.uniform(-1, 1)
                feature_importance[feature] = abs(coefficient)
                
                # Generate mock prediction
                predicted_values[feature] = coefficient * random.uniform(10, 100)
                confidence_intervals[feature] = (
                    predicted_values[feature] * 0.9,
                    predicted_values[feature] * 1.1
                )
            
            # Calculate overall accuracy (mock)
            accuracy = random.uniform(0.7, 0.95)
            
            return PredictionResult(
                prediction_id=prediction_id,
                model_id=model_config.model_id,
                predicted_values=predicted_values,
                confidence_intervals=confidence_intervals,
                feature_importance=feature_importance,
                model_accuracy=accuracy
            )

        except Exception as e:
            print(f"Linear regression training error: {e}")
            raise

    async def train_time_series(self, model_config: PredictionModelConfig, training_data: List[Dict[str, Any]]) -> PredictionResult:
        """Train time series model (simplified)"""
        try:
            prediction_id = f"pred_{int(time.time() * 1000)}_{model_config.model_id}"
            
            # Generate mock time series predictions
            predicted_values = {}
            confidence_intervals = {}
            
            # Predict next values based on recent trends
            if training_data:
                recent_data = training_data[-10:]  # Last 10 data points
                avg_trend = sum(point["target"] for point in recent_data) / len(recent_data)
                
                # Predict next 3 time points
                for i in range(1, 4):
                    predicted_value = avg_trend * (1 + random.uniform(-0.1, 0.1))
                    predicted_values[f"t+{i}"] = predicted_value
                    confidence_intervals[f"t+{i}"] = (
                        predicted_value * 0.95,
                        predicted_value * 1.05
                    )
            
            # Calculate accuracy (mock)
            accuracy = random.uniform(0.8, 0.98)
            
            return PredictionResult(
                prediction_id=prediction_id,
                model_id=model_config.model_id,
                predicted_values=predicted_values,
                confidence_intervals=confidence_intervals,
                model_accuracy=accuracy
            )

        except Exception as e:
            print(f"Time series training error: {e}")
            raise

    async def train_anomaly_detection(self, model_config: PredictionModelConfig, training_data: List[Dict[str, Any]]) -> PredictionResult:
        """Train anomaly detection model (simplified)"""
        try:
            prediction_id = f"pred_{int(time.time() * 1000)}_{model_config.model_id}"
            
            # Generate mock anomaly detection results
            predicted_values = {}
            confidence_intervals = {}
            
            # Calculate statistical thresholds
            if training_data:
                values = [point["target"] for point in training_data]
                mean_val = sum(values) / len(values)
                std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
                
                # Set anomaly thresholds
                lower_threshold = mean_val - 2 * std_val
                upper_threshold = mean_val + 2 * std_val
                
                predicted_values["lower_threshold"] = lower_threshold
                predicted_values["upper_threshold"] = upper_threshold
                predicted_values["mean"] = mean_val
                predicted_values["std"] = std_val
                
                confidence_intervals["thresholds"] = (lower_threshold, upper_threshold)
            
            # Calculate accuracy (mock)
            accuracy = random.uniform(0.85, 0.95)
            
            return PredictionResult(
                prediction_id=prediction_id,
                model_id=model_config.model_id,
                predicted_values=predicted_values,
                confidence_intervals=confidence_intervals,
                model_accuracy=accuracy
            )

        except Exception as e:
            print(f"Anomaly detection training error: {e}")
            raise

    async def train_clustering(self, model_config: PredictionModelConfig, training_data: List[Dict[str, Any]]) -> PredictionResult:
        """Train clustering model (simplified)"""
        try:
            prediction_id = f"pred_{int(time.time() * 1000)}_{model_config.model_id}"
            
            # Generate mock clustering results
            predicted_values = {}
            confidence_intervals = {}
            
            # Generate mock clusters
            num_clusters = random.randint(3, 8)
            clusters = {}
            
            for i in range(num_clusters):
                cluster_center = {
                    "x": random.uniform(0, 100),
                    "y": random.uniform(0, 100)
                }
                cluster_size = random.randint(10, 100)
                
                clusters[f"cluster_{i}"] = {
                    "center": cluster_center,
                    "size": cluster_size
                }
            
            predicted_values["clusters"] = clusters
            predicted_values["num_clusters"] = num_clusters
            
            # Calculate accuracy (mock)
            accuracy = random.uniform(0.75, 0.9)
            
            return PredictionResult(
                prediction_id=prediction_id,
                model_id=model_config.model_id,
                predicted_values=predicted_values,
                model_accuracy=accuracy
            )

        except Exception as e:
            print(f"Clustering training error: {e}")
            raise

    async def train_classification(self, model_config: PredictionModelConfig, training_data: List[Dict[str, Any]]) -> PredictionResult:
        """Train classification model (simplified)"""
        try:
            prediction_id = f"pred_{int(time.time() * 1000)}_{model_config.model_id}"
            
            # Generate mock classification results
            predicted_values = {}
            confidence_intervals = {}
            feature_importance = {}
            
            # Generate mock class probabilities
            classes = ["low", "medium", "high"]
            probabilities = {}
            
            total_prob = 0
            for cls in classes:
                prob = random.uniform(0, 1)
                probabilities[cls] = prob
                total_prob += prob
            
            # Normalize probabilities
            for cls in classes:
                probabilities[cls] /= total_prob
            
            predicted_values["probabilities"] = probabilities
            predicted_values["predicted_class"] = max(probabilities, key=probabilities.get)
            
            # Generate mock feature importance
            for feature in model_config.features:
                feature_importance[feature] = random.uniform(0, 1)
            
            # Calculate accuracy (mock)
            accuracy = random.uniform(0.8, 0.95)
            
            return PredictionResult(
                prediction_id=prediction_id,
                model_id=model_config.model_id,
                predicted_values=predicted_values,
                confidence_intervals=confidence_intervals,
                feature_importance=feature_importance,
                model_accuracy=accuracy
            )

        except Exception as e:
            print(f"Classification training error: {e}")
            raise

    async def make_prediction(self, model_id: str) -> PredictionResult:
        """Make prediction using trained model"""
        try:
            # Get latest model result
            model_result = self.prediction_results.get(model_id)
            if not model_result:
                # Try to get from Redis
                result_data = await self.redis_client.get(f"{self.ml_prefix}:result:{model_id}")
                if result_data:
                    model_result = PredictionResult(**json.loads(result_data))
                    self.prediction_results[model_id] = model_result
                else:
                    # Train model if not available
                    await self.train_model(model_id)
                    model_result = self.prediction_results.get(model_id)
            
            if model_result:
                self.stats["predictions_made"] += 1
                return model_result
            else:
                raise ValueError(f"Could not generate prediction for model: {model_id}")

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Prediction error: {e}")
            raise

    async def schedule_model_training(self, model_id: str):
        """Schedule model training based on configuration"""
        try:
            model_config = self.model_configs.get(model_id)
            if not model_config:
                return

            while True:
                try:
                    # Train model
                    await self.train_model(model_id)
                    
                    # Wait until next training time
                    wait_time = model_config.retrain_interval_hours * 3600
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    print(f"Model training scheduling error for {model_id}: {e}")
                    await asyncio.sleep(3600)  # Wait 1 hour before retrying

        except Exception as e:
            print(f"Model training scheduling setup error: {e}")

    async def start_model_training(self):
        """Start model training for all deployed models"""
        try:
            # Get all model configurations from Redis
            pattern = f"{self.ml_prefix}:model:*"
            model_keys = await self.redis_client.keys(pattern)
            
            for model_key in model_keys:
                model_id = model_key.split(":")[-1]
                model_data = await self.redis_client.get(model_key)
                if model_data:
                    model_config = PredictionModelConfig(**json.loads(model_data))
                    self.model_configs[model_id] = model_config
                    
                    # Schedule model training
                    asyncio.create_task(self.schedule_model_training(model_id))

        except Exception as e:
            print(f"Model training startup error: {e}")

    async def get_model_prediction(self, model_id: str) -> Optional[PredictionResult]:
        """Get latest model prediction"""
        try:
            # Check active predictions first
            if model_id in self.prediction_results:
                return self.prediction_results[model_id]
            
            # Get from Redis
            result_data = await self.redis_client.get(f"{self.ml_prefix}:result:{model_id}")
            if result_data:
                return PredictionResult(**json.loads(result_data))
            
            return None

        except Exception as e:
            print(f"Model prediction retrieval error: {e}")
            return None

    async def get_ml_statistics(self) -> Dict[str, Any]:
        """Get ML service statistics"""
        try:
            return {
                "ml_stats": self.stats.copy(),
                "deployed_models": len(self.model_configs),
                "active_predictions": len(self.prediction_results),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global ML predictions service instance
ml_predictions = None


async def initialize_ml_predictions(analytics_service: UltraAnalyticsService):
    """Initialize ML predictions service"""
    global ml_predictions
    if ml_predictions is None:
        ml_predictions = MLPredictionsService(analytics_service)
    return ml_predictions