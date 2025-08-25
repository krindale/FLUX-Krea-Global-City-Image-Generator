import json
import sys
import os

def create_single_city_config(city_name, is_resort=False):
    try:
        # Load appropriate config file
        config_file = 'resort_cities_config.json' if is_resort else 'global_cities_config.json'
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Find the city in appropriate sections
        target_city = None
        
        if is_resort and 'resort_destinations' in config:
            # Search in resort destinations
            for category_name, category_data in config['resort_destinations'].items():
                for city in category_data['cities']:
                    if city['name'] == city_name:
                        target_city = city
                        break
                if target_city:
                    break
        elif not is_resort and 'regions' in config:
            # Search in regular regions
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
            
            if is_resort:
                # For resort cities, create resort_destinations structure
                single_config['resort_destinations'] = {
                    'single_city': {
                        'name': 'Single Resort City Generation',
                        'description': f'Single resort city: {target_city["city"]}',
                        'cities': [target_city]
                    }
                }
                output_file = 'temp_single_resort_config.json'
            else:
                # For regular cities, create regions structure
                single_config['regions'] = {
                    'single_city': {
                        'name': 'Single City Generation',
                        'description': f'Single city: {target_city["city"]}',
                        'cities': [target_city]
                    }
                }
                output_file = 'temp_single_city_config.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(single_config, f, indent=2, ensure_ascii=False)
            
            print(f'Config created for {target_city["city"]} ({"Resort" if is_resort else "Regular"} city)')
            return True
        else:
            config_type = "resort cities" if is_resort else "main cities"
            print(f'City {city_name} not found in {config_type}!')
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
    """List all available cities, resort destinations, and fallback regions"""
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
    
    print("\n=== AVAILABLE RESORT DESTINATIONS ===")
    try:
        with open('resort_cities_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'resort_destinations' in config:
            for category_name, category_data in config['resort_destinations'].items():
                print(f"\n{category_data['name']}:")
                for city in category_data['cities']:
                    print(f"  - {city['name']} ({city['city']}, {city['country']})")
    except Exception as e:
        print(f"Error loading resort destinations: {e}")
    
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

def generate_single_selection(selection_name, is_resort=False):
    """Generate config for city, resort city, or fallback region"""
    if is_resort:
        # Try as resort city first
        if create_single_city_config(selection_name, is_resort=True):
            return True
        print(f"'{selection_name}' not found in resort destinations!")
        print("Use '--list' to see all available options.")
        return False
    else:
        # Try as regular city first
        if create_single_city_config(selection_name, is_resort=False):
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
            is_resort = '--resort' in sys.argv
            generate_single_selection(selection_name, is_resort)
    else:
        print("Usage:")
        print("  python create_single_config.py <city_name_or_region_name>")
        print("  python create_single_config.py <resort_city_name> --resort")
        print("  python create_single_config.py --list")
        print("")
        print("Examples:")
        print("  python create_single_config.py seoul")
        print("  python create_single_config.py maldives --resort")
        print("  python create_single_config.py northern_india")
        print("  python create_single_config.py china_south")
