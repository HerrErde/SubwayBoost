import json
import requests

gplayapi_url = "https://gplayapi.herrerde.xyz/api/apps/com.kiloo.subwaysurf"
json_file = "src/version.json"
season_hunt_file = "src/profile/season_hunt.json"
collections_file = "temp/input/collections_data.json"


def get_version():
    try:
        response = requests.get(gplayapi_url)
        response.raise_for_status()  # Raise an exception for unsuccessful status codes
        return response.json()["version"]
    except requests.RequestException as e:
        print(f"Error retrieving app version: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing app version JSON: {e}")
        return None


def update_season():
    try:
        with open(collections_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            time_slot = data.get("timeSlot", "")
            season = int(time_slot.split("_S")[1])
            return season
    except (IOError, json.JSONDecodeError, ValueError, IndexError) as e:
        print(f"Error loading collections data: {e}")
        return None


def update_season_hunt(season, season_hunt_file):
    try:
        with open(season_hunt_file, "r+") as file:
            data = json.load(file)
            data["data"]["currentTimeSlotId"] = f"season_S{season}"
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
    except (IOError, json.JSONDecodeError, KeyError) as e:
        print(f"Error updating season hunt file: {e}")


def update_version(data, season):
    try:
        version = data["version"]
        major, minor, patch = map(int, version.split("."))

        patch = (patch + 1) % 10
        minor += int(patch == 0)
        minor %= 10
        major += int(minor == 0 and patch == 0)
        major = min(major, 9)

        app_version = get_version()

        data.update(
            {
                "version": f"{major}.{minor}.{patch}",
                "appversion": app_version,
                "season": str(season),
            }
        )

        return data
    except (ValueError, KeyError) as e:
        print(f"Error updating version data: {e}")
        return None


def main():
    try:
        with open(json_file, "r+") as file:
            data = json.load(file)
            season = update_season()

            if season is not None:
                updated_data = update_version(data, season)

                if updated_data is not None:
                    file.seek(0)
                    json.dump(updated_data, file, indent=2)
                    file.truncate()
                    file.write("\n")

                    update_season_hunt(season, season_hunt_file)
                else:
                    print("Version update failed.")
            else:
                print("Season data is missing or invalid.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error processing JSON file: {e}")


if __name__ == "__main__":
    main()
