import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Turkish (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Son güncelleme: 24 Ekim 2026.</p>
      <p>Bu sayfa, Kleurhoek&apos;un boyama sayfaları ve el işi sayfalarıyla neler yapabileceğini, başka web sitelerine nasıl bağlantı verdiğimizi ve bize nasıl bildirimde bulunabileceğini açıklar. Kleurhoek&apos;u kullanarak bu koşulları kabul etmiş olursun.</p>

      <h2>Kendi tasarımlarımız</h2>
      <p>Kleurhoek&apos;taki tüm boyama sayfaları, kesme sayfaları ve kâğıt maketler Kleurhoek için özel olarak hazırlanmıştır. Bunları yapay zekâ yardımıyla oluşturuyor ve her sayfayı yayınlamadan önce kontrol ediyoruz. Başka web sitelerinden ya da kitaplardan hiçbir şey kopyalamıyoruz; tanınmış karakterleri, markaları ya da figürleri yeniden çizmiyoruz. Web sitesi, Kleurhoek adı ve sayfa koleksiyonu Kleurhoek&apos;a aittir.</p>
      <p>Sayfaları ücretsiz olarak şu şekillerde kullanabilirsin:</p>
      <ul>
        <li>evde boyamak, yazdırmak ve aile ile arkadaşlara dağıtmak için;</li>
        <li>okulda, kreşte, bir kulüpte ya da kütüphanede, çok sayıda kopya da dahil;</li>
        <li>bir partide, örneğin el işi etkinliği olarak.</li>
      </ul>
      <p>Yazılı iznimiz olmadan şunlara izin verilmez: sayfaları satmak (tek tek, kitapçık halinde ya da indirilebilir dosya olarak), onları başka bir web sitesinde, bir uygulamada ya da sosyal medyada kendi materyalin gibi paylaşmak ya da ürünlerde veya reklamlarda kullanmak. Kleurhoek&apos;taki sayfanın bağlantısını paylaşmaktan ise memnuniyet duyarız.</p>

      <h2>Yapımcılardan temalar</h2>
      <p>Çocuklar çoğu zaman bir çizgi filmden, bir eğlence parkından ya da bir kitaptan karakterlerin boyama sayfalarını arar. Bu çizimler yapımcılarına aittir ve onları kendimiz çizmemiz ya da kopyalamamız yasaktır. Ama birçok yapımcı bunları kendi web sitelerinde ücretsiz sunar. <Link href={link(base, "/themas")}>Yapımcılardan temalar</Link> bölümünde bu sayfaların bağlantılarını topluyoruz. Bunun için şu kurallar geçerlidir:</p>
      <ul>
        <li>Yalnızca yapımcının ya da hak sahibinin resmi web sitesine bağlantı veririz; başkalarının çizimlerini kopyalayan sitelere asla.</li>
        <li>Yapımcıya ait hiçbir görseli, çizimi ya da logoyu göstermez veya saklamayız. Sitemizde yalnızca kendi açıklamamızı ve bir bağlantıyı görürsün. Bu yalnızca bir yapımcı bize yazılı izin verdiğinde farklı olabilir; o durumda bunu belirtiriz.</li>
        <li>Her bağlantıyı yayınlamadan önce kontrol ederiz. Ardından bir bilgisayar programı her gün sayfanın hâlâ var olup olmadığını kontrol eder. Bir sayfa kaybolursa bağlantıyı otomatik olarak kaldırırız. Bunu yaparken her zaman yapımcının web sitesinin kurallarına (robots.txt) uyarız.</li>
        <li>Yapımcıların web sitelerinin içeriği kendi sorumluluklarındadır ve kendi koşullarına tabidir. Bunlar üzerinde hiçbir etkimiz yoktur.</li>
      </ul>
      <p>Bir yapımcı mısın ve bir bağlantıyı değiştirmemizi ya da kaldırmamızı mı istiyorsun, yoksa bizimle çalışmak mı istiyorsun? <Link href={contact("partnership")}>Bizimle iletişime geç</Link>. Değişikliği beş iş günü içinde yaparız.</p>

      <h2>Markalar ve adlar</h2>
      <p>Karakterlerin, eğlence parklarının, dizilerin ve markaların adları sahiplerine aittir. Bunları yalnızca bir şeyi nerede bulabileceğini anlatmak için kullanırız. Açıkça belirtilmedikçe Kleurhoek bu sahiplerle bağlantılı değildir ve onlar tarafından desteklenmemektedir.</p>

      <h2>İş ortağı bağlantıları</h2>
      <p>Bazı sayfa ve temalarda, onlarla kullanabileceğin şeylerden söz ederiz; örneğin çocuk makası ya da kuru boya kalemleri. Bunlar iş ortağı bağlantılarıdır: Böyle bir bağlantı üzerinden bir şey satın alırsan Kleurhoek mağazadan küçük bir komisyon alır. Sen aynı fiyatı ödersin. Sayfaları bu sayede ücretsiz tutuyoruz. İş ortağı bağlantıları her zaman açıkça belirtilir. Ürün, fiyat ve teslimattan mağaza sorumludur.</p>

      <h2>Telif hakkı bildirimi</h2>
      <p>Kleurhoek&apos;ta haklarına sahip olduğun bir şey olduğunu ya da bir bağlantının olmaması gereken bir yere yönlendirdiğini mi düşünüyorsun? Bunu &quot;Telif hakkı&quot; konusuyla <Link href={contact("copyright")}>iletişim formu</Link> üzerinden bildir. Hangi sayfayla ilgili olduğunu, neden doğru olmadığını düşündüğünü ve sana nasıl ulaşabileceğimizi yaz. Beş iş günü içinde yanıt veririz ve gerekirse incelerken içeriği kaldırırız.</p>

      <h2>Güvenli el işi</h2>
      <p>Kesme sayfaları ve kâğıt maketler bir yetişkinle birlikte yapılmak içindir. Çocuk makası kullan; fenerlerde her zaman LED ışık kullan, asla gerçek mum kullanma. Küçük parçalar üç yaşından küçük çocuklar için uygun değildir.</p>

      <h2>Sorumluluk</h2>
      <p>Kleurhoek&apos;u büyük bir özenle hazırlıyoruz, ancak her şeyin her zaman hatasız olacağına ya da web sitesinin her zaman erişilebilir olacağına söz veremeyiz. Yasanın izin verdiği ölçüde Kleurhoek, web sitesinin, sayfaların ya da bağlantı verdiğimiz web sitelerinin kullanımından doğan hiçbir zarardan sorumlu değildir.</p>

      <h2>Gizlilik</h2>
      <p>Ziyaretleri anonim olarak sayarız: çerez olmadan, IP adresi olmadan ve sana kadar izlenebilecek hiçbir şey olmadan. Boyamak ya da yazdırmak için hesaba ihtiyacın yok. Yine de bir hesap oluşturursan, tüm cihazlarında bulabilmen için adını, e-posta adresini ve favorilerini saklarız; hesabını istediğin zaman kendin silebilirsin. E-postalara abone olursan adresini yalnızca bunun için kullanırız ve abonelikten çıktığında adresin silinir. Bize bir mesaj gönderirsen adını ve e-posta adresini yalnızca sana yanıt vermek için kullanır, mesajı en fazla on iki ay saklarız. Mesajının daha önce silinmesini mi istiyorsun? <Link href={contact("privacy")}>Bize haber ver</Link>.</p>

      <h2>Değişiklikler ve sorular</h2>
      <p>Bu yasal uyarıyı, örneğin Kleurhoek&apos;a yeni bir şey eklendiğinde, değiştirebiliriz. En üstteki tarih son güncellemenin ne zaman yapıldığını gösterir. Bu yasal uyarıya Hollanda hukuku uygulanır. Soruların mı var? <Link href={contact()}>Bizimle iletişime geç</Link>.</p>
    </>
  );
}
