# Ini Untuk Mengimport Tools Atau Library Yang Di Butuhkan
import boto3
from flask import Flask, render_template
import math
import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Baris Ini Berisi Inisialiasi Flask Dengan Nama Modul Yang Sama
app = Flask(__name__)

# Berisi Konfigurasi Aws Dan Flask
os.environ['AWS_ACCESS_KEY_ID'] = 'ASIAZZWEFHMXYRWEEBRY'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'xFeZ70Stt+RWaGkhq+CAxZz6H0K64p0a13GV+RMF'
os.environ['AWS_SESSION_TOKEN'] = 'FwoGZXIvYXdzEIf//////////wEaDNgQg7wr6/wwRoijoCLIAakeNpfIw4zm29vwZjOZS74mJhj0KDNgG7oHlfHSQWkHvduq4KLKdcwcMQG6dmqKfAi/slGxHX8zpylrvsfmqto1XEv1I/txH/Z78iOgk+iP+vFmgcNOc3InnA7kGBWp7SGczNtLo77eEl1r5P5LEji/ZivlHJfgt+HSCL5fY/qgqLKgFeHBjVwG1OPymqlcwRRES4M/japuk1dXvqBaxm5Ehe5HnmLRHdtm9t3av38hvk3CbcwvkKjiquiPZSsoWj+vlGBcv8dmKO2GoacGMi0n662WORLl14id0IYbJ5LLQO8zyZNvX0mWh0g1t+BxS4SJN6rWEBUblNIpMpE='

# Konfigurasi Untuk DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = 'myTable'
table = dynamodb.Table(table_name)

# Dekorator Flask Untuk Rute Nya
@app.route('/')
def index():
    # Melakukan Suatu Scan Dan Mengambil Data Dari Dynamo Dan Disimpan Dalam Items
    response = table.scan()
    items = response['Items']

    # Melakukan Sebuah Literasi Melalui Setiap Items(Hasil Pindai Dynamo Db)
    # Payload Di Ekstrak Dulu Kemudian Di Ambil Nilai Suhu Dan Kelembapan Nya
    # Nilai Payload Di Ambil Dari Temperature Dan Humidity
    # Data Yang Ditemukan Lalu Di Bandingkan Dengan Data Terbaru Yang DiTemukan
    # Jadi Data Yang Diambil awalnya Adalah String, Lalu Saya Ubah String Tersebut Ke Bentuk Float Untuk Mempermudah Proses Logika
    latest_item = None
    latest_temperature = float('-inf')  
    latest_humidity = float('-inf')  

    for item in items:
        payload = item.get('payload', {})  
        temperature = float(payload.get('temperature', 0))  
        humidity = float(payload.get('humidity', 0))  
  
    
        #Untuk Membandingkan Jika Menemukan Data Yang Lebih Besar
        if temperature > latest_temperature:
            latest_item = item
            latest_temperature = temperature

        if humidity > latest_humidity:
            latest_item = item
            latest_humidity = humidity

    # Jika Ada Data Sebuah Suhu Dan Kelembapan Yang Baru Di Temukan 
    # Jadi Bagian Ini Akan Menghitung Sebuah Data Suhu Dan Kelembapan
    # Jadi Grafik Gambar Tersebut Akan DI Simpan Dalam Bentuk ByteslO Object
    # Terus ByteslO Object Diubah Menjadi Base64 String Dan Di Tampilkan Di Template Html
    if latest_item is None:
        result = "Belum ada data suhu dan kelembaban yang tersedia"
    else:
        # Menghitung sudut jarum jam untuk suhu
        max_temperature = 100.0  
        angle_temp = 180 - (latest_temperature / max_temperature * 180)  # Menghitung sudut berdasarkan suhu

        # Menghitung sudut jarum jam untuk kelembaban
        max_humidity = 100.0  # Ubah sesuai dengan kelembaban maksimum yang mungkin
        angle_humidity = 180 - (latest_humidity / max_humidity * 180)  # Menghitung sudut berdasarkan kelembaban

        # Generate a gauge chart using matplotlib for temperature
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(121, polar=True)

        theta_temp = math.radians(angle_temp)
        radii = [1] * 2
        width = math.radians(45)
        bars = ax.bar(theta_temp, radii, width=width, bottom=0.0, color=['red', 'green'])

        for r in bars:
            r.set_alpha(0.6)

        ax.set_xticks([])
        ax.set_yticks([])

        ax2 = fig.add_subplot(122, polar=True)

        theta_humidity = math.radians(angle_humidity)
        radii = [1] * 2
        bars = ax2.bar(theta_humidity, radii, width=width, bottom=0.0, color=['blue', 'green'])

        for r in bars:
            r.set_alpha(0.6)

        ax2.set_xticks([])
        ax2.set_yticks([])

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.read()).decode()

        plt.close()
        

        # Digunakan Untuk Menampilkan Temperature Dan Humidity
        return render_template("gauge_chart.html", plot_data=plot_data, temperature=round(latest_temperature), humidity=round(latest_humidity))

    # Fungsi Kode INi Untuk Mnegembalikan data Jika Tidak Ada Data Yang Di Tampilkan
    return result
# Menjalankan Aplikasi Flask Secara Langsung Sebagai Program
if __name__ == '__main__':
    app.run(debug=True)