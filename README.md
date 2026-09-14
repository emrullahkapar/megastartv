# ⚽ fixbet-bot

Fixbet TV kaynağından **güncel site adresini** sürekli takip eden, **maç ID'lerini** çeken,
**günün maçlarını kategorize eden** ve **canlı / yaklaşan / günün maçı / lig & spor bazlı**
raporlar üreten gelişmiş otomasyon botu.

## Player ve skor güncellemesi

- Atom'un güncel `/matches?id=...` player yolu ve worker → nihai HLS çözümlemesi;
  master/media, göreli URI ve imzalı query desteği.
- Gerçek oynatma/loading, sınırlı retry/kurtarma, stall kontrolü, açıklayıcı loglar;
  Chromium MSE/hls.js ve Apple native HLS ayrımı.
- Günün maçlarında **CANLI / DEVRE / MS + küçük skor**, ertelendi/iptal durumları.
  Asıl kaynak skor vermediğinde tanımlı ligler için ESPN'den kesin eşleşmeyle alınır;
  eksik skor tahmin edilmez veya 0–0 yapılmaz.
- Header/CORS isteyen kaynaklar için isteğe bağlı, izin listeli HLS hizmeti.
  **GitHub Pages backend çalıştırmaz:** gerekli hizmet ayrıca HTTPS ile deploy
  edilip `playback.proxy_url` ayarlanmalıdır; varsayılan doğrudan yayınlar korunur.

**İnceleme bulguları, doğrulama sınırları, deployment ve skor kapsamı:**
[Player / skor işletim notları](docs/PLAYER-SCORES.md).

## 🧠 Nasıl çalışır?

1. **Güncel adres takibi** (`src/fixbet/domain_checker.py`)
   - fixbettv adresleri numaralı aynalardır (fixbettv84.com, fixbettv85.com, …).
   - `config/mirrors.yml` içindeki kalıp ve aralıktaki adayları HTTP sağlık kontrolünden geçirir.
   - Çalışan adresleri bulur, en güvenilir/güncel olanı seçer ve
     `config/current_site.yml` dosyasına yazar. → **Linki her zaman güncel tutar.**

2. **Maç ID çekme** (`src/fixbet/scraper.py`, `parser.py`)
   - Sitenin maç listesinin geldiği stabil kaynaktan ham HTML çekilir
     (`data-reality.com/matches.php`, yedeği `matches2.php`).
   - Her satırın kanal kimliği (`channel?id=<id>`) ve takım/lig/kategori bilgileri çıkarılır.
     Bu kimlik gün içinde tekrar edebilir; skor eşleştirmesi için etkinlik ID'si sayılmaz.

3. **Durum ve skor** (`src/fixbet/match_state.py`, `scores.py`, `categorizer.py`)
   - Önce kaynağın gerçek durumu kullanılır: **CANLI / DEVRE / MS / Ertelendi / İptal**.
   - Kaynak skor/durum vermiyorsa `config/scores.yml` içindeki ligler ESPN scoreboard
     ile zenginleştirilir (spor/lig/tarih/saat ve iki takımın kesin eşleşmesi).
   - Hiç gerçek durum yoksa eski saat tabanlı canlı/yaklaşan/bitti tahmini korunur;
     bu tahminden skor üretilmez.
   - `[Günün Maçı]` etiketiyle **⭐ Günün Maçı** kategorisi oluşturulur.
   - **Spor** ve **Lig** bazlı alt gruplar üretilir.

4. **7/24 Kanallar** (`src/fixbet/channels.py`)
   - Güncel adresin ana sayfasındaki kanal listesi çekilir (id + ad + durum).
   - **Marka bazında** kategorize edilir (Bein Sports, Tabii, TRT, SmartSpor, …).
   - `output/channels.json` dosyasına yazılır ve raporlara eklenir.

