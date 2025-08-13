#!/usr/bin/env python3
"""
Regional Fallback Image Generator for ComfyUI Batch System
Generates representative images for regions not covered by the main 47 cities
"""

import os
import sys
import json
import requests
import time
import argparse
from pathlib import Path
import uuid

def load_config(config_path="regional_fallback_config.json"):
    """Load regional fallback configuration"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        sys.exit(1)

def normalize_region_name(region_name):
    """Convert region name to filesystem-safe format"""
    return region_name.lower().replace(' ', '_').replace('/', '_')

def check_comfyui_server(server_url):
    """Check if ComfyUI server is running"""
    try:
        response = requests.get(f"{server_url}/system_stats", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def generate_workflow(config, region_data, weather_condition):
    """Generate ComfyUI workflow for regional fallback image (matching existing system)"""
    lora_keywords = config["lora_keywords"]["activation"]
    landmark = region_data["representative_landmark"]
    weather_desc = weather_condition["condition"]
    
    positive_prompt = config["prompts"]["positive_template"].format(
        lora_keywords=lora_keywords,
        landmark=landmark,
        weather_condition=weather_desc
    )
    
    seed = int(time.time() * 1000) % 1000000
    # 파일명을 지역_날씨.png 형식으로 변경 (all lowercase)
    region_name_clean = normalize_region_name(region_data['name'].lower())
    weather_name = weather_condition['name'].lower()
    filename = f"regional_fallback/{region_name_clean}_{weather_name}"
    
    # Use the same workflow structure as regional_batch_generator.py
    workflow = {
        "39": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader"
        },
        "8": {
            "inputs": {
                "samples": ["31", 0],
                "vae": ["39", 0]
            },
            "class_type": "VAEDecode"
        },
        "27": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptySD3LatentImage"
        },
        "52": {
            "inputs": {
                "model": ["38", 0],
                "clip": ["40", 0],
                "lora_name": "noc-lwply.safetensors",
                "strength_model": 1.0,
                "strength_clip": 1.0
            },
            "class_type": "LoraLoader"
        },
        "38": {
            "inputs": {
                "unet_name": "flux1-krea-dev_fp8_scaled.safetensors",
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader"
        },
        "40": {
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp16.safetensors",
                "type": "flux",
                "device": "cpu"
            },
            "class_type": "DualCLIPLoader"
        },
        "9": {
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": filename
            },
            "class_type": "SaveImage"
        },
        "53": {
            "inputs": {
                "clip": ["40", 0],
                "text": config["prompts"]["negative_template"]
            },
            "class_type": "CLIPTextEncode"
        },
        "31": {
            "inputs": {
                "model": ["52", 0],
                "positive": ["45", 0],
                "negative": ["53", 0],
                "latent_image": ["27", 0],
                "seed": seed,
                "steps": 35,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            },
            "class_type": "KSampler"
        },
        "45": {
            "inputs": {
                "clip": ["52", 1],
                "text": positive_prompt
            },
            "class_type": "CLIPTextEncode"
        }
    }
    
    return workflow

def queue_prompt(server_url, workflow):
    """Queue a prompt to ComfyUI server"""
    prompt_data = {
        "prompt": workflow,
        "client_id": str(uuid.uuid4())
    }
    
    try:
        response = requests.post(f"{server_url}/prompt", json=prompt_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to queue prompt: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def wait_for_completion(server_url, prompt_id, timeout_seconds):
    """Wait for image generation to complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(f"{server_url}/history/{prompt_id}", timeout=5)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    return True
        except requests.RequestException:
            pass
        
        time.sleep(2)
    
    return False

