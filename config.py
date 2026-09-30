# -*- coding: utf-8 -*-
"""
Genel ayarlar.
 
RSS_FEEDS: taranacak haber kaynakları.
Bu adresler zamanla değişebilir/kırılabilir — bot her feed'i ayrı ayrı
dener, biri hata verirse diğerlerini etkilemez. Yeni bir kaynak eklemek
için buraya (isim, url) çifti eklemen yeterli.
"""
 
RSS_FEEDS = [
    ("Hürriyet", "https://www.hurriyet.com.tr/rss/anasayfa"),
    ("NTV", "https://www.ntv.com.tr/gundem.rss"),
    ("Sözcü", "https://www.sozcu.com.tr/rss/tum-haberler.xml"),
    ("Cumhuriyet", "https://www.cumhuriyet.com.tr/rss"),
]
 
# Kaç saniyede bir kontrol edilecek (3600 = 1 saat)
POLL_INTERVAL_SECONDS = 120
 
# Bot ilk açıldığında kaç saniye sonra ilk taramayı yapsın
FIRST_RUN_DELAY_SECONDS = 10
 