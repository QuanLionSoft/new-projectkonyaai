import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from bus.models import BusLine, BusSchedule


class Command(BaseCommand):
    help = 'Otobüs hatlarını ve tarifelerini yükler'

    def handle(self, *args, **kwargs):
        # 1. Önce Hat Bilgilerini Yükle (BusLine)
        # Dosya ismini kendi dosya isminizle kontrol edin
        hat_bilgisi_path = os.path.join(settings.BASE_DIR, '../data/Bus/25_202106_hatbilgisi.csv')

        self.stdout.write(f"Hat bilgileri yükleniyor: {hat_bilgisi_path}")

        try:
            with open(hat_bilgisi_path, 'r', encoding='utf-8-sig') as file:
                # CSV noktalı virgül (;) ile ayrılmış
                reader = csv.DictReader(file, delimiter=';')

                for row in reader:
                    # Uzunluk verisindeki virgülü noktaya çevir (22,082 -> 22.082)
                    uzunluk = row['uzunluk_km'].replace(',', '.') if row['uzunluk_km'] else 0

                    BusLine.objects.get_or_create(
                        ana_hat_no=int(row['ana_hat_no']),
                        alt_hat_no=int(row['alt_hat_no']),
                        defaults={
                            'ana_hat_adi': row['ana_hat_adi'],
                            'alt_hat_adi': row['alt_hat_adi'],
                            'durak_sayisi': int(row['durak_sayisi']) if row['durak_sayisi'] else 0,
                            'uzunluk_km': float(uzunluk)
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Hat bilgileri başarıyla yüklendi.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Hat bilgisi dosyası bulunamadı! Dosya yolunu kontrol edin.'))
            return

        # 2. Tarife Bilgilerini Yükle (BusSchedule)
        tarife_path = os.path.join(settings.BASE_DIR, '../data/Bus/bustarife.csv')
        self.stdout.write(f"Tarife bilgileri yükleniyor: {tarife_path}")

        try:
            with open(tarife_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file, delimiter=';')
                objs = []

                for row in reader:
                    try:
                        # İlgili hattı bul
                        line = BusLine.objects.get(
                            ana_hat_no=int(row['hat_no']),
                            alt_hat_no=int(row['alt_hat_no'])
                        )

                        # Tarih formatını parse et (2022-06-21 07:15:00)
                        tarih_str = row['saat']
                        tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d %H:%M:%S')

                        # Toplu create için listeye ekle (daha hızlı)
                        objs.append(BusSchedule(
                            line=line,
                            kalkis_tarihi=tarih_obj,
                            tarife_tipi=row['tarife_zamani']
                        ))

                    except BusLine.DoesNotExist:
                        # Eğer tarife dosyasında olup hat dosyasında olmayan bir hat varsa atla
                        continue

                # Veritabanına toplu yazma (Bulk Insert)
                if objs:
                    BusSchedule.objects.bulk_create(objs)

            self.stdout.write(self.style.SUCCESS(f'{len(objs)} adet tarife bilgisi başarıyla yüklendi.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Tarife dosyası bulunamadı!'))