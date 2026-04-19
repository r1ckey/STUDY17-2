import os
path = r'C:\Users\jorda\Documents\ANTIGRAVITY\study17\build_portal.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('js_content = f"const studyData = {\\n"', 'js_content = "const studyData = {\\n"')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
