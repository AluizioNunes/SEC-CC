"""
Machine Learning Integration for Backend
Advanced recommendation engine and predictive analytics with Redis
"""
import asyncio
import json
import time
import math
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
import numpy as np

from .client import get_redis_client


class RecommendationEngine:
    """Advanced recommendation engine with collaborative and content-based filtering"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.ml_prefix = "ml_recommendations"

        # ML Model storage
        self.models = {}
        self.user_preferences = defaultdict(dict)
        self.item_features = defaultdict(dict)

    async def track_user_behavior(
        self,
        user_id: str,
        item_id: str,
        action: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Track user behavior for ML training"""
        timestamp = time.time()

        behavior_data = {
            "user_id": user_id,
            "item_id": item_id,
            "action": action,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }

        # Store in Redis for training data
        await self.redis_client.zadd(
            f"{self.ml_prefix}:user_behavior:{user_id}",
            {json.dumps(behavior_data, default=str): timestamp}
        )

        # Store item interactions for collaborative filtering
        await self.redis_client.zadd(
            f"{self.ml_prefix}:item_interactions:{item_id}",
            {user_id: timestamp}
        )

        # Update user preferences
        await self.update_user_preferences(user_id, item_id, action)

    async def update_user_preferences(
        self,
        user_id: str,
        item_id: str,
        action: str,
        weight: float = 1.0
    ) -> None:
        """Update user preferences based on behavior"""
        # Get item features
        item_features = await self.get_item_features(item_id)
        if not item_features:
            return

        # Update user preference vector
        user_key = f"{self.ml_prefix}:user_prefs:{user_id}"

        for feature, value in item_features.items():
            current_pref = await self.redis_client.hget(user_key, feature) or 0.0
            new_pref = float(current_pref) + (weight * float(value))

            await self.redis_client.hset(user_key, feature, new_pref)

        # Store action for collaborative filtering
        action_key = f"{self.ml_prefix}:user_actions:{user_id}"
        await self.redis_client.zadd(action_key, {f"{item_id}:{action}": time.time()})

    async def get_item_features(self, item_id: str) -> Dict[str, float]:
        """Get item features for recommendation"""
        features_key = f"{self.ml_prefix}:item_features:{item_id}"
        features_data = await self.redis_client.get(features_key)

        if features_data:
            return json.loads(features_data)
        return {}

    async def set_item_features(self, item_id: str, features: Dict[str, float]) -> None:
        """Set item features for recommendation"""
        features_key = f"{self.ml_prefix}:item_features:{item_id}"
        await self.redis_client.setex(
            features_key,
            86400 * 30,  # 30 days
            json.dumps(features, default=str)
        )

    async def get_collaborative_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recommendations using collaborative filtering"""
        try:
            # Find similar users
            similar_users = await self.find_similar_users(user_id, limit=20)

            # Get items liked by similar users
            recommended_items = defaultdict(float)

            for similar_user, similarity in similar_users:
                user_actions = await self.redis_client.zrange(
                    f"{self.ml_prefix}:user_actions:{similar_user}",
                    0, -1, withscores=True
                )

                for action_data, timestamp in user_actions:
                    item_id, action = action_data.split(":", 1)

                    # Weight by action type and similarity
                    action_weight = self.get_action_weight(action)
                    similarity_weight = similarity

                    recommended_items[item_id] += action_weight * similarity_weight

            # Sort and return top recommendations
            sorted_items = sorted(
                [{"item_id": item, "score": score} for item, score in recommended_items.items()],
                key=lambda x: x["score"],
                reverse=True
            )[:limit]

            return sorted_items

        except Exception as e:
            print(f"Collaborative recommendation error: {e}")
            return []

    async def get_content_based_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recommendations using content-based filtering"""
        try:
            # Get user preferences
            user_prefs = await self.get_user_preferences(user_id)
            if not user_prefs:
                return []

            # Get all available items
            pattern = f"{self.ml_prefix}:item_features:*"
            item_keys = await self.redis_client.keys(pattern)

            recommendations = []

            for item_key in item_keys[:100]:  # Limit for performance
                item_id = item_key.split(":")[-1]
                item_features = await self.get_item_features(item_id)

                if item_features:
                    # Calculate similarity score
                    similarity = self.calculate_similarity(user_prefs, item_features)

                    recommendations.append({
                        "item_id": item_id,
                        "score": similarity,
                        "features": item_features
                    })

            # Sort by similarity
            recommendations.sort(key=lambda x: x["score"], reverse=True)

            return recommendations[:limit]

        except Exception as e:
            print(f"Content-based recommendation error: {e}")
            return []

    async def get_hybrid_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        collaborative_weight: float = 0.6,
        content_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """Get hybrid recommendations combining both methods"""
        try:
            # Get recommendations from both methods
            collaborative = await self.get_collaborative_recommendations(user_id, limit * 2)
            content_based = await self.get_content_based_recommendations(user_id, limit * 2)

            # Combine scores
            item_scores = defaultdict(float)

            # Apply collaborative filtering scores
            for item in collaborative:
                item_scores[item["item_id"]] += item["score"] * collaborative_weight

            # Apply content-based filtering scores
            for item in content_based:
                item_scores[item["item_id"]] += item["score"] * content_weight

            # Sort and return
            sorted_items = sorted(
                [{"item_id": item, "score": score} for item, score in item_scores.items()],
                key=lambda x: x["score"],
                reverse=True
            )[:limit]

            return sorted_items

        except Exception as e:
            print(f"Hybrid recommendation error: {e}")
            return []

    async def find_similar_users(self, user_id: str, limit: int = 10) -> List[Tuple[str, float]]:
        """Find users similar to the given user"""
        try:
            # Get user's actions
            user_actions = await self.redis_client.zrange(
                f"{self.ml_prefix}:user_actions:{user_id}",
                0, -1
            )

            if not user_actions:
                return []

            # Compare with other users
            pattern = f"{self.ml_prefix}:user_actions:*"
            user_keys = await self.redis_client.keys(pattern)

            similarities = []

            for user_key in user_keys[:50]:  # Limit for performance
                other_user_id = user_key.split(":")[-1]

                if other_user_id == user_id:
                    continue

                similarity = await self.calculate_user_similarity(user_id, other_user_id)
                if similarity > 0.1:  # Only include significantly similar users
                    similarities.append((other_user_id, similarity))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:limit]

        except Exception as e:
            print(f"Similar users error: {e}")
            return []

    async def calculate_user_similarity(self, user1_id: str, user2_id: str) -> float:
        """Calculate similarity between two users using cosine similarity"""
        try:
            # Get actions for both users
            actions1 = await self.redis_client.zrange(
                f"{self.ml_prefix}:user_actions:{user1_id}",
                0, -1
            )
            actions2 = await self.redis_client.zrange(
                f"{self.ml_prefix}:user_actions:{user2_id}",
                0, -1
            )

            if not actions1 or not actions2:
                return 0.0

            # Create vectors based on actions
            vector1 = self.create_user_vector(actions1)
            vector2 = self.create_user_vector(actions2)

            # Calculate cosine similarity
            return self.cosine_similarity(vector1, vector2)

        except Exception as e:
            print(f"User similarity error: {e}")
            return 0.0

    def create_user_vector(self, actions: List[str]) -> Dict[str, float]:
        """Create user preference vector from actions"""
        vector = defaultdict(float)

        for action_data in actions:
            item_id, action = action_data.split(":", 1)
            weight = self.get_action_weight(action)
            vector[item_id] += weight

        return dict(vector)

    def cosine_similarity(self, vector1: Dict[str, float], vector2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two vectors"""
        # Find common items
        common_items = set(vector1.keys()) & set(vector2.keys())

        if not common_items:
            return 0.0

        # Calculate dot product
        dot_product = sum(vector1[item] * vector2[item] for item in common_items)

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(value ** 2 for value in vector1.values()))
        magnitude2 = math.sqrt(sum(value ** 2 for value in vector2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def calculate_similarity(self, user_prefs: Dict[str, float], item_features: Dict[str, float]) -> float:
        """Calculate similarity between user preferences and item features"""
        # Simple dot product similarity
        similarity = 0.0
        for feature, pref_value in user_prefs.items():
            if feature in item_features:
                similarity += pref_value * item_features[feature]

        return similarity

    def get_action_weight(self, action: str) -> float:
        """Get weight for different action types"""
        weights = {
            "view": 1.0,
            "like": 3.0,
            "purchase": 5.0,
            "share": 4.0,
            "comment": 2.0,
            "dislike": -2.0
        }
        return weights.get(action, 1.0)

    async def get_user_preferences(self, user_id: str) -> Dict[str, float]:
        """Get user preferences vector"""
        try:
            user_key = f"{self.ml_prefix}:user_prefs:{user_id}"
            prefs_data = await self.redis_client.hgetall(user_key)

            return {k: float(v) for k, v in prefs_data.items()}

        except Exception as e:
            print(f"User preferences error: {e}")
            return {}

    async def train_recommendation_model(self, model_name: str = "default") -> Dict[str, Any]:
        """Train recommendation model using collected data"""
        try:
            # Get all user behavior data
            pattern = f"{self.ml_prefix}:user_behavior:*"
            user_keys = await self.redis_client.keys(pattern)

            training_data = []

            for user_key in user_keys[:100]:  # Limit for training
                behaviors = await self.redis_client.zrange(user_key, 0, -1)

                for behavior_data in behaviors:
                    behavior = json.loads(behavior_data)
                    training_data.append(behavior)

            # Simple training (placeholder for actual ML model)
            model_stats = {
                "training_samples": len(training_data),
                "unique_users": len(user_keys),
                "model_name": model_name,
                "training_time": time.time()
            }

            # Store model metadata
            await self.redis_client.setex(
                f"{self.ml_prefix}:model:{model_name}",
                86400 * 7,  # 7 days
                json.dumps(model_stats, default=str)
            )

            return model_stats

        except Exception as e:
            print(f"Model training error: {e}")
            return {"error": str(e)}

    async def get_recommendation_analytics(self) -> Dict[str, Any]:
        """Get recommendation system analytics"""
        try:
            # Get user behavior statistics
            pattern = f"{self.ml_prefix}:user_behavior:*"
            user_keys = await self.redis_client.keys(pattern)

            total_interactions = 0
            action_counts = Counter()

            for user_key in user_keys[:50]:  # Sample for performance
                behaviors = await self.redis_client.zrange(user_key, 0, -1)

                for behavior_data in behaviors:
                    behavior = json.loads(behavior_data)
                    total_interactions += 1
                    action_counts[behavior["action"]] += 1

            return {
                "total_interactions": total_interactions,
                "unique_users": len(user_keys),
                "action_distribution": dict(action_counts),
                "average_interactions_per_user": total_interactions / max(1, len(user_keys)),
                "recommendation_coverage": f"{len(user_keys)} users tracked"
            }

        except Exception as e:
            return {"error": str(e)}


class PredictiveAnalytics:
    """Predictive analytics for user behavior and system optimization"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.analytics_prefix = "predictive_analytics"

    async def predict_user_churn(self, user_id: str) -> Dict[str, Any]:
        """Predict user churn probability"""
        try:
            # Get user behavior history
            behavior_key = f"{self.analytics_prefix}:user_behavior:{user_id}"
            behaviors = await self.redis_client.zrange(behavior_key, 0, -1)

            if not behaviors:
                return {"churn_probability": 0.5, "confidence": "low", "reason": "insufficient_data"}

            # Simple churn prediction based on activity patterns
            recent_behaviors = [json.loads(b) for b in behaviors[-30:]]  # Last 30 actions

            # Calculate engagement score
            engagement_score = self.calculate_engagement_score(recent_behaviors)

            # Simple prediction model
            churn_probability = max(0, min(1, 1 - engagement_score))

            return {
                "user_id": user_id,
                "churn_probability": churn_probability,
                "confidence": "medium",
                "engagement_score": engagement_score,
                "recent_activity": len(recent_behaviors),
                "risk_level": "high" if churn_probability > 0.7 else "medium" if churn_probability > 0.4 else "low"
            }

        except Exception as e:
            print(f"Churn prediction error: {e}")
            return {"error": str(e)}

    def calculate_engagement_score(self, behaviors: List[Dict[str, Any]]) -> float:
        """Calculate user engagement score"""
        if not behaviors:
            return 0.0

        # Weight different actions
        action_weights = {
            "view": 1.0,
            "like": 3.0,
            "purchase": 5.0,
            "comment": 2.0,
            "share": 4.0
        }

        # Time decay factor (more recent = more important)
        now = time.time()
        total_score = 0.0
        total_weight = 0.0

        for behavior in behaviors:
            action = behavior.get("action", "view")
            timestamp = behavior.get("timestamp", now)

            # Time decay (exponential)
            days_since_action = (now - timestamp) / 86400
            time_weight = math.exp(-days_since_action / 7)  # Decay over 7 days

            action_weight = action_weights.get(action, 1.0)
            score = action_weight * time_weight

            total_score += score
            total_weight += time_weight

        return total_score / max(1, total_weight)

    async def predict_optimal_cache_ttl(self, cache_key: str) -> int:
        """Predict optimal TTL for cache key based on access patterns"""
        try:
            # Get access pattern for cache key
            access_key = f"{self.analytics_prefix}:cache_access:{cache_key}"
            access_times = await self.redis_client.zrange(access_key, 0, -1, withscores=True)

            if not access_times:
                return 300  # Default 5 minutes

            # Calculate access intervals
            intervals = []
            for i in range(1, len(access_times)):
                interval = access_times[i][1] - access_times[i-1][1]
                intervals.append(interval)

            if not intervals:
                return 300

            # Calculate optimal TTL (mean interval + standard deviation)
            mean_interval = sum(intervals) / len(intervals)
            std_dev = math.sqrt(sum((x - mean_interval) ** 2 for x in intervals) / len(intervals))

            optimal_ttl = int(mean_interval + std_dev)

            # Cap between 60 seconds and 1 hour
            return max(60, min(3600, optimal_ttl))

        except Exception as e:
            print(f"TTL prediction error: {e}")
            return 300

    async def predict_system_load(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Predict system load based on historical patterns"""
        try:
            # Get historical request data
            request_pattern = f"{self.analytics_prefix}:requests:*"
            request_keys = await self.redis_client.keys(request_pattern)

            if not request_keys:
                return {"predicted_load": "unknown", "confidence": "low"}

            # Simple load prediction based on time patterns
            current_hour = time.localtime().tm_hour

            # Mock prediction (would use actual ML model)
            predicted_load = {
                "current_hour": current_hour,
                "predicted_requests": 100 + (50 * math.sin(current_hour * math.pi / 12)),  # Sine wave pattern
                "confidence": "medium",
                "factors": ["time_of_day", "historical_patterns"]
            }

            return predicted_load

        except Exception as e:
            print(f"Load prediction error: {e}")
            return {"error": str(e)}


# Global ML instances
recommendation_engine = RecommendationEngine()
predictive_analytics = PredictiveAnalytics()
