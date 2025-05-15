import requests
import pandas as pd
import time
from datetime import datetime
import argparse

# === Constants ===
PERFORMANCE_API = "https://terminal.markets/api/analytics/players/performance?limit=50"
AGENTS_API = "https://terminal.markets/api/agents/player"
PROMPTS_API = "https://terminal.markets/api/agents/prompts"
DEFAULT_OUTPUT_CSV = "agent_snapshot_log.csv"
HEADERS = {
    "accept": "application/json",
    "referer": "https://terminal.markets/game",
    "user-agent": "Mozilla/5.0"
}

# === Get top players ===
def get_top_players(always_include):
    response = requests.get(PERFORMANCE_API, headers=HEADERS)
    response.raise_for_status()
    players = response.json()

    player_dict = {
        p["player_id"]: {
            "player_id": p["player_id"],
            "start_value": p["start_value"],
            "end_value": p["end_value"],
            "percent_change": p["percent_change"],
            "rank": p["rank"]
        } for p in players
    }

    if always_include and always_include not in player_dict:
        player_dict[always_include] = {
            "player_id": always_include,
            "start_value": None,
            "end_value": None,
            "percent_change": None,
            "rank": None
        }

    return player_dict

# === Get all agents for a player ===
def fetch_agents(player_id):
    agents = []
    offset = 0
    limit = 250
    while True:
        url = f"{AGENTS_API}?playerId={player_id}&limit={limit}&offset={offset}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        agents.extend(data.get("data", []))
        offset += limit
        if offset >= data.get("total", 0):
            break
    return agents

# === Break IDs into batches ===
def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# === Get prompts for agents ===
def fetch_prompts(agent_ids, batch_size=100):
    all_prompts = {}
    for batch in chunked(agent_ids, batch_size):
        ids_str = ",".join(str(i) for i in batch)
        try:
            response = requests.get(f"{PROMPTS_API}?ids={ids_str}", headers=HEADERS)
            response.raise_for_status()
            prompts = response.json().get("prompts", {})
            all_prompts.update(prompts)
        except requests.RequestException as e:
            print(f"Prompt batch failed: {e}")
        time.sleep(0.2)
    return all_prompts

# === Combine everything ===
def build_dataframe(top_players):
    all_rows = []
    timestamp = datetime.utcnow().isoformat()

    for player_id, perf in top_players.items():
        print(f"Processing {player_id}")
        agents = fetch_agents(player_id)
        agent_ids = [agent["id"] for agent in agents]
        prompts = fetch_prompts(agent_ids)

        for agent in agents:
            persona = agent.get("persona", {})
            all_rows.append({
                "timestamp": timestamp,
                "agent_id": agent["id"],
                "name": agent.get("name"),
                "type": agent.get("type"),
                "condition": agent.get("condition"),
                "company_id": agent.get("company_id"),
                "player_id": player_id,
                "rank": perf["rank"],
                "start_value": perf["start_value"],
                "end_value": perf["end_value"],
                "percent_change": perf["percent_change"],
                "location_id": agent.get("location_id"),
                "energy": agent.get("energy"),
                "animal": persona.get("animal", ""),
                "gender": persona.get("gender", ""),
                "age_range": persona.get("age_range", ""),
                "occupation": persona.get("occupation", ""),
                "hobbies": ", ".join(persona.get("hobbies", [])),
                "portfolio_value": agent.get("portfolio_value", 0),
                "prompt": prompts.get(agent["id"], "")
            })

    return pd.DataFrame(all_rows)

# === Main CLI Runner ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch agent snapshots from terminal.markets")
    parser.add_argument("--include", type=str, required=True, help="Always include this player address")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_CSV, help="CSV file to append data to")
    args = parser.parse_args()

    top_players = get_top_players(always_include=args.include)
    df = build_dataframe(top_players)

    try:
        existing = pd.read_csv(args.output)
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv(args.output, index=False)
    print(f"Appended snapshot with {len(df)} total rows to {args.output}")