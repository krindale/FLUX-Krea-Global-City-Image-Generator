import json
import requests
import time
import os
import argparse
from typing import List, Dict

class RegionalBatchGenerator:
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.server_url = server_url
        self.client_id = "regional_cities_generator"
        
    def normalize_timezone(self, timezone: str) -> str:
        """Convert timezone to folder-safe format"""
        # UTC+8 -> utc_plus_8, UTC-5 -> utc_minus_5, UTC+5:30 -> utc_plus_5_30
        normalized = timezone.lower().replace("utc", "utc_")
        normalized = normalized.replace("+", "plus_")
        normalized = normalized.replace("-", "minus_")
        normalized = normalized.replace(":", "_")
        return normalized
        
    def create_flux_krea_workflow(self, positive_prompt: str, negative_prompt: str, filename: str, seed: int = None) -> Dict:
        """Generate FLUX Krea workflow (with LoRA)"""
        if seed is None:
            seed = int(time.time() * 1000) % 1000000
            
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
                    "filename_prefix": f"timezones/{filename}"
                },
                "class_type": "SaveImage"
            },
            "53": {
                "inputs": {
                    "clip": ["40", 0],
                    "text": negative_prompt
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
    
    def queue_prompt(self, workflow: Dict) -> str:
        """Send workflow to ComfyUI server"""
        prompt = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        
        try:
            response = requests.post(f"{self.server_url}/prompt", json=prompt)
            response.raise_for_status()
            return response.json()["prompt_id"]
        except Exception as e:
            print(f"Failed to send prompt: {e}")
            return None
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> bool:
        """Wait for image generation completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.server_url}/history/{prompt_id}")
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history:
                        print(f"✅ Image generation completed: {prompt_id}")
                        return True
                
                time.sleep(2)
            except Exception as e:
                print(f"Error checking status: {e}")
                time.sleep(2)
        
        print(f"⏰ Timeout: {prompt_id}")
        return False
    
    def generate_city_image(self, city: Dict, weather: Dict) -> bool:
        """Generate individual city image"""
        
        # LoRA activation keywords
        lora_keywords = "lo-ply_, noc-lwply,"
        
        # Base prompt template
        base_template = "{lora_keywords} Stylized {landmark} illustration in low poly art style, geometric polygonal shapes, faceted surfaces, Low polygon count design with angular forms and triangular facets, polygonal clouds, angular horizon line, crystalline atmosphere. Vector graphics feel, clean minimalist composition, perfect for weather app background. Modern low poly aesthetic with crisp geometric edges throughout entire scene, professional UI artwork."
        
        # Timezone-based folder structure
        timezone_folder = self.normalize_timezone(city['timezone'])
        
        # Weather condition
        weather_desc = f", {weather['condition']}, {weather['mood']}"
        
        # Filename: timezone/cityname_weather.png (all lowercase)
        filename = f"{timezone_folder}/{city['name'].lower()}_{weather['name'].lower()}"
        
        # Final positive prompt
        positive_prompt = base_template.format(
            lora_keywords=lora_keywords,
            landmark=f"{city['landmark']}, {city['landmark_description']}"
        ) + weather_desc + ", low poly style background"
        
        # Negative prompt
        negative_prompt = "blur, haze, soft focus, atmospheric perspective, depth of field, bokeh, motion blur, fog, mist, dreamy, soft lighting, realistic raindrops, photographic snowflakes, natural water drops, organic snow crystals, realistic weather effects, smooth rounded shapes, large raindrops, oversized snowflakes, big weather elements, giant precipitation, huge crystals, massive particles, recognizable raindrop shapes, distinct snowflake patterns, teardrop forms, star-shaped snowflakes, detailed precipitation, complex weather shapes, medium sized particles, visible crystal shapes, prominent weather elements, noticeable precipitation"
        
        print(f"\n🎨 Generating: {city['city']}, {city['country']}")
        print(f"🏛️ Landmark: {city['landmark']}")
        print(f"🌤️ Weather: {weather['name']}")
        print(f"🕐 Timezone: {city['timezone']} -> {timezone_folder}")
        print(f"💾 Filename: {filename}")
        
        # Generate workflow
        workflow = self.create_flux_krea_workflow(positive_prompt, negative_prompt, filename)
        
        # Send prompt
        prompt_id = self.queue_prompt(workflow)
        if not prompt_id:
            print(f"❌ Prompt sending failed: {city['city']}")
            return False
        
        # Wait for completion
        success = self.wait_for_completion(prompt_id)
        if success:
            print(f"✅ Completed: {city['city']} - {weather['name']} -> {timezone_folder}")
        else:
            print(f"❌ Failed: {city['city']} - {weather['name']}")
        
        return success
    
    def generate_region_batch(self, region_name: str, config_file: str = "global_cities_config.json", weather_filter: List[str] = None):
        """Execute regional batch generation"""
        
        # Load configuration file
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {config_file}")
            return
        except json.JSONDecodeError:
            print(f"❌ Invalid configuration file format: {config_file}")
            return
        
        # Check region
        if region_name not in config['regions']:
            print(f"❌ Region not found: {region_name}")
            print(f"Available regions: {list(config['regions'].keys())}")
            return
        
        region = config['regions'][region_name]
        cities = region['cities']
        weather_conditions = config['weather_conditions']
        
        # Apply weather filter
        if weather_filter:
            weather_conditions = [w for w in weather_conditions if w['name'] in weather_filter]
        
        # Calculate timezone statistics
        timezone_stats = {}
        for city in cities:
            tz = city['timezone']
            if tz not in timezone_stats:
                timezone_stats[tz] = []
            timezone_stats[tz].append(city['city'])
        
        # Output batch information
        total_images = len(cities) * len(weather_conditions)
        print(f"🚀 Regional FLUX Krea batch generation started!")
        print(f"📍 Region: {region['name']} ({region['description']})")
        print(f"🏙️ Cities: {len(cities)}")
        print(f"🌤️ Weather conditions: {len(weather_conditions)}")
        if weather_filter:
            print(f"🔍 Weather filter: {weather_filter}")
        print(f"🖼️ Total images to generate: {total_images}")
        print(f"⏱️ Estimated time: {total_images * 3} minutes")
        print()
        print("🕐 Timezone distribution:")
        for tz, city_list in sorted(timezone_stats.items()):
            folder_name = self.normalize_timezone(tz)
            print(f"   {tz} ({folder_name}): {len(city_list)} cities")
            print(f"      -> {', '.join(city_list)}")
        print("="*60)
        
        success_count = 0
        failed_count = 0
        failed_images = []
        timezone_results = {}
        
        # Process by city
        for city_idx, city in enumerate(cities, 1):
            timezone = city['timezone']
            if timezone not in timezone_results:
                timezone_results[timezone] = {'success': 0, 'failed': 0}
                
            print(f"\n📍 [{city_idx}/{len(cities)}] {city['city']}, {city['country']}")
            print(f"🏛️ {city['landmark']} ({city['timezone']})")
            print("-" * 40)
            
            # Generate by weather
            for weather_idx, weather in enumerate(weather_conditions, 1):
                print(f"[{weather_idx}/{len(weather_conditions)}] {weather['name']} weather")
                
                if self.generate_city_image(city, weather):
                    success_count += 1
                    timezone_results[timezone]['success'] += 1
                else:
                    failed_count += 1
                    timezone_results[timezone]['failed'] += 1
                    failed_images.append(f"{city['city']} ({timezone}) - {weather['name']}")
                
                # Server overload prevention delay
                time.sleep(1)
        
        # Results summary
        print("\n" + "="*60)
        print(f"🎉 {region['name']} regional batch generation completed!")
        print(f"✅ Success: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📊 Success rate: {(success_count/total_images)*100:.1f}%")
        
        print(f"\n🕐 Results by timezone:")
        for tz in sorted(timezone_results.keys()):
            result = timezone_results[tz]
            folder_name = self.normalize_timezone(tz)
            total_tz = result['success'] + result['failed']
            success_rate = (result['success'] / total_tz * 100) if total_tz > 0 else 0
            print(f"   {tz} ({folder_name}): {result['success']}/{total_tz} ({success_rate:.1f}%)")
        
        if failed_images:
            print(f"\n❌ Failed image list:")
            for failed in failed_images:
                print(f"   - {failed}")
        
        print(f"\n📁 Results location:")
        print(f"   ComfyUI/output/timezones/")
        for tz in sorted(timezone_results.keys()):
            folder_name = self.normalize_timezone(tz)
            print(f"   -> {folder_name}/")

def list_available_regions(config_file: str = "global_cities_config.json"):
    """Output available region list"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        return
    except json.JSONDecodeError:
        print(f"❌ Invalid configuration file format: {config_file}")
        return

    print("🌍 Available regions:")
    
    all_timezones = set()
    
    for region_key, region_data in config['regions'].items():
        cities_count = len(region_data['cities'])
        
        # Timezone statistics for this region
        region_timezones = {}
        for city in region_data['cities']:
            tz = city['timezone']
            all_timezones.add(tz)
            if tz not in region_timezones:
                region_timezones[tz] = 0
            region_timezones[tz] += 1
        
        print(f"\n🌍 {region_key}")
        print(f"   Name: {region_data['name']}")
        print(f"   Description: {region_data['description']}")
        print(f"   Cities: {cities_count}")
        print(f"   Expected images: {cities_count * 6}")
        print(f"   Timezones: {', '.join(sorted(region_timezones.keys()))}")
    
    print(f"\n🕐 All timezone list ({len(all_timezones)}):")
    for tz in sorted(all_timezones):
        print(f"   {tz}")

def main():
    parser = argparse.ArgumentParser(description='Regional city landmark image batch generator (timezone-based folders)')
    parser.add_argument('--region', '-r', type=str, help='Region name to generate')
    parser.add_argument('--list', '-l', action='store_true', help='Show available region list')
    parser.add_argument('--weather', '-w', nargs='+', help='Generate specific weather only (e.g. sunny cloudy)')
    parser.add_argument('--config', '-c', default='global_cities_config.json', help='Configuration file path')
    parser.add_argument('--server', '-s', default='http://127.0.0.1:8000', help='ComfyUI server URL')
    
    args = parser.parse_args()
    
    if args.list:
        list_available_regions(args.config)
        return
    
    if not args.region:
        print("❌ Please specify a region. Use --list option to check available regions.")
        return
    
    print("🎨 Regional Low Poly City Landmark Image Generator")
    print("FLUX Krea + Low Poly Joy LoRA Style | Timezone-based Folder Structure")
    print("="*70)
    
    generator = RegionalBatchGenerator(args.server)
    generator.generate_region_batch(args.region, args.config, args.weather)

if __name__ == "__main__":
    main()