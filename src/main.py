import requests
import csv
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv("config\settings.env")

THINGSPEAK_API_KEY = os.getenv("THINGSPEAK_API_KEY")
THINGSPEAK_CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_TABLE_NAME = os.getenv("SUPABASE_TABLE_NAME")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")

# THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_API_KEY}&results=1"
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/2769816/feeds.json?api_key=WTIFG3EJDHOGBRKF&results=1"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def log_message(message):
    """Mencatat log ke file."""
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"[{datetime.now()}] {message}\n")

def fetch_data_from_thingspeak():
    """Mengambil data terbaru dari ThingSpeak."""
    try:
        response = requests.get(THINGSPEAK_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data["feeds"]:
            log_message("No data found in ThingSpeak.")
            return None
        latest_data = data["feeds"][-1]
        log_message(f"Fetched data: {latest_data}")
        return latest_data
    except requests.exceptions.RequestException as e:
        log_message(f"Error fetching data from ThingSpeak: {e}")
        return None

def send_data_to_supabase(data):
    """Mengirim data ke Supabase."""
    try:
        formatted_data = {
            "entry_id": data["entry_id"],
            "created_at": data["created_at"],
            "ph": float(data.get("field1", 0)),
            "do": float(data.get("field2", 0)),
            "t": float(data.get("field3", 0)),
            "v": float(data.get("field4", 0)),
            "sensor_id": data.get("field5", "unknown")
        }
        response = supabase.table(SUPABASE_TABLE_NAME).insert(formatted_data).execute()
        if response.data:
            log_message("Data successfully sent to Supabase.")
        else:
            log_message(f"Error sending data to Supabase: {response}")
    except Exception as e:
        log_message(f"Supabase error: {e}")

def save_data_to_csv(data):
    """Menyimpan data ke file CSV lokal."""
    file_exists = os.path.exists(CSV_FILE_PATH)
    with open(CSV_FILE_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["entry_id", "created_at", "ph", "do", "t", "v", "sensor_id"])
        writer.writerow([
            data["entry_id"],
            data["created_at"],
            data.get("field1"),
            data.get("field2"),
            data.get("field3"),
            data.get("field4"),
            data.get("field5")
        ])
    log_message("Data successfully saved to CSV.")

# def save_data_to_csv(data):
#     """Menyimpan data ke file CSV lokal dalam format tabel."""
#     file_exists = os.path.exists(CSV_FILE_PATH)
#     with open(CSV_FILE_PATH, mode="a", newline="") as file:
#         writer = csv.writer(file)
#         if not file_exists:
#             file.write("sep=,\n")
#             writer.writerow(["Entry ID", "Created At", "PH", "DO", "T", "V", "Sensor ID"])
#         writer.writerow([
#             data["entry_id"],
#             data["created_at"],
#             data.get("field1"),
#             data.get("field2"),
#             data.get("field3"),
#             data.get("field4"),
#             data.get("field5")
#         ])
#     log_message("Data successfully saved to CSV.")


def main():
    data = fetch_data_from_thingspeak()
    if data:
        send_data_to_supabase(data)
        save_data_to_csv(data)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_message(f"Unexpected error: {e}")
