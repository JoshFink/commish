"""
OpenAI Model Configuration and Pricing
Contains model definitions, pricing data, and helper functions for model selection and cost calculation.
"""

# Available OpenAI models organized by category with pricing information
OPENAI_MODELS = {
    "💰 Best for Creative Tasks": {
        "gpt-4o": "GPT-4o - $2.50/$10 per 1M tokens (Best for character roleplay)",
        "gpt-4o-mini": "GPT-4o Mini - $0.15/$0.60 per 1M tokens (Current) ⭐",
    },
    "🚀 Latest Technology": {
        "gpt-5": "GPT-5 - $1.25/$10 per 1M tokens (Latest, 90% cache discount)",
    },
    "🧠 Reasoning Models": {
        "o3": "O3 - $2/$8 per 1M tokens (Complex reasoning, 80% price drop)",
        "o3-mini": "O3 Mini - $1/$4 per 1M tokens",
        "o4-mini": "O4 Mini - $0.75/$3 per 1M tokens",
    },
    "💪 High Performance": {
        "gpt-4-turbo": "GPT-4 Turbo - $10/$30 per 1M tokens",
    },
    "💸 Budget Option": {
        "gpt-3.5-turbo": "GPT-3.5 Turbo - $0.50/$1.50 per 1M tokens",
    }
}

# Exact pricing per 1M tokens (input/output)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-5": {"input": 1.25, "output": 10.00},
    "o3": {"input": 2.00, "output": 8.00},
    "o3-mini": {"input": 1.00, "output": 4.00},
    "o4-mini": {"input": 0.75, "output": 3.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50}
}

# Model recommendations for fantasy football summaries
MODEL_RECOMMENDATIONS = {
    "gpt-4o-mini": {"badge": "⭐ Recommended", "reason": "Best creativity/cost balance"},
    "gpt-4o": {"badge": "🎭 Best Creativity", "reason": "Superior character roleplay"},
    "gpt-5": {"badge": "🆕 Latest", "reason": "Newest technology"},
    "o3": {"badge": "🧠 Smart", "reason": "Advanced reasoning"},
    "gpt-3.5-turbo": {"badge": "💸 Cheapest", "reason": "Most affordable"}
}

def get_flattened_models():
    """Return a flattened list of all available models"""
    all_models = []
    for category, models in OPENAI_MODELS.items():
        for model_id, description in models.items():
            all_models.append((f"{category}: {description}", model_id))
    return all_models

def calculate_cost(usage_data, model_id):
    """
    Calculate the cost of an OpenAI API call based on usage data
    
    Args:
        usage_data: Object with prompt_tokens, completion_tokens, total_tokens
        model_id: The model identifier (e.g., 'gpt-4o-mini')
    
    Returns:
        dict: Cost breakdown with prompt_cost, completion_cost, total_cost
    """
    if model_id not in MODEL_PRICING:
        return {"error": f"Pricing not available for model: {model_id}"}
    
    pricing = MODEL_PRICING[model_id]
    
    # Convert tokens to cost (pricing is per 1M tokens)
    prompt_cost = (usage_data.prompt_tokens / 1_000_000) * pricing["input"]
    completion_cost = (usage_data.completion_tokens / 1_000_000) * pricing["output"]
    total_cost = prompt_cost + completion_cost
    
    return {
        "prompt_tokens": usage_data.prompt_tokens,
        "completion_tokens": usage_data.completion_tokens,
        "total_tokens": usage_data.total_tokens,
        "prompt_cost": prompt_cost,
        "completion_cost": completion_cost,
        "total_cost": total_cost,
        "model": model_id
    }

def estimate_cost(input_text, estimated_output_tokens, model_id):
    """
    Estimate the cost before making an API call
    
    Args:
        input_text: The input text to be sent
        estimated_output_tokens: Estimated number of output tokens
        model_id: The model identifier
    
    Returns:
        dict: Estimated cost breakdown
    """
    if model_id not in MODEL_PRICING:
        return {"error": f"Pricing not available for model: {model_id}"}
    
    # Rough estimation: 4 characters = 1 token for English text
    estimated_input_tokens = len(input_text) // 4
    
    pricing = MODEL_PRICING[model_id]
    
    prompt_cost = (estimated_input_tokens / 1_000_000) * pricing["input"]
    completion_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]
    total_cost = prompt_cost + completion_cost
    
    return {
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "estimated_total_tokens": estimated_input_tokens + estimated_output_tokens,
        "estimated_prompt_cost": prompt_cost,
        "estimated_completion_cost": completion_cost,
        "estimated_total_cost": total_cost,
        "model": model_id
    }

def get_model_recommendation(model_id):
    """Get recommendation badge and reason for a model"""
    return MODEL_RECOMMENDATIONS.get(model_id, {"badge": "", "reason": ""})

def validate_model(model_id):
    """Validate if a model is supported"""
    return model_id in MODEL_PRICING

def get_cost_comparison(model_id, comparison_model="gpt-5"):
    """Compare cost between two models"""
    if model_id not in MODEL_PRICING or comparison_model not in MODEL_PRICING:
        return None
    
    base_pricing = MODEL_PRICING[model_id]
    comp_pricing = MODEL_PRICING[comparison_model]
    
    # Calculate percentage difference for typical usage (2000 input, 800 output tokens)
    base_cost = (2000 / 1_000_000) * base_pricing["input"] + (800 / 1_000_000) * base_pricing["output"]
    comp_cost = (2000 / 1_000_000) * comp_pricing["input"] + (800 / 1_000_000) * comp_pricing["output"]
    
    if comp_cost > base_cost:
        savings = comp_cost - base_cost
        percentage = (savings / comp_cost) * 100
        return {
            "savings": savings,
            "percentage": percentage,
            "is_cheaper": True,
            "comparison_model": comparison_model
        }
    else:
        extra_cost = base_cost - comp_cost
        percentage = (extra_cost / comp_cost) * 100
        return {
            "extra_cost": extra_cost,
            "percentage": percentage,
            "is_cheaper": False,
            "comparison_model": comparison_model
        }