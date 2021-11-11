def depression_classification(score):
  if score < 0.3:
    return 'No Depression'
  elif score < 0.5:
    return 'Mild Depression'
  elif score < 0.7:
    return 'Moderate Depression'
  elif score >= 0.7:
    return 'Severe Depression'

def score_depression(my_dict, category): 
    if category == 'house':
        return house_score(my_dict)
    elif category == 'person':
        return person_score(my_dict)
    elif category == 'tree':
        return tree_score(my_dict)
#-------------------------------------
def house_score(my_dict):
    depression_score = 0
    print(type(my_dict))
    
    if "door" in my_dict: 
        del my_dict['door'] 
    else: 
        depression_score+=0.125

    if "wall" in my_dict : 
        del my_dict['wall'] 
    else: 
        depression_score+=0.125

    if "roof" in my_dict : 
        del my_dict['roof'] 
    else: 
        depression_score+=0.125

    if "closed_window" in my_dict : 
        del my_dict['closed_window'] 
    else: 
        depression_score+=0.125
    
    if "single_line_roof" in my_dict :depression_score+=0.05
    
    if  "wall" in my_dict :depression_score+=0.05
    
    if "door" in my_dict :depression_score+=0.05
    
    if "closed_window" in my_dict :depression_score+=0.05
    
    if "open_window" in my_dict :depression_score+=0.05
    
    if "roof" in my_dict :depression_score+=0.05
    
    if "shadow" in my_dict :depression_score+=0.05
    
    if "chimney" in my_dict :depression_score+=0.05
    
    if "smoking_chimney" in my_dict :depression_score+=0.05
    
    if "clouds" in my_dict :depression_score+=0.05
    
    if "shaded_roof" in my_dict :depression_score+=0.05
    
    if "big_house" in my_dict :depression_score+=0.05
    
    if  "small_house" in my_dict :depression_score+=0.05
    
    if "bottom_placed_house" in my_dict : depression_score+=0.05
    
    print(depression_score)

    return depression_score
#-------------------------------------------------------
def person_score(my_dict):
    depression_score = 0
    print(type(my_dict))

    present = ['closed_eye', 'cupid_mouth', 'empty_eye', 'eyebrow', 'frowning_eyebrow', 'large_ear', 'large_nose', 'line_unsmiling_mouth', 'open_mouth', 'pointy_nose', 'small_eye']

    absent = ['ear', 'eye', 'face', 'mouth', 'nose']
    
    for ab in absent: 
        if ab not in my_dict: 
            depression_score+=0.125
            my_dict['Omitted '+ab] = 1.0
        #else: 
            

    for pr in present:
        if pr in my_dict :depression_score+=0.05
    
    print(depression_score)

    return depression_score


















