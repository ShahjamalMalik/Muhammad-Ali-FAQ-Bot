import discord
from muhammad_ali_faq_bot import load_FAQ_data, match_intent

# Load questions, responses, and intents from external data files
questions, responses, intents = load_FAQ_data()

# Create a dictionary to keep track of user conversations
user_conversations = {}

class MyClient(discord.Client):
    def __init__(self):
        # Initialize the Discord bot with custom intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        # Event handler: Bot is ready and logged in
        print('Logged on as', self.user)

    async def on_message(self, message):
        # Event handler: Handling incoming user messages

        # Skip the bot's own messages
        if message.author == self.user:
            return

        # Preprocess user's message: Remove periods and question marks, and convert to lowercase
        utterance = message.content.lower().replace(".", "").replace("?", "")
        user_id = str(message.author.id)

        if utterance.lower() in ["hello", "hi", "hey"]:
            # Greeting response
            await message.channel.send("Hello! How can I help you?")
            return

        if utterance.lower() in ["goodbye", "bye", "quit"]:
            # Goodbye response, and exit the bot
            await message.channel.send("Goodbye!")
            return

        intent = []
        if user_id in user_conversations:
            # Continue the existing conversation
            conversation = user_conversations[user_id]
            try:
                choice = int(utterance)
                if choice > 0 and choice <= len(conversation):
                    # Retrieve and send the response based on user's choice
                    response = responses[conversation[choice - 1][0]]
                    await message.channel.send(response)
                    del user_conversations[user_id]  # End the conversation
                else:
                    await message.channel.send("Invalid choice. Please enter a valid number.")
            except ValueError:
                await message.channel.send("Invalid input. Please enter a number.")
        else:
            # Start a new conversation
            intent = match_intent(utterance, intents)
            if intent:
                if len(intent) == 1:    
                    # If there's only one matching intent, directly get and send the response
                    response = responses[intent[0][0]]
                    await message.channel.send(response)
                else:
                    sorted_intents = sorted(intent, key=lambda x: x[1])
                    matches_text = "I found multiple possible matches:\n"
                    for i, (intent_index, errors) in enumerate(sorted_intents, start=1):
                        matches_text += f"{i}. {questions[intent_index]}\n"
                    matches_text += "Please specify which question you'd like me to answer (enter a number): "
                    await message.channel.send(matches_text)
                    user_conversations[user_id] = sorted_intents

def main():
    # Create and run the Discord bot
    client = MyClient()
    with open("bot_token.txt") as file:
        token = file.read()
    client.run(token)

if __name__ == "__main__":
    # Run the bot when the script is executed
    main()
