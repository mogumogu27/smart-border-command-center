# 🛡️ Serverless Smart Border Command Center

An automated, cloud-native IoT surveillance and threat-monitoring pipeline built with AWS (S3, Lambda, DynamoDB, SNS) and Streamlit.

## 📖 What is this project?
Traditional border monitoring relies heavily on manual oversight and localized servers. This project modernizes defense logistics by introducing a **serverless machine learning pipeline**. 

It simulates live IoT sensor data (motion and temperature) across 18 strategic border zones in India, automatically classifies the threat level using a custom Python logic model, and visualizes the active perimeter on a 3D georeferenced map. High-level threats automatically trigger an emergency email dispatch via AWS SNS.

## 🏗️ Cloud Architecture
* **Ingestion:** Simulated IoT sensor CSVs are generated and uploaded to **Amazon S3**.
* **Compute (Serverless):** An S3 trigger wakes up **AWS Lambda**, which extracts the data and runs a classification algorithm (`model_logic.py`) to determine Threat Levels (High/Medium/Low).
* **Persistence:** The processed telemetry is logged in a NoSQL **Amazon DynamoDB** table.
* **Command Dashboard:** A **Streamlit** frontend queries DynamoDB to render real-time interactive maps using **PyDeck**.
* **Alerting:** **Amazon SNS** dispatches automated emergency emails for "High" threat anomalies.

---

## 🚀 How to Try It (Local Setup)

To run this command center locally, you must have Python installed and your own AWS environment configured.

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/smart-border-command-center.git](https://github.com/your-username/smart-border-command-center.git)
cd smart-border-command-center