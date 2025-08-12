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
        
        # Filename: timezone/cityname_landmark_weather_lowpoly
        filename = f"{timezone_folder}/{city['name']}_{city['landmark'].replace(' ', '_').lower()}_{weather['name']}_lowpoly"
        
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
        """지역별 배치 생성 실행"""
        
        # 설정 파일 로드
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {config_file}")
            return
        except json.JSONDecodeError:
            print(f"❌ Invalid configuration file format: {config_file}")
            return
        
        # 지역 확인
        if region_name not in config['regions']:
            print(f"❌ Region not found: {region_name}")
            print(f"Available regions: {list(config['regions'].keys())}")
            return
        
        region = config['regions'][region_name]
        cities = region['cities']
        weather_conditions = config['weather_conditions']
        
        # 날씨 필터 적용
        if weather_filter:
            weather_conditions = [w for w in weather_conditions if w['name'] in weather_filter]
        
        # 시간대별 통계 계산
        timezone_stats = {}
        for city in cities:
            tz = city['timezone']
            if tz not in timezone_stats:
                timezone_stats[tz] = []
            timezone_stats[tz].append(city['city'])
        
        # 배치 정보 출력
        total_images = len(cities) * len(weather_conditions)
        print(f"🚀 지역별 FLUX Krea 배치 생성 시작!")
        print(f"📍 지역: {region['name']} ({region['description']})")
        print(f"🏙️ 도시 수: {len(cities)}개")
        print(f"🌤️ 날씨 조건: {len(weather_conditions)}개")
        if weather_filter:
            print(f"🔍 날씨 필터: {weather_filter}")
        print(f"🖼️ 총 생성 이미지: {total_images}개")
        print(f"⏱️ 예상 소요시간: {total_images * 3}분")
        print()
        print("🕐 시간대별 도시 분포:")
        for tz, city_list in sorted(timezone_stats.items()):
            folder_name = self.normalize_timezone(tz)
            print(f"   {tz} ({folder_name}): {len(city_list)}개 도시")
            print(f"      -> {', '.join(city_list)}")
        print("="*60)
        
        success_count = 0
        failed_count = 0
        failed_images = []
        timezone_results = {}
        
        # 도시별 진행
        for city_idx, city in enumerate(cities, 1):
            timezone = city['timezone']
            if timezone not in timezone_results:
                timezone_results[timezone] = {'success': 0, 'failed': 0}
                
            print(f"\n📍 [{city_idx}/{len(cities)}] {city['city']}, {city['country']}")
            print(f"🏛️ {city['landmark']} ({city['timezone']})")
            print("-" * 40)
            
            # 날씨별 생성
            for weather_idx, weather in enumerate(weather_conditions, 1):
                print(f"[{weather_idx}/{len(weather_conditions)}] {weather['name']} 날씨")
                
                if self.generate_city_image(city, weather):
                    success_count += 1
                    timezone_results[timezone]['success'] += 1
                else:
                    failed_count += 1
                    timezone_results[timezone]['failed'] += 1
                    failed_images.append(f"{city['city']} ({timezone}) - {weather['name']}")
                
                # 서버 과부하 방지 딜레이
                time.sleep(1)
        
        # 결과 요약
        print("\n" + "="*60)
        print(f"🎉 {region['name']} 지역 배치 생성 완료!")
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {failed_count}개")
        print(f"📊 성공률: {(success_count/total_images)*100:.1f}%")
        
        print(f"\n🕐 시간대별 결과:")
        for tz in sorted(timezone_results.keys()):
            result = timezone_results[tz]
            folder_name = self.normalize_timezone(tz)
            total_tz = result['success'] + result['failed']
            success_rate = (result['success'] / total_tz * 100) if total_tz > 0 else 0
            print(f"   {tz} ({folder_name}): {result['success']}/{total_tz} ({success_rate:.1f}%)")
        
        if failed_images:
            print(f"\n❌ 실패한 이미지 목록:")
            for img in failed_images:
                print(f"   - {img}")
        
        print(f"\n📁 결과물 위치:")
        print(f"   ComfyUI/output/timezones/")
        for tz in sorted(timezone_results.keys()):
            folder_name = self.normalize_timezone(tz)
            print(f"   ├── {folder_name}/  ({tz})")
        
        print("="*60)
    
    def list_regions(self, config_file: str = "global_cities_config.json"):
        """사용 가능한 지역 목록 출력"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {config_file}")
            return
        
        print("🌍 사용 가능한 지역:")
        print("="*50)
        
        all_timezones = set()
        for region_key, region_data in config['regions'].items():
            cities_count = len(region_data['cities'])
            
            # 해당 지역의 시간대 통계
            region_timezones = {}
            for city in region_data['cities']:
                tz = city['timezone']
                if tz not in region_timezones:
                    region_timezones[tz] = 0
                region_timezones[tz] += 1
                all_timezones.add(tz)
            
            print(f"📍 {region_key}")
            print(f"   이름: {region_data['name']}")
            print(f"   설명: {region_data['description']}")
            print(f"   도시 수: {cities_count}개")
            print(f"   예상 이미지: {cities_count * 6}개")
            print(f"   시간대: {', '.join(sorted(region_timezones.keys()))}")
            print()
        
        print(f"🕐 전체 시간대 목록 ({len(all_timezones)}개):")
        for tz in sorted(all_timezones):
            folder_name = RegionalBatchGenerator("").normalize_timezone(tz)
            print(f"   {tz} -> {folder_name}/")

def main():
    parser = argparse.ArgumentParser(description='지역별 도시 랜드마크 이미지 배치 생성기 (시간대별 폴더)')
    parser.add_argument('--region', '-r', type=str, help='생성할 지역 이름')
    parser.add_argument('--list', '-l', action='store_true', help='사용 가능한 지역 목록 표시')
    parser.add_argument('--weather', '-w', nargs='+', help='특정 날씨만 생성 (예: sunny cloudy)')
    parser.add_argument('--config', '-c', default='global_cities_config.json', help='설정 파일 경로')
    parser.add_argument('--server', '-s', default='http://127.0.0.1:8000', help='ComfyUI 서버 URL')
    
    args = parser.parse_args()
    
    generator = RegionalBatchGenerator(args.server)
    
    if args.list:
        generator.list_regions(args.config)
        return
    
    if not args.region:
        print("❌ 지역을 지정해주세요. --list 옵션으로 사용 가능한 지역을 확인하세요.")
        return
    
    print("🎨 지역별 Low Poly 도시 랜드마크 이미지 생성기")
    print("FLUX Krea + Low Poly Joy LoRA 스타일 | 시간대별 폴더 구조")
    print("="*60)
    
    generator.generate_region_batch(args.region, args.config, args.weather)

if __name__ == "__main__":
    main()
