import json
from datetime import datetime

import firebase_admin
import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore


def scrape_and_store_bist(request):
    # Firebase ile bağlantı kurmak için serviceAccountKey.json dosyasını kullanın
    cred = credentials.Certificate('path/to/your-serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

    # Firestore istemcisini oluştur
    db = firestore.client()

    # Web sitesine istekte bulunma
    url = 'https://tr.tradingview.com/symbols/BIST-XU100/'
    response = requests.get(url)

    # HTML içeriğini parse etme
    soup = BeautifulSoup(response.content, 'html.parser')

    # HTML içeriğini prettify ile alalım
    html_content = soup.prettify()

    # İlgili soruyu ve cevabı metin olarak arayalım
    search_text = "Bugün BIST 100 Endeksi değeri nedir?"
    start_index = html_content.find(search_text)

    # Eğer soruyu bulursak, cevabı bulmaya çalışalım
    if start_index != -1:
        # Soru bulundu, şimdi cevabı bulalım
        end_index = html_content.find('"acceptedAnswer"', start_index)

        # Bulunan cevabın olduğu bölümü alalım
        answer_snippet = html_content[start_index:end_index + 500]

        # Cevap bölümünden sadece değeri çekelim
        value_start = answer_snippet.find("BIST 100 Endeksi geçerli değeri") + len("BIST 100 Endeksi geçerli değeri")
        value_end = answer_snippet.find("TRY", value_start)

        # Değerin bulunduğu kısmı izole edelim
        bist_value = answer_snippet[value_start:value_end].strip()

        print(f"BIST 100 Endeks Değeri: {bist_value} TRY")

        # Mevcut tarih için BIST değerini Firestore'a kaydedelim
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Firestore koleksiyonuna kaydetme
        doc_ref = db.collection('BIST_index_daily').document(current_date)
        doc_ref.set({
            'date': current_date,
            'BIST_value': bist_value
        })

        return f"{current_date} tarihli BIST 100 endeks değeri başarıyla kaydedildi."
    else:
        return "Soru bulunamadı."
