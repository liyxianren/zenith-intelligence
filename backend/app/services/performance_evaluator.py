"""Model performance evaluation service."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import current_app


class PerformanceMetric:
    """Performance metric for a single request."""

    def __init__(
        self,
        provider: str,
        operation: str,
        response_time: float,
        success: bool,
        error_message: Optional[str] = None,
        timestamp: Optional[str] = None,
    ):
        self.provider = provider
        self.operation = operation
        self.response_time = response_time
        self.success = success
        self.error_message = error_message
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return {
            "provider": self.provider,
            "operation": self.operation,
            "response_time": self.response_time,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }


class PerformanceStats:
    """Aggregated performance statistics for a provider."""

    def __init__(self, provider: str):
        self.provider = provider
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0
        self.min_response_time: Optional[float] = None
        self.max_response_time: Optional[float] = None
        self.last_success: Optional[str] = None
        self.last_failure: Optional[str] = None

    def add_metric(self, metric: PerformanceMetric):
        self.total_requests += 1
        self.total_response_time += metric.response_time

        if metric.success:
            self.successful_requests += 1
            self.last_success = metric.timestamp
        else:
            self.failed_requests += 1
            self.last_failure = metric.timestamp

        if self.min_response_time is None or metric.response_time < self.min_response_time:
            self.min_response_time = metric.response_time

        if self.max_response_time is None or metric.response_time > self.max_response_time:
            self.max_response_time = metric.response_time

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def average_response_time(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_response_time / self.total_requests

    def to_dict(self) -> Dict:
        return {
            "provider": self.provider,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(self.success_rate, 2),
            "average_response_time": round(self.average_response_time, 2),
            "min_response_time": round(self.min_response_time, 2) if self.min_response_time else None,
            "max_response_time": round(self.max_response_time, 2) if self.max_response_time else None,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
        }


class PerformanceEvaluator:
    """Service for evaluating and comparing model performance."""

    def __init__(self):
        self._metrics: List[PerformanceMetric] = []
        self._stats: Dict[str, PerformanceStats] = {}
        self._storage_path: Optional[Path] = None

    def _get_storage_path(self) -> Path:
        if self._storage_path is None:
            base_dir = Path(current_app.root_path).parent / "data"
            base_dir.mkdir(parents=True, exist_ok=True)
            self._storage_path = base_dir / "performance_metrics.json"
        return self._storage_path

    def _load_metrics(self):
        """Load metrics from storage."""
        if self._metrics:
            return

        try:
            storage_path = self._get_storage_path()
            if storage_path.exists():
                with open(storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("metrics", []):
                        metric = PerformanceMetric(
                            provider=item["provider"],
                            operation=item["operation"],
                            response_time=item["response_time"],
                            success=item["success"],
                            error_message=item.get("error_message"),
                            timestamp=item.get("timestamp"),
                        )
                        self._metrics.append(metric)
                        if metric.provider not in self._stats:
                            self._stats[metric.provider] = PerformanceStats(metric.provider)
                        self._stats[metric.provider].add_metric(metric)
        except Exception:
            pass

    def _save_metrics(self):
        """Save metrics to storage."""
        try:
            storage_path = self._get_storage_path()
            data = {
                "metrics": [m.to_dict() for m in self._metrics[-1000:]],
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def record_metric(
        self,
        provider: str,
        operation: str,
        response_time: float,
        success: bool,
        error_message: Optional[str] = None,
    ):
        """Record a performance metric."""
        self._load_metrics()

        metric = PerformanceMetric(
            provider=provider,
            operation=operation,
            response_time=response_time,
            success=success,
            error_message=error_message,
        )

        self._metrics.append(metric)

        if provider not in self._stats:
            self._stats[provider] = PerformanceStats(provider)
        self._stats[provider].add_metric(metric)

        self._save_metrics()

    def measure_performance(self, provider: str, operation: str):
        """Context manager for measuring performance."""
        return PerformanceContext(self, provider, operation)

    def get_stats(self, provider: Optional[str] = None) -> Dict:
        """Get performance statistics."""
        self._load_metrics()

        if provider:
            if provider in self._stats:
                return self._stats[provider].to_dict()
            return {}

        return {name: stats.to_dict() for name, stats in self._stats.items()}

    def compare_providers(self) -> List[Dict]:
        """Compare performance across all providers."""
        self._load_metrics()

        comparison = []
        for name, stats in self._stats.items():
            comparison.append({
                "provider": name,
                "success_rate": round(stats.success_rate, 2),
                "average_response_time": round(stats.average_response_time, 2),
                "total_requests": stats.total_requests,
                "score": self._calculate_score(stats),
            })

        comparison.sort(key=lambda x: x["score"], reverse=True)
        return comparison

    def _calculate_score(self, stats: PerformanceStats) -> float:
        """Calculate a composite score for a provider."""
        if stats.total_requests == 0:
            return 0.0

        success_weight = 0.7
        speed_weight = 0.3

        success_score = stats.success_rate / 100

        max_expected_time = 10.0
        speed_score = max(0, 1 - (stats.average_response_time / max_expected_time))

        return (success_score * success_weight + speed_score * speed_weight) * 100

    def get_recommendation(self) -> Optional[str]:
        """Get recommended provider based on performance."""
        comparison = self.compare_providers()
        if not comparison:
            return None

        best = comparison[0]
        if best["total_requests"] >= 5 and best["score"] >= 50:
            return best["provider"]

        return None

    def clear_metrics(self):
        """Clear all metrics."""
        self._metrics = []
        self._stats = {}
        try:
            storage_path = self._get_storage_path()
            if storage_path.exists():
                storage_path.unlink()
        except Exception:
            pass


class PerformanceContext:
    """Context manager for measuring performance."""

    def __init__(self, evaluator: PerformanceEvaluator, provider: str, operation: str):
        self.evaluator = evaluator
        self.provider = provider
        self.operation = operation
        self.start_time: Optional[float] = None
        self.success = False
        self.error_message: Optional[str] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        response_time = end_time - (self.start_time or end_time)

        if exc_type is None:
            self.success = True
        else:
            self.success = False
            self.error_message = str(exc_val)

        self.evaluator.record_metric(
            provider=self.provider,
            operation=self.operation,
            response_time=response_time,
            success=self.success,
            error_message=self.error_message,
        )

        return False


performance_evaluator = PerformanceEvaluator()
