# DenisOS

Your personal digital codex - an interactive notebook for life, work, and wisdom.

*"Hello, Denis. I am your Codex."*

## Quick Start

```bash
cd denis_os
docker-compose up --build
```

Open `http://localhost:8501` in your browser.

## Deployment Guide

### Phase 1: Local Testing

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Open terminal in the `denis_os` folder
3. Run:
   ```bash
   docker-compose up --build
   ```
4. Visit `http://localhost:8501`

### Phase 2: Access from Phone (Local Network)

Use the Timber Calc in your workshop without cloud deployment:

1. Find your computer's local IP:
   - **Mac**: System Settings > Network > Wi-Fi > Details
   - **Windows**: Run `ipconfig` in terminal
   - **Linux**: Run `ip addr` or `hostname -I`

2. On your phone (same Wi-Fi), go to `http://YOUR_IP:8501`
   - Example: `http://192.168.1.15:8501`

### Phase 3: Cloud Deployment

Access from anywhere (lumber yard, job site, etc.):

1. Rent a VPS ($5/mo DigitalOcean Droplet, Linode, etc.)

2. Install Docker on the server:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   ```

3. Copy files to server:
   ```bash
   scp -r denis_os/ user@your-server-ip:~/
   ```

4. SSH in and run:
   ```bash
   ssh user@your-server-ip
   cd denis_os
   docker-compose up -d
   ```

5. **(Recommended)** Secure access with [Tailscale](https://tailscale.com/):
   - Install on server and phone
   - Access via Tailscale IP (no port forwarding needed)
   - Private network, no public exposure

## Modules

| Module | Description |
|--------|-------------|
| **Finance** | Track expenses, income, budgets. Monthly summaries. |
| **Carpentry** | Lumber calculator, project estimator, price reference. |
| **Philosophy** | Journal, daily reflection prompts, collected wisdom. |

## Data Persistence

Your data lives in `data/codex_data.json`. The Docker volume mount ensures:
- Data survives container restarts
- You can edit files locally and see changes immediately
- Backups are just file copies

## Configuration

Edit `config.json` to customize:
- Your name and timezone
- Currency (CAD/USD/EUR/GBP)
- Measurement units (imperial/metric)
- Module settings

## Project Structure

```
denis_os/
├── main.py              # App entry point
├── modules/
│   ├── finance.py       # Money tracking
│   ├── carpentry.py     # Lumber calculations
│   └── philosophy.py    # Journal & reflections
├── utils/
│   ├── config.py        # Settings manager
│   └── data_manager.py  # Data persistence
├── data/                # Your codex data
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Without Docker

```bash
pip install -r requirements.txt
streamlit run main.py
```

---

*"The unexamined life is not worth living." - Socrates*
