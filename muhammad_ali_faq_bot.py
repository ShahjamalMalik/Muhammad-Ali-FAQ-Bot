import re
import sys
import spacy
from spacy.matcher import Matcher

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# This function loads data from external files (questions.txt, answers.txt, and fuzzy_regex.txt) and returns the loaded questions, answers, and intents.
def load_FAQ_data():
    questions = []
    answers = []

    # Load questions from 'questions.txt' and store in the 'questions' list
    with open('questions.txt', 'r') as questionFile:
        questions = [line.strip() for line in questionFile.readlines()]

    # Load answers from 'answers.txt' and store in the 'answers' list
    with open('answers.txt', 'r') as answerFile:
        answers = [line.strip() for line in answerFile.readlines()]

    # Load fuzzy regular expressions from 'fuzzy_regex.txt' and store in the 'intents' list
    with open('fuzzy_regex.txt', 'r') as fuzzy_regex_file:
        intents = [line.strip() for line in fuzzy_regex_file]

    return questions, answers, intents


# A function to check for greetings using spaCy
def check_for_greeting(utterance):
    doc = nlp(utterance)
    matcher = Matcher(nlp.vocab)

    # Defining a pattern for common greetings
    greeting_pattern = [{"LOWER": {"in": ["hello", "hi", "hey"]}}]

    # Adding the greeting pattern to the matcher
    matcher.add("Greeting", [greeting_pattern])

    # Usinf the matcher to find matches in the input
    matches = matcher(doc)

    return any(matches)

# A function to check for farewells using spaCy
def check_for_farewell(utterance):
    doc = nlp(utterance)

    # Define patterns for common farewells
    farewell_patterns = [
        {"LOWER": "bye"},
        {"LOWER": "goodbye"},
        {"LOWER": "see", "LOWER": "you", "LOWER": "later"},
    ]

    # Check if any of the farewell patterns match
    for pattern in farewell_patterns:
        if any(token.text == pattern["LOWER"] for token in doc):
            return True

    return False
# Function to determine if a sentence is a question
def is_question(doc):
    # Check if the sentence starts with a question word
    if len(doc) > 0 and doc[0].text.lower() in ["how", "what", "why", "where", "when"]:
        return True
    
    # Check if the sentence contains a question mark
    if "?" in doc.text:
        return True

    # Check if the sentence contains an auxiliary verb (e.g., "is," "can," "will") which is typical in questions
    if any(token.dep_ == "aux" for token in doc):
        return True

    return False
# Function to determine if a sentence is a statement
def is_statement(doc):
    # Check if the sentence contains a verb
    if any(token.pos_ == "VERB" for token in doc):
        return True

    # Check if the sentence contains an imperative verb (e.g., "give," "tell," "go," "make," "drive")
    if any(token.lemma_.lower() in ["give", "tell", "go", "make", "drive"] for token in doc):
        return True

    # You can add more specific criteria as needed based on your use case

    return False
# This function takes user input (utterance) and a list of intents, then matches the user input with the fuzzy regex patterns in the intents. It returns a list of matched intents sorted by the number of errors.
def match_intent(utterance, intents):
    matched_intents = []

    for idx, intent in enumerate(intents):
        # Use regular expressions to check if 'utterance' matches 'intent'
        match = re.match(intent, utterance)

        if match:
            # Extract the number of errors if it's present, otherwise, use 0
            errors = int(match.group('fuzzy_errors')) if 'fuzzy_errors' in match.groupdict() else 0
            matched_intents.append((idx, errors))

    if matched_intents:
        # Sort matched intents by the number of errors in ascending order
        sorted_intents = sorted(matched_intents, key=lambda x: x[1])
        return sorted_intents

    return []

