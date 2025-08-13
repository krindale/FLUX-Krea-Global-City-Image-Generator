from PIL import Image
import os
from typing import Optional, Tuple

class SimpleBackgroundRemover:
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    
    def remove_background_simple(self, image_path: str, output_path: str, 
                                tolerance: int = 50) -> bool:
        """Simple background removal using PIL only (no numpy/opencv needed)"""
        try:
            # Open image and convert to RGBA
            img = Image.open(image_path).convert('RGBA')
            width, height = img.size
            
            # Get corner pixel as background color
            corner_pixel = img.getpixel((0, 0))[:3]  # RGB only
            bg_r, bg_g, bg_b = corner_pixel
            
            print(f"Using background color: RGB{corner_pixel}")
            
            # Process each pixel
            pixels = img.load()
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    
                    # Calculate color difference
                    color_diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                    
                    # If pixel is similar to background, make it transparent
                    if color_diff <= tolerance:
                        pixels[x, y] = (r, g, b, 0)  # Set alpha to 0
            
            # Save as PNG
            img.save(output_path, 'PNG')
            print(f"✅ Background removed: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error removing background: {e}")
            return False
    
    def remove_background_edge_detection(self, image_path: str, output_path: str) -> bool:
        """Edge-based background removal using PIL only"""
        try:
            from PIL import ImageFilter
            
            # Open image
            img = Image.open(image_path).convert('RGBA')
            
            # Create a copy for processing
            gray_img = img.convert('L')  # Convert to grayscale
            
            # Apply edge detection filter
            edges = gray_img.filter(ImageFilter.FIND_EDGES)
            
            # Create mask from edges
            mask = Image.new('L', img.size, 0)
            
            # Process the image to create a better mask
            width, height = img.size
            edge_pixels = edges.load()
            mask_pixels = mask.load()
            
            # Create initial mask based on edges
            for y in range(height):
                for x in range(width):
                    if edge_pixels[x, y] > 30:  # Edge threshold
                        mask_pixels[x, y] = 255
            
            # Apply the mask to make background transparent
            img_pixels = img.load()
            corner_color = img.getpixel((0, 0))[:3]
            
            for y in range(height):
                for x in range(width):
                    r, g, b, a = img_pixels[x, y]
                    
                    # Check if pixel is similar to corner color
                    color_diff = abs(r - corner_color[0]) + abs(g - corner_color[1]) + abs(b - corner_color[2])
                    
                    # If it's background color and not near an edge, make transparent
                    if color_diff <= 60 and mask_pixels[x, y] < 100:
                        img_pixels[x, y] = (r, g, b, 0)
            
            img.save(output_path, 'PNG')
            print(f"✅ Edge-based background removed: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error in edge-based removal: {e}")
            return False
    
    def process_images(self, input_dir: str, output_dir: str = "simple_transparent", 
                      method: str = "simple") -> int:
        """Process all images in directory"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        processed_count = 0
        
        # Get all image files
        image_files = []
        for ext in self.supported_formats:
            image_files.extend([f for f in os.listdir(input_dir) if f.lower().endswith(ext)])
        
        if not image_files:
            print("❌ No supported image files found!")
            return 0
        
        print(f"Found {len(image_files)} images to process...")
        
        for filename in image_files:
            input_path = os.path.join(input_dir, filename)
            name_without_ext = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{name_without_ext}_transparent.png")
            
            print(f"\n🔄 Processing: {filename}")
            
            success = False
            if method == "simple":
                success = self.remove_background_simple(input_path, output_path)
            elif method == "edge":
                success = self.remove_background_edge_detection(input_path, output_path)
            elif method == "auto":
                # Try both methods
                success = self.remove_background_simple(input_path, output_path)
                if not success:
                    success = self.remove_background_edge_detection(input_path, output_path)
            
            if success:
                processed_count += 1
                print(f"  ✅ Success: {output_path}")
            else:
                print(f"  ❌ Failed: {filename}")
        
        return processed_count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple background remover (PIL only)")
    parser.add_argument("--input", default=".", help="Input directory")
    parser.add_argument("--output", default="simple_transparent", help="Output directory")
    parser.add_argument("--method", choices=["simple", "edge", "auto"], default="auto")
    parser.add_argument("--single", help="Process single image")
    
    args = parser.parse_args()
    
    remover = SimpleBackgroundRemover()
    
    if args.single:
        if not os.path.exists(args.single):
            print(f"❌ File not found: {args.single}")
            return
        
        filename = os.path.basename(args.single)
        name_without_ext = os.path.splitext(filename)[0]
        output_path = f"{name_without_ext}_simple_transparent.png"
        
        print(f"Processing: {args.single}")
        
        if args.method == "auto":
            success = remover.remove_background_simple(args.single, output_path)
            if not success:
                success = remover.remove_background_edge_detection(args.single, output_path)
        elif args.method == "simple":
            success = remover.remove_background_simple(args.single, output_path)
        else:
            success = remover.remove_background_edge_detection(args.single, output_path)
            
        if success:
            print("✅ Background removed!")
        else:
            print("❌ Failed to remove background")
    else:
        processed = remover.process_images(args.input, args.output, args.method)
        print(f"\n=== Complete ===")
        print(f"Processed: {processed} images")
        print(f"Output: {args.output}")

if __name__ == "__main__":
    main()
