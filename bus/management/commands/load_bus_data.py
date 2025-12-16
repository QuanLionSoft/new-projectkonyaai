import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import make_aware
from bus.models import BusLine, BusSchedule, BusRoute, BusStop


class Command(BaseCommand):
    help = 'Otobüs Hatlarını, Rotalarını, Duraklarını ve Tarifelerini Yükler.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Veri yükleme işlemi başlıyor...'))

        # 1. HATLAR (BusLine)
        self.load_lines()

        # 2. ROTALAR (BusRoute)
        # Durak konumlarını hesaplamak için önce rotanın yüklenmesi şarttır.
        self.load_routes()

        # 3. DURAKLAR (BusStop)
        # Rota üzerindeki noktalardan durak koordinatı türeteceğiz.
        self.load_stops()

        # 4. TARİFELER (BusSchedule)
        self.load_schedules()

        self.stdout.write(self.style.SUCCESS('TÜM OTOBÜS VERİLERİ BAŞARIYLA YÜKLENDİ! 🚀'))

    def load_lines(self):
        self.stdout.write("1. Hat bilgileri yükleniyor...")
        path = os.path.join(settings.BASE_DIR, 'data', 'Bus', '25_202106_hatbilgisi.csv')

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'Dosya bulunamadı: {path}'))
            return

        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            count = 0
            for row in reader:
                try:
                    uzunluk = row.get('uzunluk_km', '0').replace(',', '.')
                    BusLine.objects.get_or_create(
                        ana_hat_no=int(row['ana_hat_no']),
                        alt_hat_no=int(row['alt_hat_no']),
                        defaults={
                            'ana_hat_adi': row['ana_hat_adi'],
                            'alt_hat_adi': row['alt_hat_adi'],
                            'durak_sayisi': int(row['durak_sayisi']) if row.get('durak_sayisi') else 0,
                            'uzunluk_km': float(uzunluk) if uzunluk else 0
                        }
                    )
                    count += 1
                except ValueError:
                    continue
        self.stdout.write(self.style.SUCCESS(f'{count} hat yüklendi.'))

    def load_routes(self):
        self.stdout.write("2. Güzergahlar (Rotalar) yükleniyor...")
        path = os.path.join(settings.BASE_DIR, 'data', 'Bus', '20_202106_guzergah.csv')

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'Dosya bulunamadı: {path}'))
            return

        # Önceki rotaları temizle
        BusRoute.objects.all().delete()

        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')

            route_objs = []

            # Sıra takibi
            current_line_key = None
            sira_counter = 1

            for row in reader:
                try:
                    ana_no = int(row['ana_hat_no'])
                    # alt_hat_no dosyada yoksa 0 kabul et
                    alt_no = int(row['alt_hat_no']) if 'alt_hat_no' in row and row['alt_hat_no'] else 0

                    # Koordinat Düzeltme (37.836.350 -> 37.836350)
                    raw_lat = row['enlem'].replace('.', '')
                    raw_lng = row['boylam'].replace('.', '')

                    if len(raw_lat) < 3 or len(raw_lng) < 3: continue

                    lat = float(raw_lat[:2] + '.' + raw_lat[2:])
                    lng = float(raw_lng[:2] + '.' + raw_lng[2:])

                    # Hat değişimi kontrolü
                    line_key = (ana_no, alt_no)
                    if line_key != current_line_key:
                        current_line_key = line_key
                        sira_counter = 1
                    else:
                        sira_counter += 1

                    # İlgili hattı bul
                    line = BusLine.objects.filter(ana_hat_no=ana_no, alt_hat_no=alt_no).first()
                    if not line: continue

                    # Rota Noktası Oluştur
                    route_objs.append(BusRoute(
                        line=line,
                        yon='Gidis',
                        sira=sira_counter,
                        enlem=lat,
                        boylam=lng
                    ))

                except ValueError:
                    continue

                # Toplu Kayıt (Batch) - Bellek şişmesin diye parça parça
                if len(route_objs) >= 5000:
                    BusRoute.objects.bulk_create(route_objs)
                    route_objs = []
                    self.stdout.write(f"... {sira_counter} nokta işlendi")

            # Kalanları kaydet
            if route_objs: BusRoute.objects.bulk_create(route_objs)

        self.stdout.write(self.style.SUCCESS(f'Rotalar yüklendi.'))

    def load_stops(self):
        self.stdout.write("3. Duraklar işleniyor ve koordinatları rotadan eşleştiriliyor...")
        path = os.path.join(settings.BASE_DIR, 'data', 'Bus', '21_202106_hatdurak.csv')

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'Dosya bulunamadı: {path}'))
            return

        # Önceki durakları temizle
        BusStop.objects.all().delete()

        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            stops_buffer = []

            for row in reader:
                try:
                    # Hattı bul
                    ana_no = int(row['ana_hat_no'])
                    alt_no = int(row['alt_hat_no'])
                    line = BusLine.objects.filter(ana_hat_no=ana_no, alt_hat_no=alt_no).first()

                    if line:
                        # KOORDİNAT EŞLEŞTİRME SİMÜLASYONU
                        # Durak dosyasında koordinat yok. Güzergah (BusRoute) tablosundan
                        # durağın sırasına denk gelen bir koordinat bulmaya çalışıyoruz.
                        # "sira" bilgisini bir çarpanla genişleterek rota üzerindeki yaklaşık konumu alıyoruz.
                        target_route_index = int(row['sira']) * 8  # Tahmini: Her durak arası ortalama 8 rota noktası

                        # O hatta ait, hedef sıradaki veya en yakın rota noktasını al
                        route_point = BusRoute.objects.filter(line=line, sira__gte=target_route_index).order_by(
                            'sira').first()

                        # Eğer rota noktası bulunamazsa hattın son noktasını veya varsayılanı al
                        if not route_point:
                            route_point = BusRoute.objects.filter(line=line).last()

                        lat = route_point.enlem if route_point else 37.8716
                        lng = route_point.boylam if route_point else 32.4852

                        stops_buffer.append(BusStop(
                            line=line,
                            durak_no=row['durak_no'],
                            sira=int(row['sira']),
                            istikamet=row.get('istikamet', ''),
                            enlem=lat,
                            boylam=lng
                        ))
                except Exception:
                    continue

                if len(stops_buffer) >= 5000:
                    BusStop.objects.bulk_create(stops_buffer)
                    stops_buffer = []

            if stops_buffer:
                BusStop.objects.bulk_create(stops_buffer)

        self.stdout.write(self.style.SUCCESS('Duraklar başarıyla yüklendi.'))

    def load_schedules(self):
        self.stdout.write("4. Sefer saatleri yükleniyor...")
        path = os.path.join(settings.BASE_DIR, 'data', 'Bus', 'bustarife.csv')

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'Dosya bulunamadı: {path}'))
            return

        # Eğer veritabanında zaten tarife varsa tekrar yüklemeyelim (Çok zaman alıyor)
        if BusSchedule.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Tarifeler zaten yüklü, atlanıyor. (Silip tekrar yüklemek isterseniz DB'yi temizleyin)"))
            return

        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            objs = []
            count = 0
            for row in reader:
                try:
                    line = BusLine.objects.filter(
                        ana_hat_no=int(row['hat_no']),
                        alt_hat_no=int(row['alt_hat_no'])
                    ).first()

                    if line:
                        # Tarih formatını düzelt
                        try:
                            t = datetime.strptime(row['saat'], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                t = datetime.strptime(row['saat'], '%H:%M:%S')
                            except:
                                continue

                        objs.append(BusSchedule(
                            line=line,
                            kalkis_tarihi=make_aware(t),  # Timezone aware
                            tarife_tipi=row['tarife_zamani']
                        ))
                        count += 1
                except:
                    continue

                if len(objs) >= 5000:
                    BusSchedule.objects.bulk_create(objs)
                    objs = []
                    self.stdout.write(f"... {count} tarife işlendi")

            if objs: BusSchedule.objects.bulk_create(objs)

        self.stdout.write(self.style.SUCCESS(f'{count} adet sefer saati yüklendi.'))