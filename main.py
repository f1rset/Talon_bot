"""Bot for fetching info from eqn.hsc.gov.ua"""

# -----------------------------------------------
import requests
import json
import time
import librosa
import sounddevice as sd


def play_sound(status=True):
    if status:
        y, sr = librosa.load(
            "alert.mp3", sr=None
        )  # use sr=None to preserve original sample rate
    else:
        y, sr = librosa.load("error.mp3", sr=None)
    # Play the audio
    sd.play(y, sr)
    sd.wait()  # Wait until audio is done playing


def request_data(department: int, service: int, date: str, headers: dict):
    """
    Fetch data from eqn.hsc.gov.ua

    Args:
        department (int): department id
        service (int): service id
        date (str): date to which test
    """
    response = requests.get(
        f"https://eqn.hsc.gov.ua/api/v2/departments/{department}/\
services/{service}/slots?date={date}&page=1&pageSize=20",
        headers=headers,
        timeout=100,
    )
    # response = requests.get(
    #     "https://eqn.hsc.gov.ua/api/v2/departments/31/services/49/slots?date=2025-06-20&page=1&pageSize=20",
    #     headers=headers,
    #     timeout=100,
    # )
    if response.status_code == 200:
        try:
            data = response.json()
            # print(data)
            return data["data"]
        except json.JSONDecodeError:
            print("Response is not valid JSON")
    else:
        print(f"Error: {response.status_code}")
        if response.status_code > 499:
            return []
        play_sound(False)
        return []


def parse_headers():
    with open("./headers.txt", "r", encoding="utf-8") as head_file:
        data = head_file.readlines()
        data = {i.strip().split(": ")[0]: i.strip().split(": ")[1] for i in data}
    head_file.close()
    return data


def fetch_dates(headers):
    response = requests.get(
        "https://eqn.hsc.gov.ua/api/v2/days?startDate=[&endDate=s&serviceId=49",
        headers=headers,
        timeout=100,
    )

    if response.status_code == 200:
        try:
            data = response.json()
            print(data)
            return [i["date"].split("T")[0] for i in data["data"]]
        except json.JSONDecodeError:
            print("Response is not valid JSON")
    else:
        print(f"Error: {response.status_code}")
        if response.status_code > 499:
            return []
        play_sound(False)
        return []


def control():
    headers = parse_headers()
    found = False
    service = 49
    dates = fetch_dates(headers)
    print(dates)
    # dates = [
    #     "2025-06-10",
    #     "2025-06-11",
    #     "2025-06-12",
    #     "2025-06-13",
    #     "2025-06-14",
    #     "2025-06-15",
    #     "2025-06-17",
    #     "2025-06-18",
    #     "2025-06-19",
    #     "2025-06-20",
    #     "2025-06-21",
    #     "2025-06-22",
    #     "2025-06-24",
    #     # "2025-06-25"
    # ]

    # departments = {65: "Апостола", 74: "Богданівська", 31: "Краматорськ"}
    departments = {65: "Апостола", 74: "Богданівська"}
    # departments = {65: "Апостола", 74: "Богданівська", 69: "Стрий"}
    results = []

    while True:
        # today = datetime.date.today()
        # dates = [today + datetime.timedelta(days=i) for i in range(21)]
        dates = fetch_dates(headers)
        if not dates:
            time.sleep(10)
        #    continue
            dates = [
                "2025-06-09",
                "2025-06-10",
                "2025-06-11",
                "2025-06-12",
                "2025-06-13",
                "2025-06-14",
                "2025-06-15",
                "2025-06-17",
                "2025-06-18",
                "2025-06-19",
                "2025-06-20",
                "2025-06-21",
                "2025-06-22",
                "2025-06-24",
                "2025-06-25",
            ]

        for date in dates[::-1]:
            for id_, department in departments.items():
                print(
                    "\x1b[0;30;0m"
                    + f"Trying dep: {department} date: {date}"
                    + "\x1b[0m"
                )
                data = request_data(id_, service, date, headers)
                if data:
                    found = True
                    print(
                        "\x1b[6;30;42m"
                        + f"Found:\ndep: {department}\ndate: {date}"
                        + "\x1b[0m"
                    )
                    results.append(
                        "\x1b[6;30;42m" + f"dep: {department}\ndate: {date}" + "\x1b[0m"
                    )
                    play_sound()
                else:
                    print(
                        "\x1b[0;30;41m"
                        + f"Not found\ndep: {department}\ndate: {date}"
                        + "\x1b[0m"
                    )

        if found:
            print("\n\nResults:\n" + "\n".join(results))
            results = []

            play_sound()
            time.sleep(5)
        time.sleep(5)


control()
