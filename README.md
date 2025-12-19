# Cross-Publication Insight Assistant

A system that enables users to discover patterns and trends across multiple AI/ML projects. Users can provide a list of GitHub repositories or publication identifiers (e.g., from Ready Tensor), and optionally include a natural-language query to guide the analysis, such as tool usage, evaluation methods, or task types.

## 🚀 Features

- 🔎 Explore cross-project patterns and relationships in AI/ML research.
- 📊 Summarize trends across repositories and publications.
- 💡 Respond to optional user queries to focus insights (e.g., specific tools or methods).
- 🧠 Combines repository metadata and publication data into human-interpretable insights.

## 🧱 Project Structure

├── backend/ # API server & data processing\
├── frontend/ # UI for interactive exploration\
├── .gitignore\
├── README.md\
└── .env

### Create a .env file
```
GOOGLE_API_KEY=your_google_api_key_here
```
> ⚙️ The backend handles data collection, processing, and analysis.  
> 🖥 The frontend is a React/JS client for visualizing insights.

## 📦 Installation

### Backend (Python)
Create and activate a virtual environment

```
cd backend
pip install -r requirements.txt
```
### Frontend (Next.js)
```
cd frontend
npm install
```
⚙️ Running Locally
### Start backend server
```
cd backend
uvicorn api:api --reload --port 8000
```
### Start frontend
```
cd frontend
npm run dev
```

Visit http://localhost:3000 in your browser to interact with the app.

📝 Usage

Enter a list of GitHub repository URLs or publication IDs.

Optionally add a query to focus the analysis.

Receive insights such as:

Which tools or libraries are common;

Frequent evaluation methods;

Trends across domains and tasks.

💡 Examples
```
# Example input
---
https://github.com/firstrepo
https://github.com/secondrepo
---
Query: "evaluation metrics used"
```
🧪 Testing

Add tests in a tests/ directory (optional but recommended).
Run tests with your framework of choice (e.g., Jest, PyTest).

📜 Contributing

Contributions and ideas are welcome! Please open issues or pull requests.

📄 License

Specify your license here (e.g., MIT, Apache 2.0).
