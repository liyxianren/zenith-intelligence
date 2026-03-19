"""Model management API blueprint."""

from flask import Blueprint, jsonify, request

from app.services.ai_service import ai_service
from app.services.performance_evaluator import performance_evaluator
from app.utils.errors import APIError

model_bp = Blueprint("model", __name__)


@model_bp.route("/providers", methods=["GET"])
def list_providers():
    """List all available model providers."""
    try:
        providers = ai_service.list_providers()
        return jsonify({
            "success": True,
            "data": {
                "providers": providers,
                "default": ai_service.default_provider
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@model_bp.route("/providers/<provider_name>/health", methods=["GET"])
def check_provider_health(provider_name: str):
    """Check health of a specific provider."""
    try:
        provider = ai_service.get_provider(provider_name)
        is_healthy = provider.health_check()
        return jsonify({
            "success": True,
            "data": {
                "provider": provider_name,
                "healthy": is_healthy
            }
        })
    except APIError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@model_bp.route("/default", methods=["GET"])
def get_default_provider():
    """Get the current default provider."""
    return jsonify({
        "success": True,
        "data": {
            "default_provider": ai_service.default_provider
        }
    })


@model_bp.route("/default", methods=["POST"])
def set_default_provider():
    """Set the default provider for the current session."""
    try:
        data = request.get_json()
        if not data or "provider" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'provider' in request body"
            }), 400

        provider_name = data["provider"]
        provider = ai_service.get_provider(provider_name)
        
        if not provider.health_check():
            return jsonify({
                "success": False,
                "error": f"Provider '{provider_name}' is not available"
            }), 400

        ai_service.default_provider = provider_name

        return jsonify({
            "success": True,
            "data": {
                "default_provider": provider_name
            }
        })
    except APIError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@model_bp.route("/health", methods=["GET"])
def check_all_health():
    """Check health of all model services."""
    try:
        health_status = ai_service.health_check()
        return jsonify({
            "success": True,
            "data": health_status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@model_bp.route("/performance", methods=["GET"])
def get_performance_stats():
    """Get performance statistics for all providers."""
    try:
        provider = request.args.get("provider")
        stats = performance_evaluator.get_stats(provider)
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@model_bp.route("/performance/compare", methods=["GET"])
def compare_performance():
    """Compare performance across all providers."""
    try:
        comparison = performance_evaluator.compare_providers()
        return jsonify({
            "success": True,
            "data": {
                "comparison": comparison,
                "recommendation": performance_evaluator.get_recommendation()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@model_bp.route("/performance/clear", methods=["POST"])
def clear_performance_metrics():
    """Clear all performance metrics."""
    try:
        performance_evaluator.clear_metrics()
        return jsonify({
            "success": True,
            "message": "Performance metrics cleared"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
