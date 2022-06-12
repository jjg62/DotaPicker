import requests
import numpy as np

#Get Hero Data
heroes = requests.get("https://api.opendota.com/api/heroes").json()

def get_hero_name(id):
    for hero in heroes:
        if hero["id"] == id:
            return hero["name"]

    return None

#Returns a vector describing hero properties
#Rather than a 132-dimensional vector (1 for each hero), use properties to avoid curse of dimensionality
#Each entry is 1 if true, 0 if false
#(str, agi, int, Melee, Carry, Nuker, Initiator, Disabler, Durable, Escape, Support, Pusher, Jungler)
def get_hero_property_vector(id):
    property_vec = np.zeros(13)
    hero = next((h for h in heroes if h["id"] == id), None)

    if hero is None:
        print("Error getting hero property vector")
        return property_vec

    #Primary attribute
    if hero["primary_attr"] == 'str':
        property_vec[0] = 1
    elif hero["primary_attr"] == 'agi':
        property_vec[1] = 1
    else:
        property_vec[2] = 1

    #Melee or Ranged
    if hero["attack_type"] == 'Melee':
        property_vec[3] = 1

    #Roles
    roles = ['Carry', 'Nuker', 'Initiator', 'Disabler', 'Durable', 'Escape', 'Support', 'Pusher', 'Jungler']
    role_vector_pos = 4
    hero_roles = hero['roles']

    for role in roles:
        if role in hero_roles:
            property_vec[role_vector_pos] = 1

        role_vector_pos += 1

    return property_vec