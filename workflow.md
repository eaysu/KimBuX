Uygulama Tanimi

KimBuX, kullanicilarin bir X/Twitter hesabini aratip o hesabin icerik karakterini hizlica anlayabildigi bir analiz servisidir. Sistem, ilgili hesabin son 100 / 250 / 500 tweetini inceleyerek profil bilgisini, en cok ilgi goren tweetlerini, sik gecen kelime ve n-gram'larini ve GPT destekli profil analizini uretir. Amac, bir hesabin ne hakkinda yazdigini, nasil bir ton kullandigini, kime hitap ettigini ve one cikan icerik yaklasimini tek yerde gostermektir.

Is Akisi Checklist

[x] Uygulamanin amaci tek cumlede net tanimlansin
[x] Ilk surumun sadece backend + terminal ciktisi oldugu netlestirilsin
[x] Analiz ciktlari kesinlestirilsin
[x] Bio gosterilsin
[x] Username ve display name gosterilsin
[x] Top liked tweetler ayri gosterilsin
[x] Recent top liked tweetler ayri gosterilsin
[x] En sik gecen kelime ve n-gram'lar cikarilsin
[x] GPT destekli profil analizi uretilsin
[x] Icerik tonu uretilsin
[x] Hedef kitle tahmini uretilsin
[x] Tahmini MBTI sonucu uretilsin
[x] En cok bahsedilen 3 konu ve yaklasimi uretilsin
[x] Analiz guven skoru uretilsin
[x] Guven skoru dusuk / orta / yuksek olarak etiketlensin

[x] Analiz kapsami ilk asamada sadece latest mode ile sinirlandirilsin
[x] Kullanici analiz limiti olarak son 100 tweet secebilsin
[x] Kullanici analiz limiti olarak son 250 tweet secebilsin
[x] Kullanici analiz limiti olarak son 500 tweet secebilsin
[x] Hesapta daha az tweet varsa mevcut tum uygun tweetler analiz edilsin
[x] Ilk tweetler uzerinden analiz sonraki surume birakilsin

[x] Ilk surumde sadece original tweet ve quote tweet'ler analize dahil edilsin
[x] Reply'ler ilk surumde analize dahil edilmesin
[x] Retweet'ler ilk surumde analize dahil edilmesin
[x] Analiz edilen gercek tweet sayisi ciktiya yazilsin
[x] Analiz edilen tweet tipleri icte kaydedilsin

[x] Twikit ile profil cekme akis tanimlansin
[x] Tweet toplama akis tanimlansin
[x] Maksimum 500 tweet siniri uygulansin
[x] Gerekli tweet alanlari belirlensin
[x] Hata durumlari tanimlansin
[x] Kullanici bulunamadi durumu yonetilsin
[x] Protected hesap durumu yonetilsin
[x] Rate limit durumu yonetilsin
[x] Session veya login sorunu yonetilsin

[x] Tweet temizleme kurallari belirlensin
[x] Link temizligi yapilsin
[x] Mention temizligi yapilsin
[x] Gereksiz karakter temizligi yapilsin
[x] Stopword temizligi eklensin
[x] Dil tespiti eklensin
[x] Turkce ve Ingilizce agirlikli hesaplar icin uygun kelime temizleme mantigi kurulsun
[x] N-gram cikarim mantigi belirlensin

[x] Top liked tweet hesaplamasi yapilsin
[x] Recent top liked tweet hesaplamasi yapilsin
[x] En sik gecen kelime ve n-gram'lar cikarilsin
[x] Analiz edilen toplam tweet sayisi gosterilsin
[x] Original ve quote oranlari hesaplanip saklansin
[x] Gerekirse sonraki surumler icin ek metrik alani acilsin

[x] GPT'ye verilecek ozet veri seti tanimlansin
[x] GPT'ye tum ham tweetler gonderilmesin
[x] Tweetler batch mantigi ile ozetlensin
[x] Her batch icin yaklasik 30 tweetlik ozet uretilsin
[x] Batch ozetleri birlestirilip final analiz girdisi haline getirilsin
[x] GPT cikti formati sabitlensin
[x] 3-4 cumlelik rahat profil analizi uretilsin
[x] Ton, hedef kitle, MBTI ve konu basliklari uretilsin
[x] Kesin hukum degil tahmini yorum uretilmesi saglansin
[x] Veri azsa dusuk guven uyarisi verilsin
[x] MBTI sonucu dusuk guvenli eglencelik bir icgoru olarak etiketlensin

[x] Aratilan hesaplar veritabanina kaydedilsin
[x] Ayni kullanici tekrar aratildiginda cache kontrolu yapilsin
[x] Her analiz icin son analiz tarihi tutulsun
[x] Ham tweet verisi ile analiz sonucu ayri saklansin
[x] Username + analiz scope + analysis version bazli kayit sistemi kurulsun

[x] Once DB'de kayit aransin
[x] Kayit guncelse direkt sonuc donulsun
[x] Kayit eskiyse yeniden analiz yapilsin
[x] Basarisiz analizler kisa sureli negatif cache ile tutulsun
[x] User not found ve rate limit gibi hata tipleri ayri negatif cache kurallari ile ele alinsin
[x] Ayni anda ayni hesap icin birden fazla analiz baslamasi engellensin

[x] Aktif hesap tanimi yapilsin
[x] Gunde 3 tweet uzeri atan hesaplar aktif hesap sayilsin
[x] Aktif hesaplar icin TTL 15 gun olsun
[x] Diger hesaplar icin TTL 30 gun olsun
[x] Cache suresi hesabin aktivitesine gore belirlensin

[x] CLI uzerinden username alinsin
[x] Kullanici analiz limiti secebilsin
[x] Sistem bekleme sirasinda durum mesajlari gostersin
[x] Sonuc terminalde okunur formatta verilsin
[x] Sonucun cache mi fresh analiz mi oldugu belirtilsin
[x] Analiz edilen gercek tweet sayisi gosterilsin
[x] Analiz tarihi gosterilsin
[x] Veri kaynagi gosterilsin
[x] Original ve quote orani gosterilsin
[x] Guven skoru gosterilsin
[x] Veri azsa dusuk guven uyarisi terminalde gosterilsin

[x] 500 tweet ust siniri sabitlensin
[x] Sadece gerekli alanlar islensin
[x] Onceden hesaplanan metrikler yeniden uretilmesin
[x] Uzun suren analizlerde kullanici bilgilendirilsin

[x] Veritabani olarak Postgres secilsin
[x] Ilk gelistirme lokal ortamda yapilsin
[] Ilk backend deploy icin Render veya Railway degerlendirilsin
[] Ileride frontend gelirse Netlify degerlendirilsin
[x] DB olarak Neon Postgres secenegi degerlendirilsin

[x] Ilk surum hedefi sabitlensin
[x] Backend servis calisir durumda olsun
[x] Terminalden hesap analizi yapilabiliyor olsun
[x] Sonuclar DB'ye kaydediliyor olsun
[x] Ayni hesap tekrar arandiginda cache'den donsun
[x] TTL doldugunda yeniden analiz tetiklensin
