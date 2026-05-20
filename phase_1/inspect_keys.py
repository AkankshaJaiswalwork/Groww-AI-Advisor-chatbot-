import json

data_path = "/Users/akankshajaiswal/Desktop/Antigravity skills/ai builds /nextleap_rag/phase_1/data/nippon-india-small-cap-fund-direct-growth_raw.json"
with open(data_path, "r") as f:
    data = json.load(f)

return_stats = data['props']['pageProps']['mfServerSideData'].get('return_stats', [])
print("Return Stats structure:")
print(json.dumps(return_stats, indent=2))
