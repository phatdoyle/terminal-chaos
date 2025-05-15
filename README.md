# Terminal Markets Agent Snapshot Logger

This Python script fetches and logs agent data from Terminal Markets, including player performance, agent details, and prompts.

## Features

- Fetches top players' performance data
- Retrieves agent information for each player
- Collects agent prompts
- Saves all data to a CSV file for analysis
- Supports including specific player addresses in the data collection. This can be used to include your address for comparative analysis. 

## Prerequisites

- Python 3.x
- Required Python packages:
  - requests
  - pandas

## Installation

1. Clone this repository or download the script
2. Install required packages:
```bash
pip install requests pandas
```

## Usage

Run the script with your player address:

```bash
python main.py --include YOUR_PLAYER_ADDRESS
```

### Command Line Arguments

- `--include`: (Required) Your player address to always include in the data collection
- `--output`: (Optional) Specify a custom output CSV file name (default: `agent_snapshot_log.csv`)

Example:
```bash
python main.py --include 0x123...abc --output my_agents.csv
```

## Output

The script generates a CSV file containing:
- Timestamp of data collection
- Agent details (ID, name, type, condition)
- Player performance metrics
- Agent persona information
- Portfolio values
- Agent prompts

## Data Structure

The CSV file includes the following columns:
- timestamp
- agent_id
- name
- type
- condition
- company_id
- player_id
- rank
- start_value
- end_value
- percent_change
- location_id
- energy
- animal
- gender
- age_range
- occupation
- hobbies
- portfolio_value
- prompt

## Notes

- The script includes rate limiting to avoid overwhelming the API
- Data is appended to the existing CSV file if it exists
- If the output file doesn't exist, a new one will be created

## API Endpoints Used

- Performance API: `https://terminal.markets/api/analytics/players/performance`
- Agents API: `https://terminal.markets/api/agents/player`
- Prompts API: `https://terminal.markets/api/agents/prompts` 