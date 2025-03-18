# Yixuan Li - 000828169
# AI Usage Declaration:
# Features: "Handle multiple client requests at once" and
# "If not, a new XML entry will be made" are written with the help of ChatGPT.

import xmlrpc.client
import datetime

server = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2")

def main():
    while True:
        # Ask the user for input & send it to server
        print("1. Add new notes. ")
        print("2. Get notes. ")
        print("3. Query Wikipedia. ")
        print("4. Exit. ")

        choice = input("Select your choice: ")
        if choice == "1":
            topic = input("Input topic: ")
            text = input("Input text: ")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                # Topic, Text, and timestamp for the note
                print(server.add_note(topic, text, timestamp))
            except Exception as e:
                print(e)
        elif choice == "2":
            topic = input("Input topic: ")
            try:
                result = server.get_notes(topic)
                if result == "Not found":
                    print(f"Topic '{topic}' not found. ")
                    new_text = input(f"Enter new text to create topic '{topic}': ")
                    if new_text.strip():
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(server.add_note(topic, new_text, timestamp))
                    else:
                        print("No new topic created. ")
                # Get the contents of the XML database based on given topic
                else:
                    print(result)
            except Exception as e:
                print(e)
        elif choice == "3":
            topic = input("Input Wikipedia topic for query: ")
            try:
                # Name search terms to lookup data on wikipedia
                wiki_data = server.search_wikipedia(topic)
                print(wiki_data)
                save_choice = input("Do you want to save this Wikipedia data as a note? (yes/no): ").strip().lower()
                if save_choice == "yes":
                    # Append the data to an existing topic
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(server.add_note(topic, wiki_data, timestamp))
            except Exception as e:
                print(e)
        elif choice == "4":
            break
        else:
            print("Invalid input. Please try again. ")

if __name__ == "__main__":
    main()