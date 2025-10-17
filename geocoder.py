from geopy.geocoders import Nominatim

def get_address_from_coords(lat, lon):
    """
    Takes latitude and longitude and returns a dictionary
    containing the city and district.
    """
    # Create a geolocator instance. The user_agent is required by Nominatim's
    # policy and can be the name of your app.
    geolocator = Nominatim(user_agent="civicfix_reporter_app")

    try:
        # Combine lat and lon into the required format
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True)

        # The raw address data is a dictionary. We check if it exists.
        if location and location.raw.get('address'):
            address_details = location.raw['address']
            
            # Address formats vary. We try to find the most specific term first
            # (e.g., 'city', 'town', 'village'). If none exist, we default to None.
            city = address_details.get('city') or address_details.get('town') or address_details.get('village')
            
            # The district is often stored in the 'county' key.
            district = address_details.get('county')
            
            return {"city": city, "district": district}
            
    except Exception as e:
        # If anything goes wrong (like a network error), we print the error
        # and return nothing.
        print(f"An error occurred during geocoding: {e}")
        return None


# This block is for testing the function directly.
# It only runs when you execute `python geocoder.py`.
if __name__ == "__main__":
    # Sample coordinates for Parangipettai
    test_lat = 11.4985
    test_lon = 79.7644
    
    print(f"Testing geocoder with coordinates: ({test_lat}, {test_lon})")
    
    address = get_address_from_coords(test_lat, test_lon)
    
    if address:
        print("\nSuccessfully found address:")
        print(f"  City: {address.get('city')}")
        print(f"  District: {address.get('district')}")
    else:
        print("\nCould not retrieve address.")