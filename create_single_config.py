import json
import sys

def create_single_city_config(city_name):
    try:
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
            print(f'City {city_name} not found!')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        city_name = sys.argv[1]
        create_single_city_config(city_name)
    else:
        print("Usage: python create_single_config.py <city_name>")
