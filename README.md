# Customer-Journey-Analyzer
Understand how customers move through your funnel: acquisition → activation → conversion → retention.   This project analyzes drop-offs, retention by cohort, and channel impact, then surfaces simple, actionable insights.

### What It Does
- Loads event data (mock CSV) for users, dates, funnel stages, and channels
- Calculates funnel conversion and stage-by-stage drop-off
- Builds monthly cohorts and retention curves
- Highlights channel contribution and lift
- Optional Streamlit dashboard for quick exploration

### Example Insights (mock)
- Activation rate: **62%**, Conversion rate: **31%**
- Top activation channel: **Organic**
- Retention at D+30: **44%** for users acquired via LinkedIn

### Tech Stack
 **Python** for analysis
 **Pandas / Numpy** for data wrangling
 **Plotly / Streamlit** for visualization

### Why I Built It
Teams often spend more time debating metrics than improving them.  
This repo demonstrates a clear, repeatable way to view the journey and decide where to act next.

### How to Run
```bash
# create env (optional)
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# install deps
pip install -r requirements.txt

# print console summary
python main.py

# launch dashboard
streamlit run app.py
