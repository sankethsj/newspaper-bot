# AI Agent Instructions for newspaper-bot

## Project Overview
This is a Flask-based web application that automates downloading the Kannada Prabha e-paper. The project consists of two main components:
1. A web interface (`webapp/`) for viewing and downloading papers
2. An automated bot (`bot.py`) that fetches and compiles daily newspapers

## Key Architecture Components

### Bot Component (`bot.py`)
- Downloads newspaper pages in parallel using ThreadPool
- Uses temporary storage (`tmp/`) for individual pages before merging
- Automatically cleans up files older than 7 days
- Key functions:
  - `get_page_count()`: Fetches total pages for an issue
  - `download_pdf()`: Downloads individual pages
  - `export_to_single_df()`: Merges pages into single PDF

### Web Application (`webapp/`)
- Flask blueprint architecture in `webapp/views.py`
- Uses GitHub API to fetch paper list from repository
- Simple templates in `webapp/templates/` for rendering views

## Development Patterns

### File Naming Conventions
- PDF files follow pattern: `ISSUE-ID_REGION_YYYYMMDD.pdf`
  Example: `KANPRABHA_MN_20240120.pdf`
- PDF pages follow pattern: `YYYYMMDD_PP.PDF` where PP is zero-padded page number

### Data Flow
1. Bot fetches page count from enewspapr.com API
2. Downloads individual pages in parallel to `tmp/` directory
3. Merges pages into single PDF in `output/` directory
4. Web interface lists files from GitHub repository output folder

### Environment Setup
```bash
pip install -r requirements.txt
python app.py  # Runs on http://localhost:5000
```

### Key Configuration
- Default newspaper: Kannada Prabha Mangalore Edition (KANPRABHA_MN)
- Files auto-delete after 7 days
- ThreadPool size: 8 workers for parallel downloads

## Integration Points
1. enewspapr.com API for page details and PDF downloads
2. GitHub API for serving paper list through web interface

## Common Operations
- Running bot: `python bot.py`
- Accessing web interface: Run `app.py` and visit http://localhost:5000
- Finding specific paper: Check `output/` directory with YYYYMMDD format

## Error Handling
- Bot handles missing papers gracefully
- Web interface shows download error page for invalid requests
- ThreadPool ensures reliable parallel downloads

## Testing
Currently no automated tests. When adding tests, focus on:
- PDF download reliability
- Page count verification
- File cleanup logic