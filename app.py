def fetch_excel_from_github():
    if not GITHUB_TOKEN:
        if os.path.exists(EXCEL_FILE):
            try:
                return pd.read_excel(EXCEL_FILE).to_dict('records')
            except:
                return []
        return []
    
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{EXCEL_FILE}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            content_encoded = response.json().get("content", "")
            decoded_bytes = base64.b64decode(content_encoded)
            df = pd.read_excel(BytesIO(decoded_bytes))
            return df.to_dict('records')
    except:
        pass
    
    return []
