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


# A function to check for greetings
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

# This function classifies the speech act (e.g., question, command, statement) of the utterance.
def classify_speech_act(utterance):
    doc = nlp(utterance)

    if any(ent.label_ == "ORG" for ent in doc.ents):
        return "Sorry, I don't know. I don't work for that organization."
    elif any(ent.label_ == "GPE" for ent in doc.ents):
        return "Sorry, I don't know. I've never been to that place."
    elif any(question_word in utterance for question_word in ["how", "what", "why", "where", "when"]):
        return "Sorry, I don't know the answer to that."
    elif any(command_word in utterance for command_word in ["give", "tell", "go", "make", "drive"]):
        return "Sorry, I don't know how to do that."
    else:
        return "Sorry, I don't understand your request."

# This function generates responses based on the matched intent and user input.
def generate(intent, responses, questions, utterance):
    print(utterance)
    if not intent:
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

            if check_for_greeting(utterance):
                print("Hello! How can I assist you today?")
            else:
                intent = match_intent(utterance, intents)
                response = generate(intent, responses, questions, utterance)
                print(response)
            print()
    except KeyboardInterrupt:
        print("Goodbye!")

if __name__ == "__main__":
    main()
