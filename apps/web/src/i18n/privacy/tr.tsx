import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Son güncelleme: 4 Kasım 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be ve www.kleurhoek.com), çocuklar için özgün boyama sayfaları ve el işi sayfaları sunan bir web sitesidir. Mümkün olduğunca az veri topluyoruz. Bu sayfada neyi sakladığımızı, neden ve ne kadar süreyle sakladığımızı ve haklarının neler olduğunu tam olarak bulabilirsin.</p>

      <h2>Biz kimiz</h2>
      <p>Kleurhoek, Hollandalı bir web sitesidir. Gizlilikle ilgili soruların için lütfen <Link href={contact("privacy")}>iletişim formumuzu</Link> kullan.</p>

      <h2>Ziyaret ve boyama</h2>
      <p>Ziyaretleri anonim olarak sayıyoruz: çerez olmadan, IP adresi olmadan ve sana kadar izlenebilecek hiçbir şey olmadan. Google, Meta ve Pinterest dahil, başkalarına ait hiçbir reklam veya izleme komut dosyası kullanmıyoruz. Boyamak, yazdırmak ve birlikte boyamak için hesap gerekmez. Boyadıkların kendi cihazında kalır. Birlikte boyadığınızda fırça darbeleri, isim olmadan, sunucumuz üzerinden odadaki diğer kişilere iletilir; 30 dakika boyunca kimse boyama yapmazsa oda kapanır. Hediye etiketleri için yazdığın isimler asla sunucumuza gönderilmez.</p>
      <p>Ziyaretçileri iki kez saymamak için IP adresinden ve tarayıcından, her gün değişen bir anahtarla günlük bir kod oluşturuyoruz; IP adresinin kendisini saklamıyoruz. 90 gün sonra bu kodu rastgele bir kodla değiştiriyoruz; böylece biz bile bir sayımı artık bir cihazla ilişkilendiremeyiz. Sayımların kendisini (hangi sayfa, hangi ülke, telefon mu bilgisayar mı, ne zaman) saklıyoruz; böylece sitenin yıllar içinde nasıl kullanıldığını görebiliyoruz.</p>

      <h2>Hesap</h2>
      <p>Hesaplar yalnızca yetişkinler içindir (16 yaş ve üzeri). Çocukların hesaba ihtiyacı yoktur ve hesap oluşturamazlar. Hesabın varsa adını, e-posta adresini ve favorilerini saklıyoruz; böylece onları tüm cihazlarında bulabilirsin. Hesabını kendin silebilirsin; favorilerin ve e-posta kaydın da onunla birlikte silinir.</p>

      <h2>E-posta</h2>
      <p>E-postalara kaydolursan e-posta adresini, seçtiğin konuları, ülkeni ve dilini saklıyoruz. Kaydını önce bir bağlantı aracılığıyla onaylarsın. E-postalarımızda, onları açıp açmadığını ölçmek için izleme pikselleri veya yönlendirilmiş bağlantılar yoktur. Her e-postanın altındaki tek bir tıklamayla abonelikten çıkabilirsin; o zaman adresini sileriz.</p>

      <h2>İletişim</h2>
      <p>Bize mesaj gönderirsen adını ve e-posta adresini yalnızca sana yanıt vermek için kullanırız. Mesajı en fazla on iki ay saklarız.</p>

      <h2>Pinterest, Facebook ve Instagram</h2>
      <p>Kleurhoek, kendi boyama sayfalarını Kleurhoek&apos;un Pinterest, Facebook ve Instagram&apos;daki kendi hesaplarında yayınlar. Bunun için bu hesapları Pinterest ve Meta&apos;nın resmî oturum açma sistemi (OAuth) üzerinden bağlarız. Bu bağlantının erişim belirteçlerini şifrelenmiş olarak saklar ve yalnızca kendi hesaplarımızda gönderi yayınlamak ve pano oluşturmak için kullanırız. Bu hizmetlerin diğer kullanıcılarına ait verileri okumayız, toplamayız veya saklamayız; bağlantıyı reklam için de kullanmayız. Sitemizdeki “Pinterest&apos;e kaydet” düğmesi sıradan bir bağlantıdır: hiçbir Pinterest komut dosyası yüklenmez. Bağlantı her an kaldırılabilir; ardından belirteçleri sileriz.</p>

      <h2>Bize kimler yardım ediyor</h2>
      <p>Web sitesi, Scaleway&apos;in Amsterdam&apos;daki sunucularında çalışır. Cloudflare hız ve güvenlik sağlar, Zitadel oturum açmayı yönetir ve Brevo e-postalarımızı gönderir. Bu şirketler verileri yalnızca bizim adımıza ve yalnızca bu amaçla işler. Amazon gibi bir mağazaya giden bir bağlantıya tıklarsan, o andan itibaren o mağazanın gizlilik politikası geçerli olur.</p>

      <h2>Hakların</h2>
      <p>Hakkında hangi verileri tuttuğumuzu sorabilir, bunların düzeltilmesini veya silinmesini isteyebilirsin. Bunun için lütfen <Link href={contact("privacy")}>bizimle iletişime geç</Link>. Verilerini nasıl işlediğimize katılmıyorsan Autoriteit Persoonsgegevens&apos;e (Hollanda veri koruma kurumu) veya kendi ülkendeki denetim kurumuna şikâyette bulunabilirsin.</p>

      <h2>Değişiklikler</h2>
      <p>Sakladıklarımızda bir şey değişirse bu sayfayı güncelleriz. Üstteki tarih, sayfanın en son ne zaman güncellendiğini gösterir.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Gizlilik politikası", description: "Kleurhoek hangi verileri, neden ve ne kadar süre saklar: çerez yok, ziyaretler anonim sayılır ve hesaplar yalnızca yetişkinler içindir.", Body };
