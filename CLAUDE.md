# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLUX Krea Global City Image Generator is a ComfyUI-based batch system that generates low-poly style landmark images for 47 major cities across 6 weather conditions. The system outputs timezone-organized images suitable for Flutter app development.

## Key Commands

### Main Operations
- **Run main interface**: `.\easy_batch_generator.bat`
- **Regional generation**: `python regional_batch_generator.py --region <region_name> --config global_cities_config.json`
- **Individual city**: `python create_single_config.py <city_name>`
- **Weather-specific**: Add `--weather <conditions>` to regional command
- **List regions**: `python regional_batch_generator.py --list --config global_cities_config.json`

### Development Commands
- **Test configuration**: Generate single city first to verify ComfyUI integration
- **Clear outputs**: Delete `ComfyUI/output/timezones/` folder manually or via batch menu

## Architecture

### Core Components
1. **easy_batch_generator.bat** - Main Windows batch interface with 11-option menu system
2. **regional_batch_generator.py** - Python engine that interfaces with ComfyUI API
3. **global_cities_config.json** - Master configuration with 47 cities across 5 regions
4. **create_single_config.py** - Utility to extract single city configs for testing

### System Dependencies
- **ComfyUI Server**: Must be running on `http://127.0.0.1:8000`
- **Required Models**: 
  - `flux1-krea-dev_fp8_scaled.safetensors` (UNET)
  - `clip_l.safetensors`, `t5xxl_fp16.safetensors` (CLIP)
  - `ae.safetensors` (VAE)
  - `low-poly-joy.safetensors` (LoRA)

### Data Structure
- **5 Regions**: asia_pacific, europe, north_america, middle_east_africa, south_america  
- **47 Cities**: Each with name, timezone, landmark, coordinates
- **6 Weather Types**: sunny, cloudy, rainy, snowy, sunset, foggy
- **Output Organization**: `ComfyUI/output/timezones/utc_plus_X/` structure

### Image Generation Pipeline
1. Batch script → Python generator → ComfyUI API → FLUX Krea model → LoRA processing → VAE decode → File output
2. Template system: `{lora_keywords} {landmark} {weather_condition}` with negative prompts for style consistency
3. Fixed parameters: 1024x1024, 35 steps, euler sampler, CFG 1.0

## Key Configuration Points

### Prompt Engineering
- **Positive template**: Uses LoRA activation keywords (`lo-ply_, noc-lwply`) + landmark + weather + style descriptors
- **Negative template**: Excludes realistic weather effects, smooth shapes, large particles
- **Critical**: Maintain geometric/angular terminology throughout prompts

### Timezone Mapping
- Uses `normalize_timezone()` function: `UTC+8` → `utc_plus_8`, `UTC-5` → `utc_minus_5`
- Special handling for half-hour timezones: `UTC+5:30` → `utc_plus_5_30`

### Regional Organization
Cities are grouped by geographic proximity and cultural similarity, not just timezone. Each region has Korean names/descriptions but English operational interface.

## Development Notes

### File Paths
- Assumes ComfyUI installed in parallel directory: `../ComfyUI/`
- Output path: `../ComfyUI/output/timezones/`
- Temp files: `temp_single_city_config.json` (auto-cleanup)

### Error Handling
- 300-second timeout per image generation
- Automatic file overwriting (warns users)
- Graceful handling of missing cities in single-config generation

### Performance Characteristics  
- ~2-4 minutes per image (GPU-dependent)
- Regional batches: 1-3 hours each
- Full generation: 9-14 hours (282 images)
- VRAM requirement: 12GB+ recommended

### Integration Points
The system is designed for Flutter app integration with timezone-aware image loading patterns included in README examples.