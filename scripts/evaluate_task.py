#!/usr/bin/env python3

import json
import sys
import os
from typing import Tuple, Dict
from pathlib import Path
import importlib.util
from ollama import chat

# Default baseline metrics (intentionally poor values)
DEFAULT_BASELINE = {
    "fastest": {
        "ttft": 100.0,  # 10 seconds to first token
        "token_latency": 1.0  # 1 second per token
    },
    "smallest": {
        "size_gb": 100.0,  # 100GB model size
        "vram_gb": 100.0  # 100GB VRAM usage
    },
    "best-quality": {
        "quality": 0  # 80% quality score
    }
}

def load_baseline_metrics(task_path: str) -> Dict:
    """
    Load baseline metrics from task directory, or return defaults if not found.
    """
    metrics_file = Path(task_path) / "evaluation" / "baseline_metrics.json"
    try:
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                return json.load(f)
        return DEFAULT_BASELINE
    except Exception as e:
        print(f"Warning: Could not load baseline metrics: {e}")
        return DEFAULT_BASELINE

def save_baseline_metrics(task_path: str, metrics: Dict):
    """
    Save new baseline metrics if they're better than current ones.
    """
    metrics_file = Path(task_path) / "evaluation" / "baseline_metrics.json"
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save baseline metrics: {e}")

def get_task_metrics(task_path: str) -> Tuple[object, object]:
    """
    Dynamically import the task's metric modules.
    """
    metrics_path = Path(task_path) / "evaluation" / "metrics"
    
    # Import quality metrics
    quality_spec = importlib.util.spec_from_file_location(
        "response_quality",
        metrics_path / "response_quality.py"
    )
    quality_module = importlib.util.module_from_spec(quality_spec)
    quality_spec.loader.exec_module(quality_module)
    
    # Import performance metrics
    perf_spec = importlib.util.spec_from_file_location(
        "performance",
        metrics_path / "performance.py"
    )
    perf_module = importlib.util.module_from_spec(perf_spec)
    perf_spec.loader.exec_module(perf_module)
    
    return quality_module, perf_module


def evaluate_task(task_path: str, model_name: str) -> Tuple[float, float, float, dict]:
    """
    Evaluate a specific task's model.
    
    Returns:
        Tuple of (avg_quality, avg_ttft, avg_token_latency, memory_stats)
    """
    # Load task-specific metrics
    print(f"Loading task metrics for {task_path}")
    quality_module, perf_module = get_task_metrics(task_path)
    print(f"Loaded task metrics for {task_path}")
    
    # Load benchmark cases
    with open(os.path.join(task_path, 'benchmarks', 'test_cases.json'), 'r') as f:
        test_cases = json.load(f)['test_cases']
    
    quality_scores = []
    performance_metrics = []
    print(f"Running evaluation for {model_name} on {task_path}")
    
    # Run evaluation for each test case
    for case in test_cases[:1]:
        print(f"Running evaluation for {model_name} on {task_path} for case {case['id']}")
        # Measure performance
        perf_metrics = perf_module.measure_performance(
            model_name=model_name,
            messages=case['conversation']
        )
        performance_metrics.append(perf_metrics)
        print(f"Performance metrics for {model_name} on {task_path} for case {case['id']}: {perf_metrics}")
        
        # Get model response (non-streaming for quality evaluation)
        response = chat(
            model=model_name,
            messages=case['conversation'],
            stream=False
        )
        
        # Evaluate quality
        quality_metric = quality_module.evaluate_response_quality(
            conversation_history=case['conversation'],
            model_response=response.message.content,
            expected_output=case['expected_output']
        )
        quality_scores.append(quality_metric)
        print(f"Quality metrics for {model_name} on {task_path} for case {case['id']}: {quality_metric}")
    
    # Calculate average scores
    print(f"Calculating average scores for {model_name} on {task_path}")
    avg_quality = sum(score.score for score in quality_scores) / len(quality_scores)
    avg_ttft = sum(p.latency.time_to_first_token for p in performance_metrics) / len(performance_metrics)
    avg_token_latency = sum(p.latency.avg_inter_token_latency for p in performance_metrics) / len(performance_metrics)
    
    # Get memory stats from the last performance metrics (they should be the same for all runs)
    memory_stats = {
        "size_gb": performance_metrics[-1].memory.size_bytes / (1024*1024*1024),
        "vram_gb": performance_metrics[-1].memory.vram_bytes / (1024*1024*1024),
        "details": performance_metrics[-1].memory.details
    }
    
    return avg_quality, avg_ttft, avg_token_latency, memory_stats


