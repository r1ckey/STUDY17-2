import os
import json
import re

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
js_path = os.path.join(base_dir, "dashboard_data.js")
html_path = os.path.join(base_dir, "index.html")

# Define the structure of the study course
study_data = {
    "title": "STUDY17",
    "subtitle": "Data Engineering Mastery",
    "localStorageKey": "study17_de_progress",
    "themeColor": "#3b82f6", # Blue
    "secondaryColor": "#10b981", # Emerald
    "axes": [
        {
            "title": "1. Python & PySpark",
            "modules": [
                { "id": "17.1.1", "title": "Data Engineering Essentials", "path": "docs/python/index.md" },
                { "id": "17.1.2", "title": "PySpark Fundamentals", "path": "docs/python/pyspark.md" }
            ]
        },
        {
            "title": "2. Databricks Core",
            "modules": [
                { "id": "17.2.1", "title": "Lakehouse Architecture", "path": "docs/databricks/index.md" },
                { "id": "17.2.2", "title": "Arch: Control vs Data Plane", "path": "docs/databricks/architecture.md" },
                { "id": "17.2.3", "title": "Delta Lake Dynamics", "path": "docs/databricks/delta_lake.md" },
                { "id": "17.2.4", "title": "Performance & Optimization", "path": "docs/databricks/performance.md" }
            ]
        },
        {
            "title": "3. Modern Data Stack",
            "modules": [
                { "id": "17.3.1", "title": "dbt (Data Build Tool)", "path": "docs/dbt/index.md" },
                { "id": "17.3.2", "title": "Apache Airflow Mechanics", "path": "docs/airflow/index.md" }
            ]
        },
        {
            "title": "4. Cloud Certifications",
            "modules": [
                { "id": "17.4.1", "title": "GCP ACE Roadmap", "path": "docs/certifications/gcp_ace.md" },
                { "id": "17.4.2", "title": "Databricks Associate", "path": "docs/certifications/databricks_associate.md" },
                { "id": "17.4.3", "title": "Azure Data Engineer (DP-203)", "path": "docs/certifications/azure_de.md" }
            ]
        },
        {
            "title": "5. Projects & Portfolios",
            "modules": [
                { "id": "17.5.1", "title": "競馬データ分析基盤", "path": "docs/projects/keiba.md" }
            ]
        }
    ]
}

# 1. Generate dashboard_data.js
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
js_content += '    title: "STUDY17",\n'
js_content += '    subtitle: "Data Engineering Mastery",\n'
js_content += '    localStorageKey: "study17_de_progress",\n'
js_content += '    themeColor: "#3b82f6",\n'
js_content += '    secondaryColor: "#10b981",\n'
js_content += '    axes: ' + json.dumps(study_data["axes"], ensure_ascii=False, indent=4) + '\n};\n\n'
js_content += 'window.moduleContents = ' + json.dumps(contents_dict, ensure_ascii=False, indent=2) + ';\n'

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)


