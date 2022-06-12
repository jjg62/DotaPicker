import requests

import heroes
import numpy as np
import time

from sklearn.neural_network import MLPClassifier

classifier = None

def train(player_id, limit, progress_bar, show_results, try_again):

    global classifier

    #Get 100 matches the player won
    won_matches = requests.get("https://api.opendota.com/api/players/" + str(player_id) + "/matches?win=1" + (("&limit=" + str(limit)) if limit > 0 else ""))

    #Check OK
    if won_matches.status_code == 200:
        won_matches = won_matches.json()
    else:
        print("Error finding player's matches")
        try_again()
        return

    train_y = []
    train_x = []
    for win in won_matches:
        #Get match id and player slot, hero played and team of the player
        id = win["match_id"]
        slot = win["player_slot"]
        hero_played = win["hero_id"]
        team = 0 if (slot < 5) else 1 #0 = dire, 1 = radiant

        #Get details for that match
        match_details = requests.get("https://api.opendota.com/api/matches/" + str(id))
        code = match_details.status_code
        if code == 200:
            match_details = match_details.json()
        else:
            print(match_details.status_code)
            print("Error getting match details for match", id)
            error = match_details.json()["error"]
            print(error)
            if(code == 429):
                print("Waiting for rate limit to unlock...\n")
                time.sleep(30)
            continue


        team_vector = np.zeros(13)

        #Go through picks and bans
        picks_bans = match_details["picks_bans"]

        if picks_bans is None: continue

        for pb in picks_bans:

            #Get hero picked and which team
            hid = pb["hero_id"]
            t = pb["team"]

            #Get enemy picks before the player picked
            if hid != hero_played:
                if t != team:
                    #Add together their 'property vectors' giving a descriptor for enemy team
                    team_vector += heroes.get_hero_property_vector(hid)
            else:
                break

        train_x.append(team_vector)
        train_y.append(hid)
        print(id)
        print(heroes.get_hero_name(hero_played))
        print(team_vector)
        print("\n")
        progress_bar["value"] = (len(train_x) / limit) * 100

    classifier = MLPClassifier(max_iter=500, hidden_layer_sizes=(4,4), random_state=1)
    classifier.fit(train_x, train_y)

    show_results()


def query(input_team_vec):
    global classifier

    #Get probabilities of each class
    probs = classifier.predict_proba([input_team_vec])
    #Sort probabilities, then get top 3 indices
    best_3_indices = np.argsort(probs[0])[-3:]
    return classifier.classes_[best_3_indices]