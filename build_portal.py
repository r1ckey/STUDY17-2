import os
import json

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
js_path = os.path.join(base_dir, "dashboard_data.js")

study_data = {
    "title": "DATA ENGINERING (Ultimate)",
    "subtitle": "Kazaneya Data Engineering Track",
    "localStorageKey": "study17_ultimate_progress",
    "themeColor": "#3b82f6",
    "secondaryColor": "#10b981",
    "axes": [
        {
            "title": "1. Python Data Foundation",
            "modules": [
                { "id": "17.1.1", "title": "Core Python (Generators/Typing)", "path": "docs/python/core.md" },
                { "id": "17.1.2", "title": "Pandas vs Polars (Memory)", "path": "docs/python/pandas.md" }
            ]
        },
        {
            "title": "2. PySpark Mastery",
            "modules": [
                { "id": "17.2.1", "title": "Distributed Computing & Partitions", "path": "docs/pyspark/distributed.md" },
                { "id": "17.2.2", "title": "Lazy Evaluation & Catalyst", "path": "docs/pyspark/lazy_eval.md" },
                { "id": "17.2.3", "title": "Shuffle vs Broadcast Joins", "path": "docs/pyspark/joins.md" }
            ]
        },
        {
            "title": "3. Databricks Core",
            "modules": [
                { "id": "17.3.1", "title": "Control & Data Plane", "path": "docs/databricks/architecture.md" },
                { "id": "17.3.2", "title": "Delta Lake Acid & Time Travel", "path": "docs/databricks/delta_lake.md" },
                { "id": "17.3.3", "title": "Performance Optimization", "path": "docs/databricks/performance.md" },
                { "id": "17.3.4", "title": "Auto Loader (Streaming)", "path": "docs/databricks/autoloader.md" }
            ]
        },
        {
            "title": "4. Modern Data Stack",
            "modules": [
                { "id": "17.4.1", "title": "ELT vs ETL Paradigm Shift", "path": "docs/dbt/elt.md" },
                { "id": "17.4.2", "title": "dbt Models & Mechanics", "path": "docs/dbt/index.md" },
                { "id": "17.4.3", "title": "dbt Testing & Documentation", "path": "docs/dbt/testing.md" },
                { "id": "17.4.4", "title": "Apache Airflow Orchestration", "path": "docs/airflow/index.md" }
            ]
        },
        {
            "title": "5. Certifications",
            "modules": [
                { "id": "17.5.1", "title": "GCP ACE", "path": "docs/certifications/gcp_ace.md" },
                { "id": "17.5.2", "title": "Databricks Associate", "path": "docs/certifications/databricks_associate.md" },
                { "id": "17.5.3", "title": "Azure Data Engineer", "path": "docs/certifications/azure_de.md" }
            ]
        },
        {
            "title": "6. Projects",
            "modules": [
                { "id": "17.6.1", "title": "競馬分析基盤 (Keiba Project)", "path": "docs/projects/keiba.md" }
            ]
        }
    ]
}

contents_dict = {}

for axis in study_data["axes"]:
    for mod in axis["modules"]:
        rel_path = mod["path"].replace("/", os.sep)
        full_path = os.path.join(base_dir, rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                contents_dict[mod["id"]] = f.read()
        else:
            contents_dict[mod["id"]] = f"# Coming Soon\n\n{mod['title']} は現在執筆中です。"

js_content = "const studyData = {\n"
js_content += '    title: "DATA ENGINEERING",\n'
js_content += '    subtitle: "Roadmap Mastery",\n'
js_content += '    localStorageKey: "study17_ultimate_progress",\n'
js_content += '    themeColor: "#3b82f6",\n'
js_content += '    secondaryColor: "#10b981",\n'
js_content += '    axes: ' + json.dumps(study_data["axes"], ensure_ascii=False, indent=4) + '\n};\n\n'
js_content += 'window.moduleContents = ' + json.dumps(contents_dict, ensure_ascii=False, indent=2) + ';\n'

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print("Successfully generated ULTIMATE roadmap bundle in dashboard_data.js")
