import geopy

def address_to_coordinates(address, *, country_code="us"):
    """
    Uses geopy to retrieve latitude and longtitude.

    Parameters
    ----------
    address 
        any address, can be city or even name (e.g. World Trade Center)
    country_code (default "us")
        if not None will check that returned address is from this country
        (country to search can be specified, but I think this is a better solution)

    Returns
    -------
    (latitude, longitude)

    Examples
    --------
    >>> address_to_coordinates("New York")
    (40.7127281, -74.0060152)
    >>> address_to_coordinates("Red Square, Moscow") # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    RuntimeError: Looked for Red Square, Moscow, expected country us, got country_code=ru
    >>> address_to_coordinates("Red Square, Moscow", country_code="ru")
    (55.7536283, 37.62137960067377)
    """
    geolocator = geopy.Nominatim(user_agent="no_warning_please")
    location = geolocator.geocode(address, addressdetails=True)
    
    if location is None:
        raise RuntimeError(f"{address} was not found")
    
    if country_code is not None:
        found_country_code = location.raw["address"]["country_code"]
        if found_country_code != country_code:
            raise RuntimeError(f"Looked for {address}, expected country {country_code}, "
                               f"got country_code={found_country_code}")

    return (location.latitude, location.longitude)

def parse_address_to_twint_config(address, *, num_km, country_code="us"):
    """
    Example
    -------
    >>> parse_address_to_twint_config("New York", num_km=10)
    '40.7127281,-74.0060152,10km'
    
    Returns
    -------
    string_with_center_and_radius
    """
    latitude, longitude = address_to_coordinates(address, country_code=country_code)
    return f"{latitude},{longitude},{num_km}km"