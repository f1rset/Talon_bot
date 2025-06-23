"""Bot for fetching info from eqn.hsc.gov.ua"""

# -----------------------------------------------
import json
import time
import requests
import librosa
import sounddevice as sd


def play_sound(status: bool = True):
    """
    Function to fire sounds

    Args:
        status (bool, optional): found(True) or error(False). Defaults to True.
    """
    if status:
        y, sr = librosa.load("alert.mp3", sr=None)

    else:
        y, sr = librosa.load("error.mp3", sr=None)

    sd.play(y, sr)
    sd.wait()


def request_data(department: int, service: int, headers: dict):
    """
    Fetch data from eqn.hsc.gov.ua

    Args:
        department (int): department id
        service (int): service id
        date (str): date to which test

    Returns:
        list: dates available
    """
    response = requests.get(
        f"https://eqn.hsc.gov.ua/api/v2/equeue/days?serviceId={service}&departmentId={department}",
        headers=headers,
        timeout=1000,
    )

    if response.status_code == 200:
        try:
            data = response.json()
            # print(data) # DEBUGING PRINT
            return data["data"]
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            return []
    else:
        print("\x1b[0;30;41m" + f"Error: {response.status_code}" + "\x1b[0m")
        if response.status_code > 499:
            return []
        play_sound(False)
        return []


def parse_headers():
    """
    Parses Headers for http request from `headers.txt`

    Returns:
        dict: Headers dictionary
    """
    with open("./headers.txt", "r", encoding="utf-8") as head_file:
        data = head_file.readlines()
        data = {i.strip().split(": ")[0]: i.strip().split(": ")[1] for i in data}
    head_file.close()
    return data


def control():
    """
    Function that controls the flow
    """
    # departments = {65: "Апостола", 74: "Богданівська", 31: "Краматорськ"}
    departments = {65: "Апостола", 74: "Богданівська"}
    # departments = {65: "Апостола", 74: "Богданівська", 69: "Стрий"}

    results = {i: [] for i in departments}
    headers = parse_headers()
    found = False
    service = 49

    while True:
        for id_, dep in departments.items():
            print(f"Trying {dep}:")
            data = request_data(id_, service, headers)

            if data:
                play_sound()
                found = True
                print(f"Available dates ({dep}):")
                for i in data:
                    print(" - " + i["date"].split("T")[0])
                    results[id_].append(" - " + i["date"].split("T")[0])
            else:
                print(f"No dates available for {dep}")
        if found:
            play_sound()

            print("\n\n\n\x1b[6;30;42mResults:\x1b[0m")
            for i, value in results.items():
                if value:
                    print("  " + departments[i] + ":")
                    print("   " + "\n   ".join(value))
            time.sleep(5)
        time.sleep(5)
        found = False
        results = {i: [] for i in departments}


control()
