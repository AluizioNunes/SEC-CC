"""
Database Advanced Search Engine
Full-text search, vector similarity, and fuzzy matching with Redis
"""
import asyncio
import json
import time
import math
import re
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter

from .client import get_redis_client


class AdvancedSearchEngine:
    """Advanced search engine with full-text search, vector similarity, and fuzzy matching"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.search_prefix = "advanced_search"

        # Search statistics
        self.stats = {
            "searches_performed": 0,
            "search_hits": 0,
            "search_misses": 0,
            "avg_search_time": 0,
            "errors": 0
        }

    async def index_document(
        self,
        document_id: str,
        content: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Index document for search"""
        try:
            # Extract searchable text
            searchable_text = self.extract_searchable_text(content)

            # Generate document vector for similarity search
            document_vector = self.generate_document_vector(searchable_text)

            # Store document data
            document_data = {
                "id": document_id,
                "content": content,
                "searchable_text": searchable_text,
                "vector": document_vector,
                "metadata": metadata or {},
                "indexed_at": time.time()
            }

            # Store in Redis
            await self.redis_client.setex(
                f"{self.search_prefix}:document:{document_id}",
                86400 * 30,  # 30 days
                json.dumps(document_data, default=str)
            )

            # Add to search index
            await self.add_to_search_index(document_id, searchable_text, document_vector)

            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Document indexing error: {e}")
            return False

    def extract_searchable_text(self, content: Dict[str, Any]) -> str:
        """Extract searchable text from document content"""
        text_parts = []

        def extract_text(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    extract_text(value, f"{prefix}.{key}" if prefix else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_text(item, f"{prefix}[{i}]")
            elif isinstance(obj, str):
                if prefix and not prefix.startswith("_"):  # Skip metadata fields
                    text_parts.append(f"{prefix}: {obj}")
                else:
                    text_parts.append(obj)

        extract_text(content)
        return " ".join(text_parts)

    def generate_document_vector(self, text: str) -> Dict[str, float]:
        """Generate vector representation of document"""
        # Simple TF-IDF like vectorization
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)

        # Calculate TF (Term Frequency)
        total_words = len(words)
        vector = {}

        for word, count in word_counts.items():
            if len(word) > 2:  # Skip very short words
                tf = count / total_words
                vector[word] = tf

        return vector

    async def add_to_search_index(self, document_id: str, text: str, vector: Dict[str, float]) -> None:
        """Add document to search index"""
        # Add to full-text index
        words = set(re.findall(r'\b\w+\b', text.lower()))

        for word in words:
            if len(word) > 2:
                await self.redis_client.sadd(f"{self.search_prefix}:word:{word}", document_id)

        # Add to vector index for similarity search
        for term, weight in vector.items():
            await self.redis_client.zadd(f"{self.search_prefix}:term:{term}", {document_id: weight})

    async def search(
        self,
        query: str,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Perform advanced search"""
        start_time = time.time()

        options = options or {}
        search_type = options.get("type", "full_text")  # full_text, fuzzy, vector
        limit = options.get("limit", 10)
        threshold = options.get("threshold", 0.1)

        try:
            if search_type == "full_text":
                results = await self.full_text_search(query, limit)
            elif search_type == "fuzzy":
                results = await self.fuzzy_search(query, limit)
            elif search_type == "vector":
                results = await self.vector_search(query, limit, threshold)
            else:
                results = await self.full_text_search(query, limit)

            search_time = time.time() - start_time

            # Update statistics
            self.stats["searches_performed"] += 1
            if results["total"] > 0:
                self.stats["search_hits"] += 1
            else:
                self.stats["search_misses"] += 1

            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (self.stats["searches_performed"] - 1) + search_time)
                / self.stats["searches_performed"]
            )

            return {
                "query": query,
                "results": results["documents"],
                "total": results["total"],
                "search_time": search_time,
                "search_type": search_type,
                "performance": "optimized"
            }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Search error: {e}")
            return {"error": str(e)}

    async def full_text_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Full-text search implementation"""
        try:
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            query_terms = [word for word in query_words if len(word) > 2]

            if not query_terms:
                return {"documents": [], "total": 0}

            # Get documents containing query terms
            candidate_docs = set()

            for term in query_terms[:5]:  # Limit terms for performance
                docs = await self.redis_client.smembers(f"{self.search_prefix}:word:{term}")
                candidate_docs.update(docs)

            # Score documents based on term matches
            scored_docs = []

            for doc_id in candidate_docs:
                score = await self.score_document(doc_id, query_terms)
                if score > 0:
                    scored_docs.append((doc_id, score))

            # Sort by score and limit results
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            # Get full document data
            documents = []
            for doc_id, score in scored_docs[:limit]:
                doc_data = await self.get_document_data(doc_id)
                if doc_data:
                    documents.append({
                        "id": doc_id,
                        "score": score,
                        "data": doc_data
                    })

            return {"documents": documents, "total": len(documents)}

        except Exception as e:
            print(f"Full-text search error: {e}")
            return {"documents": [], "total": 0}

    async def fuzzy_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Fuzzy search with typo tolerance"""
        try:
            # Get documents that might match (simplified fuzzy matching)
            query_words = re.findall(r'\b\w+\b', query.lower())

            # Find similar words in index
            candidate_terms = set()
            for word in query_words:
                # Simple fuzzy matching - find words with similar length and characters
                pattern = f"{self.search_prefix}:word:*{word[:3]}*"
                similar_keys = await self.redis_client.keys(pattern)

                for key in similar_keys[:10]:  # Limit for performance
                    term = key.split(":")[-1]
                    if self.calculate_edit_distance(word, term) <= 2:  # Max 2 edits
                        candidate_terms.add(term)

            # Search using candidate terms
            if candidate_terms:
                return await self.full_text_search(" ".join(candidate_terms), limit)

            return {"documents": [], "total": 0}

        except Exception as e:
            print(f"Fuzzy search error: {e}")
            return {"documents": [], "total": 0}

    def calculate_edit_distance(self, word1: str, word2: str) -> int:
        """Calculate Levenshtein distance between two words"""
        if len(word1) < len(word2):
            return self.calculate_edit_distance(word2, word1)

        if len(word2) == 0:
            return len(word1)

        previous_row = list(range(len(word2) + 1))

        for i, c1 in enumerate(word1):
            current_row = [i + 1]

            for j, c2 in enumerate(word2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)

                current_row.append(min(insertions, deletions, substitutions))

            previous_row = current_row

        return previous_row[-1]

    async def vector_search(self, query: str, limit: int = 10, threshold: float = 0.1) -> Dict[str, Any]:
        """Vector similarity search"""
        try:
            # Generate query vector
            query_vector = self.generate_document_vector(query)

            if not query_vector:
                return {"documents": [], "total": 0}

            # Find similar documents using vector similarity
            candidate_docs = set()

            for term, query_weight in query_vector.items():
                if query_weight < threshold:
                    continue

                # Get documents with this term
                docs = await self.redis_client.zrange(
                    f"{self.search_prefix}:term:{term}",
                    0, -1, withscores=True
                )

                for doc_id, doc_weight in docs:
                    candidate_docs.add(doc_id)

            # Calculate similarity scores
            scored_docs = []

            for doc_id in candidate_docs:
                similarity = await self.calculate_vector_similarity(query_vector, doc_id)
                if similarity >= threshold:
                    scored_docs.append((doc_id, similarity))

            # Sort by similarity
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            # Get full document data
            documents = []
            for doc_id, similarity in scored_docs[:limit]:
                doc_data = await self.get_document_data(doc_id)
                if doc_data:
                    documents.append({
                        "id": doc_id,
                        "score": similarity,
                        "data": doc_data
                    })

            return {"documents": documents, "total": len(documents)}

        except Exception as e:
            print(f"Vector search error: {e}")
            return {"documents": [], "total": 0}

    async def calculate_vector_similarity(self, query_vector: Dict[str, float], document_id: str) -> float:
        """Calculate cosine similarity between query and document vectors"""
        try:
            # Get document vector
            doc_data = await self.get_document_data(document_id)
            if not doc_data or "vector" not in doc_data:
                return 0.0

            doc_vector = doc_data["vector"]

            # Calculate cosine similarity
            dot_product = 0.0
            query_magnitude = 0.0
            doc_magnitude = 0.0

            # Find common terms
            common_terms = set(query_vector.keys()) & set(doc_vector.keys())

            for term in common_terms:
                dot_product += query_vector[term] * doc_vector[term]

            # Calculate magnitudes
            for weight in query_vector.values():
                query_magnitude += weight ** 2

            for weight in doc_vector.values():
                doc_magnitude += weight ** 2

            query_magnitude = math.sqrt(query_magnitude)
            doc_magnitude = math.sqrt(doc_magnitude)

            if query_magnitude == 0 or doc_magnitude == 0:
                return 0.0

            return dot_product / (query_magnitude * doc_magnitude)

        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0

    async def score_document(self, document_id: str, query_terms: List[str]) -> float:
        """Score document based on query term matches"""
        try:
            doc_data = await self.get_document_data(document_id)
            if not doc_data:
                return 0.0

            searchable_text = doc_data.get("searchable_text", "").lower()

            # Calculate score based on term frequency
            score = 0.0
            for term in query_terms:
                # Count occurrences
                occurrences = len(re.findall(r'\b' + re.escape(term) + r'\b', searchable_text))
                if occurrences > 0:
                    # Boost score for exact matches
                    score += occurrences * (1 + len(term) / 10)  # Longer terms get higher score

            return score

        except Exception as e:
            print(f"Document scoring error: {e}")
            return 0.0

    async def get_document_data(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document data from index"""
        try:
            doc_key = f"{self.search_prefix}:document:{document_id}"
            doc_data = await self.redis_client.get(doc_key)

            if doc_data:
                return json.loads(doc_data)
            return None

        except Exception as e:
            print(f"Document retrieval error: {e}")
            return None

    async def get_search_analytics(self) -> Dict[str, Any]:
        """Get search engine analytics"""
        try:
            # Get search statistics
            total_searches = self.stats["searches_performed"]

            if total_searches == 0:
                return {"message": "No search data available"}

            hit_rate = (self.stats["search_hits"] / total_searches) * 100

            # Get popular search terms
            pattern = f"{self.search_prefix}:word:*"
            word_keys = await self.redis_client.keys(pattern)

            term_popularity = {}
            for key in word_keys[:50]:  # Sample for performance
                term = key.split(":")[-1]
                doc_count = await self.redis_client.scard(key)
                term_popularity[term] = doc_count

            # Sort by popularity
            popular_terms = sorted(
                [{"term": term, "document_count": count} for term, count in term_popularity.items()],
                key=lambda x: x["document_count"],
                reverse=True
            )[:10]

            return {
                "total_searches": total_searches,
                "search_hits": self.stats["search_hits"],
                "search_misses": self.stats["search_misses"],
                "hit_rate_percent": round(hit_rate, 2),
                "average_search_time": round(self.stats["avg_search_time"], 3),
                "popular_terms": popular_terms,
                "errors": self.stats["errors"],
                "search_performance": "optimized"
            }

        except Exception as e:
            return {"error": str(e)}

    async def optimize_search_index(self) -> Dict[str, Any]:
        """Optimize search index for better performance"""
        try:
            # Analyze index usage patterns
            pattern = f"{self.search_prefix}:word:*"
            word_keys = await self.redis_client.keys(pattern)

            optimizations = []

            for key in word_keys[:100]:  # Sample analysis
                term = key.split(":")[-1]
                doc_count = await self.redis_client.scard(key)

                # Identify optimization opportunities
                if doc_count > 1000:  # Very common terms
                    optimizations.append({
                        "term": term,
                        "type": "high_frequency",
                        "suggestion": "Consider stop word filtering",
                        "document_count": doc_count
                    })

                if doc_count < 2:  # Very rare terms
                    optimizations.append({
                        "term": term,
                        "type": "low_frequency",
                        "suggestion": "Consider removing rare terms",
                        "document_count": doc_count
                    })

            return {
                "total_terms": len(word_keys),
                "optimizations": optimizations,
                "optimization_count": len(optimizations),
                "recommendations": [
                    "Implement stop word filtering for common terms",
                    "Consider term frequency analysis",
                    "Implement search result caching",
                    "Add search query analytics"
                ]
            }

        except Exception as e:
            return {"error": str(e)}


# Global search engine instance
search_engine = AdvancedSearchEngine()
