#!/usr/bin/env python3

import json
import sys
import os
from typing import Tuple
from pathlib import Path
import importlib.util
from ollama import chat


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
    for case in test_cases:
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


def print_results(metrics: Tuple[float, float, float, dict]):
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


def save_metrics(metrics: Tuple[float, float, float, dict], task_path: str, model_name: str) -> str:
    """Save metrics to a JSON file and return the file path."""
    avg_quality, avg_ttft, avg_token_latency, memory_stats = metrics
    
    metrics_data = {
        "task_path": task_path,
        "model_name": model_name,
        "quality_score": avg_quality,
        "ttft": avg_ttft,
        "token_latency": avg_token_latency,
        "memory_stats": memory_stats
    }
    
    # Save to a file in the task's evaluation directory
    metrics_file = Path(task_path) / "evaluation" / "latest_metrics.json"
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(metrics_file, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    
    return str(metrics_file)


def main():
    if len(sys.argv) != 3:
        print("Usage: evaluate_task.py <task_path> <model_name>")
        sys.exit(1)
        
    task_path = sys.argv[1]
    model_name = sys.argv[2]
    
    try:
        print(f"Evaluating {model_name} on {task_path}")
        metrics = evaluate_task(task_path, model_name)
        
        # Print human-readable results
        print_results(metrics)
        
        # Save metrics to file
        metrics_file = save_metrics(metrics, task_path, model_name)
        print(f"\nMetrics saved to: {metrics_file}")
        
        # Exit based on quality threshold
        QUALITY_THRESHOLD = 0.8
        sys.exit(0 if metrics[0] >= QUALITY_THRESHOLD else 1)
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 