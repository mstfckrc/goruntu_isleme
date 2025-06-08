import json

def get_topics_from_keywords(sentence):
   
    with open("controller/topics/topics.json", "r", encoding="utf-8") as file:
        topics = json.load(file)

    sentence = sentence.lower()
    matching_topics = []

    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in sentence and topic not in matching_topics:
                    matching_topics.append(topic)
    
    if not matching_topics:
        return ["Belirlenmemiş"]
    
    return ", ".join(matching_topics)