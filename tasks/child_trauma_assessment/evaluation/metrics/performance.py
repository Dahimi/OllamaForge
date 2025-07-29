import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from ollama import chat, ps
from datetime import datetime


@dataclass
class LatencyMetrics:
    time_to_first_token: float  # seconds
    inter_token_latencies: List[float]  # list of latencies between tokens
    avg_inter_token_latency: float
    total_response_time: float
    
    
@dataclass
class MemoryMetrics:
    size_bytes: int  # Total model size in bytes
    vram_bytes: int  # VRAM usage in bytes
    details: Dict    # Additional model details


@dataclass
class PerformanceMetrics:
    latency: LatencyMetrics
    memory: MemoryMetrics


def get_model_memory_stats(model_name: str) -> MemoryMetrics:
    """
    Get memory statistics for a specific model using ollama.ps()
    """
    processes = ps()
    for model in processes.models:
        if model_name in model.name:
            return MemoryMetrics(
                size_bytes=model.size,
                vram_bytes=model.size_vram,
                details={
                    "format": model.details.format,
                    "family": model.details.family,
                    "parameter_size": model.details.parameter_size,
                    "quantization": model.details.quantization_level
                }
            )
    raise ValueError(f"Model {model_name} not found in running processes")


def measure_performance(model_name: str, messages: List[Dict]) -> PerformanceMetrics:
    """
    Measures performance metrics while running model inference.
    
    Args:
        model_name: Name of the Ollama model
        messages: List of conversation messages
    
    Returns:
        PerformanceMetrics containing latency and memory measurements
    """
    inter_token_times = []
    last_token_time = None
    
    # Start timing
    start_time = time.time()
    first_token_received = False
    time_to_first_token = None
    
    # Start streaming response
    stream = chat(
        model=model_name,
        messages=messages,
        stream=True,
    )
    
    # Process stream and collect metrics
    for chunk in stream:
        current_time = time.time()
        
        # First token timing
        if not first_token_received:
            time_to_first_token = current_time - start_time
            first_token_received = True
        
        # Inter-token latency
        if last_token_time is not None:
            inter_token_times.append(current_time - last_token_time)
        last_token_time = current_time
    
    total_time = time.time() - start_time
    
    # Get memory metrics
    memory_metrics = get_model_memory_stats(model_name)
    
    # Calculate latency metrics
    latency_metrics = LatencyMetrics(
        time_to_first_token=time_to_first_token,
        inter_token_latencies=inter_token_times,
        avg_inter_token_latency=sum(inter_token_times) / len(inter_token_times) if inter_token_times else 0,
        total_response_time=total_time
    )
    
    return PerformanceMetrics(
        latency=latency_metrics,
        memory=memory_metrics
    )


def format_performance_report(metrics: PerformanceMetrics) -> str:
    """
    Formats performance metrics into a readable report.
    """
    report = f"""Performance Metrics Report:

Latency:
--------
Time to First Token: {metrics.latency.time_to_first_token:.3f}s
Average Inter-token Latency: {metrics.latency.avg_inter_token_latency:.3f}s
Total Response Time: {metrics.latency.total_response_time:.3f}s

Memory Usage:
------------
Model Size: {metrics.memory.size_bytes / (1024*1024*1024):.2f}GB
VRAM Usage: {metrics.memory.vram_bytes / (1024*1024*1024):.2f}GB

Model Details:
-------------
Format: {metrics.memory.details["format"]}
Family: {metrics.memory.details["family"]}
Parameter Size: {metrics.memory.details["parameter_size"]}
Quantization: {metrics.memory.details["quantization"]}
"""
    return report 