# E-Paper Bot

A tool designed to automate downloading of Kannada e-papers from official sources:

- [Kannada Prabha E-Paper](https://kpepaper.asianetnews.com/)
- [Vishwavani E-Paper](https://epaper.vishwavani.news/)
- [Hosa Digantha E-Paper](https://epaper.hosadigantha.com/)

Features a simple web interface for accessing downloaded papers and automated daily downloads via GitHub Actions.

[![E-paper bot](https://github.com/sankethsj/newspaper-bot/actions/workflows/python-app.yml/badge.svg)](https://github.com/sankethsj/newspaper-bot/actions/workflows/python-app.yml)

## Website

Access downloaded papers: [E-Paper Bot](https://sankethsj.github.io/epaper/)

## Legal Notice

This tool is for personal, non-commercial use only. All content rights belong to their respective owners:

- Kannada Prabha © Asianet News Media and Entertainment Pvt Ltd
- Vishwavani © Vishwavani Daily
- Hosa Digantha © Hosa Digantha

## Setup and Usage

### Installation

```bash
git clone https://github.com/sankethsj/newspaper-bot.git
cd newspaper-bot
pip install -r requirements.txt
```

### Running Locally

```bash
python app.py
```

Access the web interface at `http://localhost:5000`

## Project Structure

```plaintext
paperbot/
  ├── kannada_prabha.py  # Kannada Prabha download logic
  ├── vishwavani.py      # Vishwavani download logic
  ├── hosadigantha.py    # Hosa Digantha download logic
  └── utils.py           # Shared utilities (PDF merging, date handling, etc.)
```

## Contributing

For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)