5. **GitHub Pages sayfası** (`src/fixbet/site.py` + `src/fixbet/templates/index.html`)
   - Repo kökündeki **`index.html`** her çalıştırmada şablondan yeniden üretilir
     (tek kaynak: şablon). Sayfada **uydurma/sabit maç yoktur**; gömülen her maç
     kaynaktan çekilen gerçek programdır.
   - **Üç sekme:** 📺 TV KANALLARI, 📅 GÜNÜN MAÇLARI ve **⚡ EXTRA PANELLER**. Eski "canlı maçlar"
     sekmesi sabit örnek veriyle dolduğu için kaldırıldı — canlılık bilgisi artık günün maçları
     içinde **kaynak durumu varsa ondan, yoksa program saatinden** belirleniyor.
   - **Yedek durum hesabı:** Gerçek durum gelmediğinde başlangıç saati + spora göre yayın penceresi
     (`settings.yml → categorize.live_window_by_sport`) → 🔴 Canlı / ⏰ Yaklaşan /
     ✅ Bitti. Aynı tablo sayfaya da gömülür, yani bot ile site aynı şeyi söyler.
     Sayaçlar ("1 sa 20 dk kaldı", "≈ 63'") 30 sn'de bir tazelenir; programın saat
     dilimi korunur. Gerçek kaynak durumu saatten gelen tahminle ezilmez.
   - **Skor:** Tamamlanan maçta MS + final skor; canlı/devrede varsa güncel skor.
     Eksik, ertelenen, iptal veya başlamayan maçta skor yok. Canlı skor snapshot'ı
     eskirse “son skor” notu gösterilir. Küçük skor rozeti uzun takım isimlerinde
     ve mobil görünümde düzeni bozmaz.
   - **Kanala tıkla → yayın player'de:** Alttaki kanal kartına (veya maç
     kartındaki ▶ İZLE'ye) tıklayınca yayın doğrudan oynatıcıda açılır ve sayfa
     yumuşakça player'e kayar (kısa altın "flash" animasyonu ile).
   - **Kompakt kartlar + görünüm seçimi:** Kanal kartları küçültüldü ve
     **▦ Izgara / ☰ Liste** (yatay) seçenekleri eklendi; tercih `localStorage`'da saklanır.
   - Ekstra: marka filtreleri (Bein Sports, S Sport, TRT, Tabii Spor, …), kanal & maç
     **arama**, durum/spor filtreleri, canlı saat, takım logoları, ⭐ Günün Maçı rozeti,
     klavye kısayolları (`←`/`→` kanal, `G`/`L` görünüm, `1`/`2` sekme), `#kanal=...` derin bağlantısı,
     JS kapalıysa çalışan `<noscript>` maç listesi.
   - **Canlı tazeleme:** Sayfa açılışta ve 5 dakikada bir `output/today_matches.json`
     dosyasını okumayı dener (bot bu dosyayı 5 dakikada bir günceller); erişilemezse
     gömülü gerçek veriyle sorunsuz çalışmaya devam eder.

