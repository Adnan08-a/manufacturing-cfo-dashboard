import re
path = 'utils/styling.py'
content = open(path, encoding='utf-8').read()
old = re.search(r'def kpi_grid\(cards.*?st\.markdown\("".join\(parts\), unsafe_allow_html=True\)', content, re.DOTALL)
if old:
    new = 'def kpi_grid(cards: list[dict]) -> None:\n    cols = st.columns(len(cards))\n    for col, c in zip(cols, cards):\n        delta_html = ""\n        if c.get("delta"):\n            sign_class = c.get("delta_sign", "neutral")\n            delta_html = f\'<div class="kpi-delta {sign_class}">{c["delta"]}</div>\'\n        with col:\n            st.markdown(\n                f\'<div class="kpi-card">\'\n                f\'<div class="kpi-label">{c["label"]}</div>\'\n                f\'<div class="kpi-value">{c["value"]}</div>\'\n                f\'{delta_html}\'\n                f\'</div>\',\n                unsafe_allow_html=True,\n            )'
    content = content[:old.start()] + new + content[old.end():]
    open(path, 'w', encoding='utf-8').write(content)
    print('USPJESNO')
else:
    print('NIJE PRONADJENO - pokusavam drugaciji pristup')
    if 'parts = [' in content:
        print('NASAO parts = [')
