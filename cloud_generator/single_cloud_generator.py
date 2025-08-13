import json
import requests
import time
import os
import argparse
from typing import List, Dict, Tuple

class SingleCloudGenerator:
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.server_url = server_url
        self.client_id = "single_cloud_generator"
        
    def create_cloud_workflow(self, size: Tuple[int, int], positive_prompt: str, 
                            negative_prompt: str, filename: str, seed: int = None) -> Dict:
        """Generate single complete cloud workflow with transparent background"""
        if seed is None:
            seed = int(time.time() * 1000) % 1000000
            
        width, height = size
        
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
                    "width": width,
                    "height": height,
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
                    "filename_prefix": f"single_clouds/{filename}"
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
                    "cfg": 3.5,
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

    def generate_cloud_prompts(self, image_style: str) -> Dict[str, str]:
        """Generate prompts for single complete clouds based on image style"""
        
        cloud_configs = {
            "blue_sky_mountain": {
                "positive": "lo-ply_, noc-lwply, single complete white cloud, full cloud visible, transparent background, geometric low poly style, angular cloud formation, clean edges, centered composition, complete cloud shape, no cropping, isolated cloud, faceted white surfaces",
                "negative": "multiple clouds, cropped cloud, partial cloud, cut off edges, solid background, complex details, realistic clouds, soft edges, background elements, ground, mountains, buildings, incomplete shape"
            },
            
            "sunset_cityscape": {
                "positive": "lo-ply_, noc-lwply, single complete sunset cloud, full cloud visible, transparent background, geometric low poly style, orange pink purple colors, angular formation, clean edges, centered composition, complete cloud shape, no cropping, isolated cloud, warm colored faceted surfaces",
                "negative": "multiple clouds, cropped cloud, partial cloud, cut off edges, solid background, complex details, realistic clouds, soft edges, background elements, ground, mountains, buildings, city, incomplete shape"
            },
            
            "overcast_gray": {
                "positive": "lo-ply_, noc-lwply, single complete gray cloud, full cloud visible, transparent background, geometric low poly style, gray tones, angular formation, clean edges, centered composition, complete cloud shape, no cropping, isolated cloud, muted gray faceted surfaces",
                "negative": "multiple clouds, cropped cloud, partial cloud, cut off edges, solid background, complex details, realistic clouds, soft edges, background elements, ground, mountains, buildings, incomplete shape"
            },
            
            "fantasy_castle": {
                "positive": "lo-ply_, noc-lwply, single complete fantasy cloud, full cloud visible, transparent background, geometric low poly style, light blue gray white colors, magical atmosphere, angular formation, clean edges, centered composition, complete cloud shape, no cropping, isolated cloud, ethereal faceted surfaces, dreamy tones",
                "negative": "multiple clouds, cropped cloud, partial cloud, cut off edges, solid background, complex details, realistic clouds, soft edges, background elements, ground, mountains, buildings, dark colors, black clouds, incomplete shape"
            },
            
            "mystical_blue": {
                "positive": "lo-ply_, noc-lwply, single complete mystical cloud, full cloud visible, transparent background, geometric low poly style, soft blue silver white colors, enchanted atmosphere, angular formation, clean edges, centered composition, complete cloud shape, no cropping, isolated cloud, luminous faceted surfaces, fairy tale mood",
                "negative": "multiple clouds, cropped cloud, partial cloud, cut off edges, solid background, complex details, realistic clouds, soft edges, background elements, ground, mountains, buildings, dark colors, black clouds, incomplete shape"
            }
        }
        
        return cloud_configs.get(image_style, cloud_configs["blue_sky_mountain"])

    def get_cloud_size(self, image_style: str) -> Tuple[int, int]:
        """Get optimal size for complete cloud that fits well in 1024x1024 images"""
        # Sizes designed to ensure complete cloud visibility with margin
        sizes = {
            "blue_sky_mountain": (400, 300),    # Medium size for clear sky
            "sunset_cityscape": (500, 350),     # Larger for dramatic effect
            "overcast_gray": (450, 320),        # Medium-large for coverage
            "fantasy_castle": (480, 340),       # Medium-large for magical effect
            "mystical_blue": (420, 310)         # Medium size for ethereal effect
        }
        return sizes.get(image_style, (400, 300))

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
                        print(f"✅ Cloud generation completed: {prompt_id}")
                        return True
                
                time.sleep(2)
            except Exception as e:
                print(f"Error checking status: {e}")
                time.sleep(2)
        
        print(f"⏰ Timeout: {prompt_id}")
        return False

    def generate_single_cloud(self, image_style: str, output_dir: str = "single_clouds"):
        """Generate one complete cloud for an image style"""
        
        print(f"Generating single complete cloud for {image_style} style...")
        
        # Get size and prompts for this style
        size = self.get_cloud_size(image_style)
        prompts = self.generate_cloud_prompts(image_style)
        
        filename = f"{image_style}_complete_cloud"
        
        print(f"Generating {filename} (size: {size[0]}x{size[1]})...")
        print(f"Cloud will be: Complete, centered, no cropping, transparent background")
        
        workflow = self.create_cloud_workflow(
            size=size,
            positive_prompt=prompts["positive"],
            negative_prompt=prompts["negative"],
            filename=filename
        )
        
        prompt_id = self.queue_prompt(workflow)
        if prompt_id:
            if self.wait_for_completion(prompt_id):
                print(f"✓ Successfully generated complete cloud: {filename}")
                return True
            else:
                print(f"✗ Failed to generate {filename}")
                return False
        else:
            print(f"✗ Failed to queue {filename}")
            return False

    def generate_all_single_clouds(self, output_dir: str = "single_clouds"):
        """Generate one complete cloud for each image style"""
        
        styles = ["blue_sky_mountain", "sunset_cityscape", "overcast_gray", "fantasy_castle", "mystical_blue"]
        success_count = 0
        
        print("=== Generating Single Complete Clouds ===")
        print("Each cloud will be:")
        print("• One complete cloud per image")
        print("• Fully visible (no cropping)")
        print("• Transparent background")
        print("• Optimally sized for 1024x1024 images")
        print()
        
        for style in styles:
            print(f"\n--- Processing {style} ---")
            if self.generate_single_cloud(style, output_dir):
                success_count += 1
                print(f"✅ {style}: SUCCESS")
            else:
                print(f"❌ {style}: FAILED")
            
            # Small delay between generations
            time.sleep(2)
        
        print(f"\n=== Generation Complete ===")
        print(f"Successfully generated: {success_count}/{len(styles)} clouds")
        print(f"Output directory: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Generate single complete clouds for low-poly images")
    parser.add_argument("--style", 
                       choices=["blue_sky_mountain", "sunset_cityscape", "overcast_gray", "fantasy_castle", "mystical_blue", "all"],
                       default="all",
                       help="Image style to generate cloud for")
    parser.add_argument("--output", default="single_clouds", help="Output directory")
    parser.add_argument("--server", default="http://127.0.0.1:8000", help="ComfyUI server URL")
    
    args = parser.parse_args()
    
    generator = SingleCloudGenerator(args.server)
    
    if args.style == "all":
        generator.generate_all_single_clouds(args.output)
    else:
        generator.generate_single_cloud(args.style, args.output)
    
    print("Single cloud generation complete!")

if __name__ == "__main__":
    main()
