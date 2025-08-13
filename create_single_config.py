import json
import sys
import os

def create_single_city_config(city_name):
    try:
        # Load main cities config
        with open('global_cities_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Find the city in all regions
        target_city = None
        for region_name, region_data in config['regions'].items():
            for city in region_data['cities']:
                if city['name'] == city_name:
                    target_city = city
                    break
            if target_city:
                break
        
        if target_city:
            # Create single city config
            single_config = config.copy()
            single_config['regions'] = {
                'single_city': {
                    'name': 'Single City Generation',
                    'description': f'Single city: {target_city["city"]}',
                    'cities': [target_city]
                }
            }
            
            with open('temp_single_city_config.json', 'w', encoding='utf-8') as f:
                json.dump(single_config, f, indent=2, ensure_ascii=False)
            
            print(f'Config created for {target_city["city"]}')
            return True
        else:
            print(f'City {city_name} not found in main cities!')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

def create_single_fallback_config(region_name):
    try:
        # Load fallback regions config
        with open('regional_fallback_config.json', 'r', encoding='utf-8') as f:
            fallback_config = json.load(f)
        
        # Find the region in fallback config
        target_region = None
        if region_name in fallback_config['regional_fallbacks']:
            target_region = fallback_config['regional_fallbacks'][region_name]
        
        if target_region:
            # Create single region fallback config
            single_config = fallback_config.copy()
            single_config['regional_fallbacks'] = {
                region_name: target_region
            }
            
            with open('temp_single_fallback_config.json', 'w', encoding='utf-8') as f:
                json.dump(single_config, f, indent=2, ensure_ascii=False)
            
            print(f'Config created for {target_region["name"]} fallback region')
            return True
        else:
            print(f'Fallback region {region_name} not found!')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

def list_available_options():
    """List all available cities and fallback regions"""
    print("\n=== AVAILABLE CITIES ===")
    try:
        with open('global_cities_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for region_name, region_data in config['regions'].items():
            print(f"\n{region_data['name']}:")
            for city in region_data['cities']:
                print(f"  - {city['name']} ({city['city']}, {city['country']})")
    except Exception as e:
        print(f"Error loading cities: {e}")
    
    print("\n=== AVAILABLE FALLBACK REGIONS ===")
    try:
        with open('regional_fallback_config.json', 'r', encoding='utf-8') as f:
            fallback_config = json.load(f)
        
        for region_key, region_data in fallback_config['regional_fallbacks'].items():
            priority_text = {1: "High", 2: "Medium", 3: "Low"}.get(region_data.get("priority", 3), "Unknown")
            print(f"  - {region_key} ({region_data['name']}) - Priority: {priority_text}")
            print(f"    Population: {region_data.get('population', 'N/A')}")
    except Exception as e:
        print(f"Error loading fallback regions: {e}")

def generate_single_selection(selection_name):
    """Generate config for either city or fallback region"""
    # Try as city first
    if create_single_city_config(selection_name):
        return True
    
    # Try as fallback region
    if create_single_fallback_config(selection_name):
        return True
    
    print(f"'{selection_name}' not found in cities or fallback regions!")
    print("Use '--list' to see all available options.")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_available_options()
        else:
            selection_name = sys.argv[1]
            generate_single_selection(selection_name)
    else:
        print("Usage:")
        print("  python create_single_config.py <city_name_or_region_name>")
        print("  python create_single_config.py --list")
        print("")
        print("Examples:")
        print("  python create_single_config.py seoul")
        print("  python create_single_config.py northern_india")
        print("  python create_single_config.py china_south")