# This function classifies the speech act (e.g., question, command, statement) of the utterance using spaCy.
def classify_speech_act(utterance):
    doc = nlp(utterance)
    
    # Check for "ORG" entities
    if any(ent.label_ == "ORG" for ent in doc.ents):
        return "Sorry, I don't know. I don't work for that organization."
    
    # Check for "GPE" entities
    if any(ent.label_ == "GPE" for ent in doc.ents):
        return "Sorry, I don't know. I've never been to that place."
    
    # Check if it's a question
    if is_question(doc):
        return "It seems like you're asking a question, but I may not have the answer."
    
    # Check if it's a statement
    if is_statement(doc):
        return "It looks like you're making a statement. Is there something specific you'd like to know?"
    

    
    # If none of the above, provide a generic response
    return "Sorry, I don't understand your request."


# This function generates responses based on the matched intent and user input.
def generate(intent, responses, questions, utterance):
    #If not intent
    if not intent:
        # Check if the string get to is in the utterance, if it is send a customized google maps link
        # If there's an ent.label tag of person or work_of_art and it's not muhammad ali, give back a google link
        # If neither are the case then do classify_speech_act with utterance
        if "get to" in utterance:
            location = re.search(r'get to (.+)', utterance).group(1)
            google_maps_link = f"https://www.google.com/maps/search/{location.replace(' ', '%20')}"
            return f"Sorry, I don't know, but you could try Google Maps. Here's a link: {google_maps_link}"
        elif any(ent.label_ in ["PERSON", "WORK_OF_ART"] for ent in nlp(utterance).ents):
            entity_name = next(ent.text for ent in nlp(utterance).ents if ent.label_ in ["PERSON", "WORK_OF_ART"])
            if(entity_name == "muhammad ali"):
                return f"This is a FAQ Bot about Muhammad Ali, please ask the questions in questions.txt to have them answered"
            else: 
                wikipedia_link = f"https://en.wikipedia.org/wiki/{entity_name.replace(' ', '_')}"
                return f"Sorry, I don't know, but maybe you could try Wikipedia. Here's a link: {wikipedia_link}"
        else:
            speech_act_response = classify_speech_act(utterance)
            return speech_act_response
    
    if isinstance(intent, int):
        # If there's only one matching intent, return the corresponding response
        return responses[intent]
    #If multiple matching responses, let the user choose which one they want answered by picking a number that assosciates with the question
    elif isinstance(intent, list):
        if len(intent) == 1:
            # If there's only one matching intent, return the corresponding response
            return responses[intent[0][0]]
        else:
            response = "I found multiple possible matches:\n"
            for i, (intent_index, errors) in enumerate(intent, start=1):
                response += f"{i}. {questions[intent_index]}\n"
            response += "Please specify which question you'd like me to answer (enter a number): "
            print(response)  # Print the options
            try:
                choice = int(input("Enter your choice: "))  # Read the user's choice
                if choice > 0 and choice <= len(intent):
                    # Return the response based on the user's choice
                    return responses[intent[choice - 1][0]]
                else:
                    return "Invalid choice. Please enter a valid number."
            except ValueError:
                return "Invalid input. Please enter a number."
    

# Main program execution
def main():
    # Load questions, responses, and intents
    questions, responses, intents = load_FAQ_data()

    print("Hello! I know stuff about Muhammad Ali. When you're done, just say 'goodbye.'")

    try:
        while True:
            # Get user's input and process it
            utterance = input(">>> ").strip().lower().replace(".", "").replace("?", "")

            #The utterance will be checked for farewells/greetings with the methods we created to do so, if neither is the case then generate an appropriate response
            if check_for_greeting(utterance):
                print("Hello! How can I assist you today?")
            elif check_for_farewell(utterance):
                print("Goodbye! If you have more questions in the future, feel free to return.")
                break  # Exit the chat loop
            else:
                intent = match_intent(utterance, intents)
                response = generate(intent, responses, questions, utterance)
                print(response)
            print()
    except KeyboardInterrupt:
        print("Goodbye!")

if __name__ == "__main__":
    main()
