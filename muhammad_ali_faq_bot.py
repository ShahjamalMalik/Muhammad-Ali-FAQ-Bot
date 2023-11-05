import re
import sys  
# This function loads data from external files (questions.txt, answers.txt, and fuzzy_regex.txt) and returns the loaded questions, answers, and intents. These files contain information about the FAQ items and the fuzzy regex patterns for matching user input.
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

# This function generates responses based on the matched intent and user input. It handles different scenarios, such as greetings and goodbyes. If there's a single matched intent, it returns the corresponding response. If there are multiple matched intents, it lets the user choose from the available options.
def generate(intent, responses, questions, utterance):
    if not intent:
        if "hello" in utterance or "hi" in utterance or "hey" in utterance:
            return "Hello! How can I help you?"
        if "goodbye" in utterance or "quit" in utterance or "exit" in utterance:
            print("Goodbye!")  
            sys.exit(0)  # Terminate the script
        return "I'm not able to answer that about Muhammad Ali"

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
            
            intent = match_intent(utterance, intents)
            response = generate(intent, responses, questions, utterance)
            print(response)
            print()
    except KeyboardInterrupt:
        print("Goodbye!")

if __name__ == "__main__":
    main()
