#!/usr/bin/env python3

import json
from pathlib import Path
from typing import List, Dict, Any

def load_task_history(task_path: str) -> List[Dict[str, Any]]:
    """
    Load historical performance data for a task.
    Returns empty list if no history exists.
    """
    history_file = Path(task_path) / "evaluation" / "history.json"
    if not history_file.exists():
        return []
    
    with open(history_file, 'r') as f:
        return json.load(f)

def save_task_history(task_path: str, history: List[Dict[str, Any]]):
    """Save updated performance history."""
    history_file = Path(task_path) / "evaluation" / "history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

def determine_tags(
    task_path: str,
    quality_score: float,
    ttft: float,
    token_latency: float,
    memory_stats: Dict[str, Any]
) -> List[str]:
    """
    Determine which tags a model should receive based on its performance.
    Returns list of tags like ["fastest", "smallest", "most-accurate"]
    """
    tags = []
    
    # Load historical performance
    history = load_task_history(task_path)
    
    # Always require minimum quality threshold
    QUALITY_THRESHOLD = 0.8
    if quality_score < QUALITY_THRESHOLD:
        return []  # No tags if quality is below threshold
    
    # Prepare current metrics
    current_metrics = {
        "quality_score": quality_score,
        "ttft": ttft,
        "token_latency": token_latency,
        "model_size": memory_stats["size_gb"],
        "vram_usage": memory_stats["vram_gb"]
    }
    
    # Add to history
    history.append(current_metrics)
    
    # Find best historical performances
    if history:
        best_quality = max(h["quality_score"] for h in history[:-1]) if len(history) > 1 else 0
        best_speed = min((h["ttft"] + h["token_latency"]) for h in history[:-1]) if len(history) > 1 else float('inf')
        best_size = min(h["model_size"] for h in history[:-1]) if len(history) > 1 else float('inf')
        
        # Current metrics
        current_speed = ttft + token_latency
        current_size = memory_stats["size_gb"]
        
        # Determine tags
        if quality_score > best_quality:
            tags.append("most-accurate")
        
        if current_speed < best_speed:
            tags.append("fastest")
            
        if current_size < best_size:
            tags.append("smallest")
            
        # If this is the first model for the task
        if len(history) == 1:
            tags = ["first", "most-accurate", "fastest", "smallest"]
    
    # Save updated history
    save_task_history(task_path, history)
    
    return tags

def format_ollama_name(base_name: str, tags: List[str]) -> str:
    """
    Format the Ollama model name with appropriate tags.
    Example: "username/model:fastest-smallest"
    """
    if not tags:
        return base_name
    
    return f"{base_name}:{'-'.join(sorted(tags))}"

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: determine_tags.py <metrics_json>")
        sys.exit(1)
        
    with open(sys.argv[1], 'r') as f:
        metrics = json.load(f)
    
    tags = determine_tags(
        metrics["task_path"],
        metrics["quality_score"],
        metrics["ttft"],
        metrics["token_latency"],
        metrics["memory_stats"]
    )
    
    print(format_ollama_name(metrics["model_name"], tags)) 