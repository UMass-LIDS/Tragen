import json
with open("config.json") as config:
        config = json.load(config)

for tc in config["traffic_classes"]:
    print(tc)
