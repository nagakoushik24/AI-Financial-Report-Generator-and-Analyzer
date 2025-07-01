import requests

def fetch_sec_filing_by_year(cik, doc_type, year):
    cik_str = str(cik).lstrip('0').zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
    headers = {'User-Agent': 'Naga Koushik nagakoushik24@gmail.com'}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch SEC data"}
    
    data = response.json()
    filings = data.get("filings", {}).get("recent", {})
    
    for i in range(len(filings.get("form", []))):
        if filings["form"][i] == doc_type:
            filing_year = filings["filingDate"][i].split("-")[0]
            if filing_year == str(year):
                accession = filings["accessionNumber"][i].replace("-", "")
                primary_doc = filings["primaryDocument"][i]
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"
                return {
                    "companyName": data.get("name"),
                    "CIK": cik_str,
                    "formType": doc_type,
                    "filingDate": filings["filingDate"][i],
                    "filingURL": filing_url
                }

    return {"message": f"No {doc_type} filing found for year {year}"}


def download_pdf(url, save_path="temp_sec_filing.pdf"):
    """
    Downloads the PDF from SEC and saves it locally.
    Returns the path to the saved file or None on failure.
    """
    headers = {'User-Agent': 'Naga Koushik <nagakoushik24@gmail.com>'}  # Customize this
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return save_path
        else:
            print(f"Failed to download: {response.status_code}")
            return None
    except Exception as e:
        print("Error downloading PDF:", e)
        return None