def generate_regional_images(config, regions=None, weather_conditions=None, priority_filter=None):
    """Generate images for specified regions and weather conditions"""
    server_url = config["settings"]["server_url"]
    timeout_seconds = config["settings"]["timeout_seconds"]
    
    # Check ComfyUI server
    if not check_comfyui_server(server_url):
        print(f"❌ ComfyUI server not accessible at {server_url}")
        return False
    
    # Filter regions by priority if specified
    regional_fallbacks = config["regional_fallbacks"]
    if priority_filter:
        regional_fallbacks = {
            name: data for name, data in regional_fallbacks.items()
            if data.get("priority", 3) in priority_filter
        }
    
    # Filter regions if specified
    if regions:
        regional_fallbacks = {
            name: data for name, data in regional_fallbacks.items()
            if name in regions
        }
    
    # Filter weather conditions if specified
    weather_conditions_list = config["weather_conditions"]
    if weather_conditions:
        weather_conditions_list = [
            w for w in weather_conditions_list
            if w["name"] in weather_conditions
        ]
    
    total_images = len(regional_fallbacks) * len(weather_conditions_list)
    
    # Batch information output (matching existing style)
    print(f"🚀 Regional FLUX Krea fallback image generation started!")
    print(f"📍 Regions: {len(regional_fallbacks)}")
    print(f"🌤️ Weather conditions: {len(weather_conditions_list)}")
    print(f"🖼️ Total images to generate: {total_images}")
    print(f"⏱️ Estimated time: {total_images * 3} minutes")
    print()
    print("🌍 Regional representative landmarks:")
    for name, data in regional_fallbacks.items():
        priority_text = {1: "High", 2: "Medium", 3: "Low"}.get(data.get("priority", 3), "Unknown")
        print(f"   {data['name']} (Priority: {priority_text})")
        print(f"      -> {data['representative_landmark']}")
    print("="*60)
    
    success_count = 0
    failed_count = 0
    failed_images = []
    priority_results = {}
    
    # Process regions
    for region_idx, (region_name, region_data) in enumerate(regional_fallbacks.items(), 1):
        priority = region_data.get("priority", 3)
        if priority not in priority_results:
            priority_results[priority] = {'success': 0, 'failed': 0}
            
        print(f"\n📍 [{region_idx}/{len(regional_fallbacks)}] {region_data['name']}")
        print(f"🏛️ {region_data['representative_landmark']} (Priority: {priority})")
        print(f"🌍 Coverage area: {region_data['coverage_area']}")
        print("-" * 40)
        
        # Generate by weather conditions
        for weather_idx, weather_condition in enumerate(weather_conditions_list, 1):
            print(f"[{weather_idx}/{len(weather_conditions_list)}] {weather_condition['name']} weather")
            
            # Generate workflow
            workflow = generate_workflow(config, region_data, weather_condition)
            
            # Queue prompt
            result = queue_prompt(server_url, workflow)
            if not result:
                print(f"    ❌ Failed to queue prompt")
                failed_count += 1
                priority_results[priority]['failed'] += 1
                failed_images.append(f"{region_data['name']} - {weather_condition['name']}")
                continue
            
            prompt_id = result["prompt_id"]
            print(f"    🔄 Generating... (ID: {prompt_id})")
            
            # Wait for completion
            if wait_for_completion(server_url, prompt_id, timeout_seconds):
                print(f"    ✅ Generation completed")
                success_count += 1
                priority_results[priority]['success'] += 1
            else:
                print(f"    ⏰ Timeout ({timeout_seconds}s)")
                failed_count += 1
                priority_results[priority]['failed'] += 1
                failed_images.append(f"{region_data['name']} - {weather_condition['name']}")
            
            # Server overload prevention delay
            time.sleep(1)
    
    # Results summary (matching existing style)
    print("\n" + "="*60)
    print(f"🎉 Regional fallback image generation completed!")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Success rate: {(success_count/total_images)*100:.1f}%")
    
    print(f"\n📊 Results by priority:")
    for priority in sorted(priority_results.keys()):
        result = priority_results[priority]
        priority_text = {1: "High", 2: "Medium", 3: "Low"}.get(priority, "Unknown")
        total_priority = result['success'] + result['failed']
        success_rate = (result['success'] / total_priority * 100) if total_priority > 0 else 0
        print(f"   Priority {priority} ({priority_text}): {result['success']}/{total_priority} ({success_rate:.1f}%)")
    
    if failed_images:
        print(f"\n❌ Failed images:")
        for failed in failed_images:
            print(f"   - {failed}")
    
    print(f"\n📁 Results saved to: ComfyUI/output/regional_fallback/")
    
    return success_count == total_images

def list_regions(config):
    """List all available regions with their priorities"""
    print("\n📍 Available Regional Fallbacks:")
    
    # Group by priority
    by_priority = {}
    for name, data in config["regional_fallbacks"].items():
        priority = data.get("priority", 3)
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append((name, data))
    
    for priority in sorted(by_priority.keys()):
        priority_name = {1: "High", 2: "Medium", 3: "Low"}.get(priority, f"Priority {priority}")
        print(f"\n  🔸 {priority_name} Priority:")
        
        for name, data in by_priority[priority]:
            population = data.get("population", "N/A")
            print(f"    • {name}: {data['name']} ({population})")
            print(f"      📍 {data['representative_landmark']}")
            print(f"      🌍 {data['coverage_area']}")

def main():
    parser = argparse.ArgumentParser(description="Generate regional fallback images for weather app")
    parser.add_argument("--config", default="regional_fallback_config.json", help="Configuration file path")
    parser.add_argument("--regions", nargs="+", help="Specific regions to generate (default: all)")
    parser.add_argument("--weather", nargs="+", help="Specific weather conditions (default: all)")
    parser.add_argument("--priority", nargs="+", type=int, choices=[1, 2, 3], help="Filter by priority levels")
    parser.add_argument("--list", action="store_true", help="List available regions and exit")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # List regions if requested
    if args.list:
        list_regions(config)
        return
    
    # Generate images
    success = generate_regional_images(
        config,
        regions=args.regions,
        weather_conditions=args.weather,
        priority_filter=args.priority
    )
    
    if success:
        print("\n🎉 All images generated successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Some images failed to generate")
        sys.exit(1)

if __name__ == "__main__":
    main()