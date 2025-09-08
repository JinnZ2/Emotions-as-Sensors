from sensors import load_sensor

grief = load_sensor("sensors/grief.json")

signal = grief.detect(event="loss of ally")
action = grief.respond(signal)

print(action)
# → "Map loss, adapt to new structure, release after cycle completes"