def determine_model_tags(task_path: str, avg_quality: float, avg_ttft: float, 
                        avg_token_latency: float, memory_stats: dict) -> Tuple[list[str], Dict]:
    """
    Determine model tags based on evaluation metrics and comparison with baselines.
    Returns a tuple of (awarded_tags, updated_baselines).
    """
    tags = []
    baseline = load_baseline_metrics(task_path)
    updated_baseline = dict(baseline)  # Create a copy for potential updates
    
    # Quality threshold check (must pass this for any tag)
    QUALITY_THRESHOLD = 0.8
    if avg_quality >= QUALITY_THRESHOLD:
        # Check for speed-related tags
        if (avg_ttft < baseline["fastest"]["ttft"] and 
            avg_token_latency < baseline["fastest"]["token_latency"]):
            tags.append("fastest")
            updated_baseline["fastest"]["ttft"] = avg_ttft
            updated_baseline["fastest"]["token_latency"] = avg_token_latency
            
        # Check for size-related tags
        if (memory_stats['size_gb'] < baseline["smallest"]["size_gb"] and 
            memory_stats['vram_gb'] < baseline["smallest"]["vram_gb"]):
            tags.append("smallest")
            updated_baseline["smallest"]["size_gb"] = memory_stats['size_gb']
            updated_baseline["smallest"]["vram_gb"] = memory_stats['vram_gb']
            
        # Check for quality-focused tag
        if avg_quality > baseline["best-quality"]["quality"]:
            tags.append("best-quality")
            updated_baseline["best-quality"]["quality"] = avg_quality
    
    return tags, updated_baseline

def print_results(metrics: Tuple[float, float, float, dict], tags: list[str], baseline: Dict):
    """Print evaluation results in a formatted way."""
    avg_quality, avg_ttft, avg_token_latency, memory_stats = metrics
    
    print("\nEvaluation Results:")
    print(f"Average Quality Score: {avg_quality:.3f}")
    print(f"Average Time to First Token: {avg_ttft:.3f}s")
    print(f"Average Inter-token Latency: {avg_token_latency:.3f}s")
    print("\nMemory Usage:")
    print(f"Model Size: {memory_stats['size_gb']:.2f}GB")
    print(f"VRAM Usage: {memory_stats['vram_gb']:.2f}GB")
    print("\nModel Details:")
    print(f"Format: {memory_stats['details']['format']}")
    print(f"Family: {memory_stats['details']['family']}")
    print(f"Parameter Size: {memory_stats['details']['parameter_size']}")
    print(f"Quantization: {memory_stats['details']['quantization']}")
    
    print("\nBaseline Metrics:")
    print(f"Fastest - TTFT: {baseline['fastest']['ttft']:.3f}s, Token Latency: {baseline['fastest']['token_latency']:.3f}s")
    print(f"Smallest - Size: {baseline['smallest']['size_gb']:.2f}GB, VRAM: {baseline['smallest']['vram_gb']:.2f}GB")
    print(f"Best Quality Score: {baseline['best-quality']['quality']:.3f}")
    
    if tags:
        print("\nQualified Tags (Improvements over baseline):")
        for tag in tags:
            print(f"- {tag}")


def main():
    if len(sys.argv) != 3:
        print("Usage: evaluate_task.py <task_path> <model_name>")
        sys.exit(1)
        
    task_path = sys.argv[1]
    model_name = sys.argv[2]
    
    try:
        print(f"Evaluating {model_name} on {task_path}")
        metrics = evaluate_task(task_path, model_name)
        tags, new_baseline = determine_model_tags(task_path, *metrics)
        print_results(metrics, tags, new_baseline)
        
        # Only save new baseline metrics if we got any tags (meaning we had improvements)
        if tags:
            save_baseline_metrics(task_path, new_baseline)
            
            # Write tags to a file for GitHub Actions to use
            with open("model_tags.txt", "w") as f:
                f.write("\n".join(tags))
        
        # Exit based on quality threshold
        QUALITY_THRESHOLD = 0.8
        sys.exit(0 if metrics[0] >= QUALITY_THRESHOLD else 1)
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 