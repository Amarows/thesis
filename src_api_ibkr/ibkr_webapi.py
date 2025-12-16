import requests
r = requests.get("https://localhost:5000/v1/api/iserver/marketdata/history",
                 params={"conid": 265598, "period": "1d", "bar": "5min"},
                 verify=False)  # CP uses a self-signed cert
print(r.json())