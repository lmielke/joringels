# yaml_to_json.py
"""
    convets the joringels yml file to a jq readable json string
    initialze_joringels.sh then takse this string to derrive startup parameters for jo.serve
"""
import json, yaml, os

filePath = os.path.join(os.environ.get("RMUSERDIR", "/home/gitlab-runner"), ".ssp")
fileName = os.environ.get("DATASAFENAME")
with open(os.path.join(filePath, f"_joringels.yml"), "r") as y:
    out = yaml.safe_load(y)
with open(os.path.join(filePath, f"_joringels.json"), "w+") as f:
    json.dump(json.dumps(out, ensure_ascii=False), f)
with open(os.path.join(filePath, f"_joringels.json"), "r") as f:
    text = f.read()
with open(os.path.join(filePath, f"_joringels.json"), "w") as f:
    f.write(text[1:-1].replace("\\", ""))
