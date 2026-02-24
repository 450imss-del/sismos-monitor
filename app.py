from flask import Flask, jsonify, send_from_directory
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__, static_folder="static")

# ================= FRONTEND =================
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ================= USGS =================
def get_usgs():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    data = requests.get(url).json()
    result = []
    for eq in data["features"][:50]:
        p = eq["properties"]
        g = eq["geometry"]["coordinates"]
        result.append({
            "fuente": "USGS",
            "lugar": p["place"],
            "magnitud": p["mag"],
            "lat": g[1],
            "lon": g[0],
            "profundidad": g[2]
        })
    return result

# ================= IRIS =================
def get_iris():
    url = "https://service.iris.edu/fdsnws/event/1/query?format=geojson&limit=50"
    data = requests.get(url).json()
    result = []
    for eq in data["features"]:
        p = eq["properties"]
        g = eq["geometry"]["coordinates"]
        result.append({
            "fuente": "IRIS",
            "lugar": p.get("place", "IRIS"),
            "magnitud": p.get("mag"),
            "lat": g[1],
            "lon": g[0],
            "profundidad": g[2]
        })
    return result

# ================= JMA JAPÓN =================
def get_jma():
    url = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"
    xml_data = requests.get(url).text
    root = ET.fromstring(xml_data)
    result = []
    for entry in root.findall(".//entry")[:10]:
        title = entry.find("title").text
        result.append({
            "fuente": "JMA",
            "lugar": title,
            "magnitud": None,
            "lat": None,
            "lon": None,
            "profundidad": None
        })
    return result

# ================= SSN MÉXICO =================
def get_ssn():
    url = "http://www.ssn.unam.mx/feeds/rss.xml"
    xml_data = requests.get(url).text
    root = ET.fromstring(xml_data)
    result = []
    for item in root.findall(".//item")[:20]:
        title = item.find("title").text
        result.append({
            "fuente": "SSN México",
            "lugar": title,
            "magnitud": None,
            "lat": None,
            "lon": None,
            "profundidad": None
        })
    return result

# ================= API UNIFICADA =================
@app.route("/api/sismos")
def api_sismos():
    data = []
    try:
        data += get_usgs()
        data += get_iris()
        data += get_jma()
        data += get_ssn()
    except Exception as e:
        return jsonify({"error": str(e)})
    return jsonify(data)

# Ejecutar local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
