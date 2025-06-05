# Restoration-Intel: Business Intelligence Platform

## 🚀 Project Overview

Restoration-Intel is a comprehensive business intelligence platform designed to provide deep insights into financial metrics, operational efficiency, and strategic decision-making for restoration businesses.

### Key Features
- Advanced Cash Flow Forecasting
- Operational Metrics Tracking
- Predictive Business Health Alerts
- Comprehensive Financial Analytics
- Vendor and Collections Management

## 🛠 Prerequisites

Before you begin, ensure you have the following installed:
- Docker Desktop
- Docker Compose
- Python 3.11+
- Node.js 18.x
- npm 9.x
- Git

## 💻 Quick Start

### Automatic Setup (Recommended)

#### For Unix/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

#### For Windows:
```cmd
setup.bat
```

### Manual Setup

1. Clone the Repository
```bash
git clone https://github.com/your-org/restoration-intel.git
cd restoration-intel
```

2. Create Environment Files
```bash
cp .env.docker.example .env.docker
cp next-app/.env.local.example next-app/.env.local
```

3. Install Dependencies
```bash
npm install
cd next-app
npm install
cd ..
pip install -r requirements.txt
```

4. Start Docker Services
```bash
docker-compose up --build
```

## 🔍 Services

- **Next.js Frontend**: http://localhost:3000
- **FastAPI Backend**: http://localhost:8000
- **Supabase**: http://localhost:54321

## 📊 Key Metrics Covered

### Phase 1: Immediate Cash Flow Stabilization
- Daily Cash Position
- Cash Conversion Cycle
- Accounts Receivable Aging
- Weekly Cash Flow Forecast

### Phase 2: Operational Efficiency
- Revenue Per Job
- Job Completion Rate
- Customer Acquisition Cost
- Technician Utilization

### Phase 3: Profitability Optimization
- Gross Margin Analysis
- Job-Level Profitability
- Inventory Turnover

## 🛡️ Security Features

- Non-root Docker containers
- Environment-based configuration
- Secure secret management
- Flexible authentication mechanisms

## 🔧 Troubleshooting

Refer to:
- `DOCKER_TROUBLESHOOTING.md` for Docker-related issues
- `STARTUP_GUIDE.md` for detailed setup instructions

## 📝 Configuration

### Environment Variables
- `.env.docker`: Docker and service configurations
- `next-app/.env.local`: Next.js specific environment variables

### Customization
- Modify `requirements.txt` to update Python dependencies
- Adjust `docker-compose.yml` for service configurations

## 🚧 Development Workflow

### Starting Services
```bash
docker-compose up
```

### Stopping Services
```bash
docker-compose down
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

[Specify your project's license]

## 📞 Contact

[Your contact information or support channels]

---

**Note**: This project is under active development. Features and configurations may change rapidly.