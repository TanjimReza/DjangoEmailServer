from pprint import pprint

import requests


def verify_profile(profile_name, email):
    url = 'https://script.google.com/macros/s/AKfycbz-K4WbnBMN9f_0oSPW-1HIkhQy6V6hZGqL6NyIlcX-QG3ANrkDMs040t_2JQcZ1wKH/exec'
    
    params = {
        'profileName': profile_name,
        'email': email
    }
    response = requests.get(url, params=params)
    result = response.json()
    pprint(result)
    return result['result']

# Example usage
is_valid = verify_profile('BondhuShobha', 'tanjimreza786@gmail.com')

pprint(is_valid)