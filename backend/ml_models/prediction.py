import pandas as pd
from prophet import Prophet
from bike.models import BikeRide
from django.utils import timezone


def train_bike_demand_model():
    # 1. Veritabanından sürüş verilerini çek (Sadece başlangıç zamanı yeterli)
    rides = BikeRide.objects.all().values('rental_start_date')

    # Veri yoksa boş döndür (Hata almamak için)
    if not rides:
        return []

    # 2. Pandas DataFrame'e çevir
    df = pd.DataFrame(list(rides))

    # Sütun ismini Prophet'in istediği formata ('ds') çevir ve saatlik grupla
    df['ds'] = pd.to_datetime(df['rental_start_date'])

    # Saatlik frekansa göre sürüş sayılarını topla (Resample)
    # 'y' hedef değişkendir (talep sayısı)
    df_grouped = df.set_index('ds').resample('H').size().reset_index(name='y')

    # 3. Prophet Modelini Eğit
    m = Prophet()
    m.fit(df_grouped)

    # 4. Gelecek 24 saat için DataFrame oluştur
    future = m.make_future_dataframe(periods=24, freq='H')

    # 5. Tahmin Yap
    forecast = m.predict(future)

    # 6. Sonuçları formatla (Son 24 saati al - yani geleceği)
    # React tarafında kolay kullanmak için JSON listesine çeviriyoruz
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(24)

    formatted_result = []
    for index, row in result.iterrows():
        formatted_result.append({
            'time': row['ds'].strftime('%H:%M'),  # Sadece saati alıyoruz
            'date': row['ds'].strftime('%Y-%m-%d'),
            'prediction': round(row['yhat']),  # Tahmin edilen bisiklet sayısı
            'min_prediction': round(row['yhat_lower']),
            'max_prediction': round(row['yhat_upper'])
        })

    return formatted_result