# Öğrenci Koçluk Sistemi V3

Kapsam: 5, 6, 7, 8/LGS, 9, 10, 11, 12/YKS ve Mezun/YKS.

## Özellikler
- Koç ve öğrenci girişi
- Sınıfa göre otomatik ders listesi
- Konu bazlı Doğru / Yanlış / Boş ve çalışma süresi
- Sınıfa göre uygun deneme türleri
- TYT, AYT ve LGS'de ders bazlı deneme girişi
- Haftalık soru ve süre hedefleri
- 48 saat yanlış tekrar listesi
- Koç kontrol merkezi
- Konu performansı
- Deneme net gelişim grafiği
- Haftalık veli raporu

## Çalıştırma
1. Python 3.11+ kurun.
2. `pip install -r requirements.txt`
3. `python app.py`
4. Tarayıcı: http://127.0.0.1:5000

Demo koç: `koc / 123456`
Demo öğrenci: `ogrenci / 123456`

Not: Gerçek internete açmadan önce SECRET_KEY, kullanıcı şifreleri, yedekleme ve HTTPS ayarları yapılmalıdır.