6. **⚡ EXTRA PANELLER — doğrudan m3u8 / panel kanalları** (`src/fixbet/extras.py` + `config/extra_channels.yml`)
   - Ana siteden bağımsız ek kaynaklar:
     - **ATOM SPOR** (14 kanal: Bein Sports 1-5, S Sport / 2 / Plus, Tivibu Spor 1-3, SmartSpor,
       TV 8,5, Bein Sports Haber) — player sayfasından (`/matches?id=<slug>`) veya worker yönlendirmesinden HLS çözülür.
     - **SELÇUK SPOR / Sporcafe** (14 kanal: Bein Sports 1-5, Max 1-2, S Sport 1-2, Tivibu 1-2,
       SmartSpor, A Spor, Eurosport 1) — **iki aşamalı**: ana sayfadan oynatıcı sunucusu
       (`main.uxsyplayer….click`) bulunur, oynatıcı sayfasındaki `this.adsBaseUrl` kökünden
       `{kök}{slug}/playlist.m3u8` kurulur.
     - **TARAFTARIUM24** (12 kanal: Bein Sports 1-5, Bein Sports Max 1-2, S Sport 1-2,
       TRT Spor, TRT 1, A Spor) — ana sayfadaki kanal ID/linkleri otomatik keşfedilir.
       Güncel rota (`/mac-izle/<id>`) ve kullanıcının verdiği eski
       `/channel/watch/<id>` rotası birlikte desteklenir; sayfa HLS vermezse panel sayfası
       yedek olarak oynatıcıda açılır.
   - Bot her çalışmada **m3u8 adresini çıkarır** (düz link, göreli link, URL-encoded,
     base64/`atob`, iç içe iframe'ler, ana sayfadaki kanal bağlantısı veya
     `player.stream_base_patterns` kuralları). Çıkaramazsa son çözümü
     `keep_resolved_hours` kadar korur; yedek olarak panelin `fallback_template`'i
     ve iframe için kanal/oynatıcı sayfası eklenir.
   - Panelin adresi değişirse: önce son bilinen adres, sonra `entry_urls` (yönlendirme izlenir),
     sonra birden fazla numaralı alan adı kalıbı taranır (ör. **taraftarium24bedava → 25 …**).
     Bulunan adres, rota ve oynatıcı sunucusu `output/extra_channels.json` içinde saklanır;
     sonraki çalışma buradan başlar.
   - Sayfada **⚡ EXTRA PANELLER** sekmesi: aynı kompakt kartlar, panel çipleri, arama, ızgara/liste.
     Karta tıklayınca yayın **sayfanın kendi HLS oynatıcısında** açılır — Safari/iOS'ta yerel HLS,
     diğer tarayıcılarda `hls.js` (CDN'den yalnızca ilk EXTRA yayında yüklenir).
   - Oynatıcı ekleri: **kaynak çipleri** (Kaynak 1 / Kaynak 2 / 🌐 Site), açılmayan kaynakta
     **otomatik sıradaki kaynağa geçiş**, hata katmanı (🔄 Tekrar dene · ⏭ Diğer kaynak ·
     ↗ Yeni sekmede aç), PiP, tam ekran, `←`/`→` ile EXTRA kanallar arasında gezinme, `S` kaynak
     değiştir, `3` sekme, `#extra=atom:bein-sports-1` derin bağlantısı.
   - Yeni bir extra panel eklemek için `config/extra_channels.yml` → `panels` altına yeni blok
     eklemek yeterlidir; sayfa/bot tarafında kod değişikliği gerekmez.

7. **🏆 Lig puan durumu — LİG PUANI butonu** (`src/fixbet/standings.py` + `config/standings.yml`)
   - Saatin hemen yanındaki **LİG PUANI** butonu (neon mavi/pembe kenar, solda tablo ikonu)
     ekranın ortasında karartılmış (`backdrop-filter`) bir **PUAN DURUMU** modalı açar.
   - Tablo sütunları: **SIRA · TAKIM · O · G · B · M · AV · P**, satır aralarında ince ayraç çizgileri.
     Kaynak notundan gelen Avrupa/düşme hattı rozetleri sıra hücresinde renklendirilir.
   - **Veri gerçek kaynaktan gelir** (ESPN `standings` ucu, `config/standings.yml → leagues`).
     Skorlardaki ilke burada da geçerlidir: **sayfa asla uydurma puan tablosu göstermez.**
     Sıra/O/G/B/M/averaj/puan kaynaktan geldiği gibi yazılır; yalnızca kaynak averajı hiç
     vermediğinde attığı-yediği farkı, puan eksikse G×3+B kuralı uygulanır (ikisi de kaynağın
     kendi sayılarından). `O` veya `G/B/M` eksikse satır **atlanır**, doldurulmaz.
   - Kaynak bir lig için erişilemezse o ligin **son bilinen** tablosu korunur
     (`output/standings.json`); tablo hiç yoksa modal dürüst bir "veri yok" mesajı gösterir.
   - `config/standings.yml → display_names` yalnızca ESPN'in ASCII takım adlarını Türkçeleştirir
     (Besiktas → Beşiktaş); **hiçbir sayısal değeri değiştirmez**, eşleşmeyen ad aynen kalır.
   - Sayfa açılışta ve 5 dakikada bir `output/standings.json` dosyasını okur; JS kapalıysa
     `<noscript>` içinde aynı tablo düz HTML olarak basılır.

8. **Raporlar** (`src/fixbet/reports.py` → `output/`)
   - `report.html` → tarayıcıda açılan, kendi kendine yeten canlı panel (maçlar + 7/24 kanallar).
   - `matches.md` → okunabilir günlük maç listesi + kanal listesi.
   - `matches.json`, `live_matches.json`, `today_matches.json`, `channels.json` → makine okunur veri.
   - `extra_channels.json` → EXTRA panellerin güncel m3u8 adresleri (sayfa 5 dakikada bir okur).
   - `standings.json` → lig puan durumu (sayfa 5 dakikada bir okur).

## 🚀 Kurulum & Çalıştırma

```bash
pip install -r requirements.txt

# Tam boru hattı (site -> maçlar -> kategori -> raporlar)
python fixbet.py run

# Sadece güncel adresi güncelle
python fixbet.py update-site

# Sadece maçları çek
python fixbet.py matches

# Sürekli izleme (5 dakikada bir)
python fixbet.py serve 5

# Sayfayı ağ olmadan, output/ içindeki son gerçek veriden yeniden üret
python fixbet.py build-index

# Sadece EXTRA panelleri (Atom / Selçuk / Taraftarium) yenile ve sayfayı güncelle
python fixbet.py extras

# Sadece lig puan durumunu çek ve sayfayı güncelle
python fixbet.py standings

# İsteğe bağlı sayfa + HLS hizmeti (TLS reverse proxy arkasında)
python fixbet.py web --host 0.0.0.0 --port 8000

# Ağ erişimi olan ortamda playlist/segment/header/MIME tanılaması
python fixbet.py diagnose-stream atom:bein-sports-1
```

Çıktılar `output/` klasörüne ve güncel adres `config/current_site.yml` dosyasına yazılır.

## ✅ Testler

```bash
pip install -r requirements-dev.txt
python -m pytest -q tests
python tests/test_pipeline.py
python tests/test_channels.py
python tests/test_site.py
python tests/test_extras.py
python tests/test_standings.py
npm install && npm test
python tests/test_frontend.py
npx playwright install --with-deps chromium
npm run test:browser
```

## 🤖 GitHub Actions ile Otomatik Güncelleme

- `.github/workflows/update.yml` → periyodik olarak botu çalıştırıp üretilen raporları GitHub'a push eder.
- `.github/workflows/cron.yml` → günlük toplu güncelleme işini çalıştırmak için kullanılabilir.

## 📁 Yapı

```text
fixbet-bot/
├── fixbet.py
├── updater.py
├── index.html
├── requirements.txt
├── README.md
├── config/
├── src/fixbet/
├── tests/
└── output/
```

## ⚖️ Uyarı

Bu proje yalnızca eğitim/otomasyon amaçlıdır. Telif hakkı olan içeriklerin yeniden dağıtımı yasak olabilir; kendi siteniz/datanız için kullanın.
