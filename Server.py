# Yixuan Li - 000828169
# AI Usage Declaration:
# Features: "Handle multiple client requests at once" and
# "If not, a new XML entry will be made" are done with the help of ChatGPT.

import xml.etree.ElementTree as ET
import xml.dom.minidom
import threading
import requests
import os
import datetime
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn

file = "notes.xml"

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

def init_file():
    try:
        if not os.path.exists(file):
            root = ET.Element("notes")
            tree = ET.ElementTree(root)
            tree.write(file)
    except Exception as e:
        print(f"Error initializing file: {e}")

def pretty_print_xml(tree):
    rough_string = ET.tostring(tree.getroot(), 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Process the client's input
def add_note(topic, text, timestamp):
    tree = ET.parse(file)
    root = tree.getroot()
    for note in root.findall("note"):
        if note.find("topic").text.lower() == topic.lower():
            entries = note.find("entries")
            if entries is None:
                entries = ET.SubElement(note, "entries")
            entry = ET.SubElement(entries, "entry")
            ET.SubElement(entry, "timestamp").text = timestamp
            ET.SubElement(entry, "text").text = text
            tree.write(file, encoding="utf-8", xml_declaration=True)
            return "Note updated. "
    note = ET.SubElement(root, "note")
    ET.SubElement(note, "topic").text = topic
    entries = ET.SubElement(note, "entries")
    entry = ET.SubElement(entries, "entry")
    ET.SubElement(entry, "timestamp").text = timestamp
    ET.SubElement(entry, "text").text = text
    tree.write(file, encoding="utf-8", xml_declaration=True)
    return "New topic added. "

# Process the client's input
def get_notes(topic):
    tree = ET.parse(file)
    root = tree.getroot()
    for note in root.findall("note"):
        if note.find("topic").text.lower() == topic.lower():
            entries = note.find("entries")
            if entries is not None:
                results = []
                for entry in entries.findall("entry"):
                    timestamp = entry.find("timestamp").text
                    text = entry.find("text").text
                    results.append(f"[{timestamp}] {text}")
                return "\n".join(results)
    wiki_data = search_wikipedia(topic)
    if "No results found. " not in wiki_data and "Error retrieving information. " not in wiki_data:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_note(topic, wiki_data, timestamp)
        return f"Topic not found locally. Wikipedia data added:\n{wiki_data}"
    return "Not found. "

# Query wikipedia for user submitted articles
def search_wikipedia(topic):
    try:
        url = f"https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": topic
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            if search_results:
                first_result = search_results[0]
                title = first_result["title"]
                snippet = first_result["snippet"]
                page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                return f"Title: {title}\nSnippet: {snippet}\nURL: {page_url}"
            return "No results found."
        return "Error retrieving information. "
    except requests.exceptions.RequestException as e:
        return f"Error retrieving information: {e}"

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def run_server():
    try:
        server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
        server.register_function(add_note, "add_note")
        server.register_function(get_notes, "get_notes")
        server.register_function(search_wikipedia, "search_wikipedia")
        print("Server running on port 8000. ")
        server.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    init_file()
    server_thread = threading.Thread(target=run_server)
    server_thread.start()