# 2. Generate index.html (STUDY8 / 13 style)
html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STUDY17: Data Engineering Mastery</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.6);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-primary: #3b82f6; /* Blue */
            --accent-secondary: #10b981; /* Emerald */
            --border-color: rgba(59, 130, 246, 0.3);
            --glass-bg: rgba(15, 23, 42, 0.8);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; cursor: default; }

        body {
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 40%);
            color: var(--text-primary);
            font-family: 'Outfit', 'Noto Sans JP', sans-serif;
            line-height: 1.6; overflow-x: hidden; min-height: 100vh;
        }

        .container {
            max-width: 1400px; margin: 0 auto; padding: 2rem;
            display: grid; grid-template-columns: 350px 1fr; gap: 2rem; height: 100vh;
        }

        #loader {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: var(--bg-color); display: flex; justify-content: center; align-items: center;
            z-index: 1000; transition: opacity 0.5s ease;
        }
        .spinner {
            width: 50px; height: 50px; border: 5px solid var(--card-bg);
            border-top: 5px solid var(--accent-primary); border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        .sidebar {
            background: #1e293b; border-right: 1px solid var(--border-color);
            padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem;
            overflow-y: auto; position: sticky; top: 0; height: calc(100vh - 4rem);
            border-radius: 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        .sidebar::-webkit-scrollbar { width: 6px; }
        .sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

        .header h1 {
            font-family: 'Outfit', sans-serif; font-size: 1.8rem;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;
        }
        .header p { color: var(--text-secondary); font-size: 0.9rem; }

        .search-box input {
            width: 100%; padding: 0.8rem 1rem; background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color); border-radius: 12px; color: white;
            font-size: 0.9rem; outline: none; transition: all 0.3s ease;
        }
        .search-box input:focus { border-color: var(--accent-primary); box-shadow: 0 0 15px rgba(59, 130, 246, 0.2); }

        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .stat-card {
            background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 16px;
            text-align: center; border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .stat-value { font-size: 1.4rem; font-weight: 800; color: var(--accent-primary); }
        .stat-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }

        .axis-group { margin-bottom: 1.5rem; }
        .axis-title {
            font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;
            letter-spacing: 2px; margin-bottom: 0.8rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;
        }
        .axis-title::after { content: ''; flex: 1; height: 1px; background: var(--border-color); }

        .module-list { list-style: none; display: flex; flex-direction: column; gap: 0.4rem; }
        .module-item {
            padding: 0.8rem 1rem; border-radius: 10px; background: transparent;
            border: 1px solid transparent; cursor: pointer; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex; align-items: center; gap: 0.8rem;
        }
        .module-item:hover { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); transform: translateX(5px); }
        .module-item.active { background: linear-gradient(90deg, rgba(59, 130, 246, 0.2), transparent); border-left: 4px solid var(--accent-primary); }
        .module-id { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--accent-secondary); font-weight: 600; }
        .module-title-text { font-size: 0.85rem; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; max-width: 150px; }
        .module-check { margin-left: auto; width: 14px; height: 14px; border: 2px solid var(--accent-primary); border-radius: 4px; opacity: 0.3; }
        .module-item.completed .module-check { background: var(--accent-primary); opacity: 1; box-shadow: 0 0 8px var(--accent-primary); }

        .main-content {
            background: #111827; border-radius: 24px; border: 1px solid var(--border-color);
            overflow-y: auto; position: relative; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); display: flex; flex-direction: column;
        }
        .main-content::-webkit-scrollbar { width: 8px; }
        .main-content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

        .dashboard-home { padding: 3rem; display: flex; flex-direction: column; gap: 3rem; }
        .welcome-hero {
            text-align: center; padding: 4rem 2rem;
            background: radial-gradient(circle at center, rgba(16, 185, 129, 0.1) 0%, transparent 70%); border-radius: 20px;
        }
        .welcome-hero h2 { font-family: 'Outfit', sans-serif; font-size: 3rem; margin-bottom: 1rem; color: white; }

        .radar-container {
            width: 100%; max-width: 600px; margin: 0 auto; background: rgba(255, 255, 255, 0.02);
            padding: 2rem; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .viewer { padding: 3rem; display: none; animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .content-meta {
            margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);
            display: flex; justify-content: space-between; align-items: center; position: sticky; top: -3rem; background: #111827; z-index: 10;
        }
        .btn-complete {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); border: none;
            padding: 0.8rem 2rem; border-radius: 12px; color: white; font-weight: 700; cursor: pointer; transition: all 0.3s ease;
        }
        .btn-complete:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(59, 130, 246, 0.4); }

        .markdown-body h1 { color: var(--accent-secondary); border-bottom: 2px solid var(--accent-primary); padding-bottom: 0.5rem; margin: 2rem 0 1rem; }
        .markdown-body h2 { color: var(--accent-primary); margin: 1.5rem 0 1rem; }
        .markdown-body h3 { color: #f8fafc; margin: 1.2rem 0 0.8rem; }
        .markdown-body p { margin-bottom: 1rem; font-size: 1.05rem; }
        .markdown-body pre { background: #011627; padding: 1.5rem; border-radius: 12px; overflow-x: auto; margin: 1.5rem 0; border: 1px solid rgba(255, 255, 255, 0.1); }
        .markdown-body code { font-family: 'JetBrains Mono', monospace; color: #82aaff; }
        .markdown-body blockquote { border-left: 4px solid var(--accent-secondary); background: rgba(16, 185, 129, 0.1); padding: 1rem; margin: 1.5rem 0; font-style: italic; }
        .markdown-body ul { padding-left: 1.5rem; margin-bottom: 1rem; }
        .markdown-body li { margin-bottom: 0.5rem; }
        .mermaid { background: transparent; padding: 1rem 0; text-align: center; }

        @media (max-width: 1000px) {
            .container { grid-template-columns: 1fr; height: auto; padding: 1rem; gap: 1rem; }
            .sidebar { position: relative; height: auto; width: 100%; max-height: 400px; padding: 1.5rem; }
            .welcome-hero h2 { font-size: 2rem; }
            .viewer { padding: 1.5rem; }
            .content-meta { position: relative; top: 0; }
        }
    </style>
</head>
<body>

    <div id="loader"><div class="spinner"></div></div>

    <div class="container">
        <aside class="sidebar">
            <header class="header">
                <h1 id="portal-title">STUDY17</h1>
                <p id="portal-subtitle">Data Engineering</p>
            </header>

            <div class="search-box">
                <input type="text" id="search-input" placeholder="モジュールを検索...">
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="total-progress">0%</div>
                    <div class="stat-label">Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="completed-count">0/0</div>
                    <div class="stat-label">Modules</div>
                </div>
            </div>

            <nav id="axis-list"></nav>
        </aside>

        <main class="main-content">
            <div id="dashboard-home" class="dashboard-home">
                <section class="welcome-hero">
                    <h2 id="hero-title">Master Data Engineering.</h2>
                    <p>Azure, Databricks, PySpark, dbt によるモダンデータスタックを完全網羅。</p>
                </section>

                <div class="radar-container">
                    <canvas id="masteryRadar"></canvas>
                </div>
            </div>

            <div id="viewer" class="viewer">
                <div class="content-meta">
                    <span id="current-id" class="module-id" style="font-size: 1.2rem;"></span>
                    <button class="btn-complete" id="mark-complete-btn">完了としてマーク</button>
                </div>
                <div id="markdown-content" class="markdown-body"></div>
            </div>
        </main>
    </div>

    <script src="dashboard_data.js"></script>
    <script>
        let masteryData = JSON.parse(localStorage.getItem(studyData.localStorageKey)) || {};
        let currentModuleId = null;
        let radarChart = null;

        function init() {
            document.getElementById('portal-title').textContent = studyData.title;
            document.getElementById('portal-subtitle').textContent = studyData.subtitle;
            renderAxes();
            updateGlobalStats();
            initRadar();
            
            mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });
            
            marked.use({
                renderer: {
                    code(token) {
                        if (token.lang === 'mermaid') {
                            return `<div class="mermaid">${token.text}</div>`;
                        }
                        return `<pre><code class="language-${token.lang}">${token.text}</code></pre>`;
                    }
                }
            });

            setTimeout(() => {
                document.getElementById('loader').style.opacity = '0';
                setTimeout(() => document.getElementById('loader').remove(), 500);
            }, 800);

            document.getElementById('search-input').addEventListener('input', handleSearch);
        }

        function renderAxes() {
            const list = document.getElementById('axis-list');
            list.innerHTML = '';
            studyData.axes.forEach(axis => {
                const group = document.createElement('div');
                group.className = 'axis-group';
                group.innerHTML = `<div class="axis-title">${axis.title}</div>`;
                
                const ul = document.createElement('ul');
                ul.className = 'module-list';
                axis.modules.forEach(mod => {
                    const isCompleted = masteryData[mod.id];
                    const li = document.createElement('li');
                    li.className = `module-item ${isCompleted ? 'completed' : ''}`;
                    li.id = `nav-${mod.id}`;
                    li.onclick = () => loadModule(mod.id);
                    li.innerHTML = `
                        <span class="module-id">${mod.id}</span>
                        <span class="module-title-text" title="${mod.title}">${mod.title}</span>
                        <div class="module-check"></div>
                    `;
                    ul.appendChild(li);
                });
                group.appendChild(ul);
                list.appendChild(group);
            });
        }

        async function loadModule(id) {
            currentModuleId = id;
            const container = document.getElementById('dashboard-home');
            const viewer = document.getElementById('viewer');
            const mdContent = document.getElementById('markdown-content');
            
            container.style.display = 'none';
            viewer.style.display = 'block';
            
            const axis = studyData.axes.find(a => a.modules.some(m => m.id === id));
            const mod = axis.modules.find(m => m.id === id);
            
            document.getElementById('current-id').textContent = mod.id;
            document.querySelectorAll('.module-item').forEach(el => el.classList.remove('active'));
            document.getElementById(`nav-${id}`).classList.add('active');

            try {
                let text = "";
                if (window.moduleContents && window.moduleContents[id]) {
                    text = window.moduleContents[id];
                } else {
                    const response = await fetch(mod.path);
                    if (!response.ok) throw new Error('File not found');
                    text = await response.text();
                }
                
                mdContent.innerHTML = marked.parse(text);
                if (window.mermaid) { setTimeout(() => { mermaid.init(undefined, ".mermaid"); }, 20); }
                document.querySelector('.main-content').scrollTop = 0;
            } catch (e) {
                mdContent.innerHTML = `<h1>Coming Soon</h1><p>モジュール ${id} (${mod.title}) は現在執筆中です。</p>`;
            }

            updateCompleteBtn(id);
        }

        function updateCompleteBtn(id) {
            const btn = document.getElementById('mark-complete-btn');
            if (masteryData[id]) {
                btn.textContent = '完了済み'; btn.style.opacity = '0.6';
            } else {
                btn.textContent = '完了としてマーク'; btn.style.opacity = '1';
            }
            btn.onclick = () => toggleComplete(id);
        }

        function toggleComplete(id) {
            masteryData[id] = !masteryData[id];
            localStorage.setItem(studyData.localStorageKey, JSON.stringify(masteryData));
            
            const navItem = document.getElementById(`nav-${id}`);
            if (masteryData[id]) navItem.classList.add('completed');
            else navItem.classList.remove('completed');
            
            updateGlobalStats(); updateCompleteBtn(id); updateRadar();
        }

        function updateGlobalStats() {
            const total = studyData.axes.reduce((acc, axis) => acc + axis.modules.length, 0);
            const completed = Object.values(masteryData).filter(v => v).length;
            const percentage = total === 0 ? 0 : Math.round((completed / total) * 100);
            
            document.getElementById('total-progress').textContent = `${percentage}%`;
            document.getElementById('completed-count').textContent = `${completed}/${total}`;
            document.getElementById('hero-title').textContent = percentage === 100 ? "Data Engineering Architect!" : "Master Data Engineering.";
        }

        function handleSearch(e) {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.module-item').forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(term) ? 'flex' : 'none';
            });
        }

        function initRadar() {
            const ctx = document.getElementById('masteryRadar').getContext('2d');
            const labels = studyData.axes.map(a => a.title.split('. ')[1] || a.title);
            const data = studyData.axes.map(axis => {
                const completed = axis.modules.filter(m => masteryData[m.id]).length;
                return axis.modules.length === 0 ? 0 : (completed / axis.modules.length) * 100;
            });

            radarChart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Mastery Level (%)', data: data,
                        backgroundColor: 'rgba(59, 130, 246, 0.2)', borderColor: studyData.themeColor,
                        pointBackgroundColor: studyData.secondaryColor, borderWidth: 3
                    }]
                },
                options: {
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            pointLabels: { color: '#94a3b8', font: { size: 10 } },
                            ticks: { display: false, stepSize: 20 }, suggestedMin: 0, suggestedMax: 100
                        }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        function updateRadar() {
            radarChart.data.datasets[0].data = studyData.axes.map(axis => {
                const completed = axis.modules.filter(m => masteryData[m.id]).length;
                return axis.modules.length === 0 ? 0 : (completed / axis.modules.length) * 100;
            });
            radarChart.update();
        }

        window.onload = init;
    </script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully configured index.html and dashboard_data.js for STUDY17!")
