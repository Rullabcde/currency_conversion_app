import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

class CurrencyConverter: 
    def __init__(self, cache_file="exchange_rates_cache.json"):
        # Load environment variables
        load_dotenv()
        self.API_KEY = os.getenv('EXCHANGERATE_API_KEY')
        if not self.API_KEY:
            raise ValueError("API Key tidak ditemukan")
            
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.cache_file = cache_file
        self.exchange_rates = {}
        self.last_update = None
        self.supported_currencies = []
        
        # Load cached data atau fetch data baru
        self.load_or_update_rates()
        
    def fetch_latest_rates(self):
        try:
            # Mengambil daftar mata uang yang didukung
            supported_url = f"{self.base_url}/{self.API_KEY}/codes"
            response = requests.get(supported_url)
            response.raise_for_status()
            self.supported_currencies = response.json()['supported_codes']
            
            # Mengambil kurs terbaru
            latest_url = f"{self.base_url}/{self.API_KEY}/latest/USD"
            response = requests.get(latest_url)
            response.raise_for_status()
            
            data = response.json()
            if data['result'] == 'success':
                self.exchange_rates = data['conversion_rates']
                self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_to_cache()
                return True
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"Error saat mengambil data dari API: {e}")
            return False
    
    def load_or_update_rates(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as file:
                    cache = json.load(file)
                    cache_time = datetime.strptime(cache['last_update'], "%Y-%m-%d %H:%M:%S")
                    time_diff = datetime.now() - cache_time
                    
                    if time_diff.days < 1: 
                        self.exchange_rates = cache['rates']
                        self.last_update = cache['last_update']
                        return
            
            if not self.fetch_latest_rates():
                raise Exception("Gagal mengambil data kurs terbaru")
                
        except Exception as e:
            print(f"Error: {e}")
            print("Menggunakan data kurs default...")
            self.use_default_rates()
    
    def use_default_rates(self):
        """Set kurs default jika API tidak tersedia."""
        self.exchange_rates = {
            "USD": 1.0,
            "EUR": 0.93,
            "IDR": 15600,
            "SGD": 1.35,
            "MYR": 4.73,
            "JPY": 150.27
        }
        self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_to_cache(self):
        cache_data = {
            "rates": self.exchange_rates,
            "last_update": self.last_update
        }
        with open(self.cache_file, 'w') as file:
            json.dump(cache_data, file, indent=4)
    
    def convert(self, amount, from_currency, to_currency):
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in self.exchange_rates or to_currency not in self.exchange_rates:
            raise ValueError("Mata uang tidak didukung")
        
        # Konversi ke USD terlebih dahulu (karena USD adalah base currency dari API)
        amount_in_usd = amount / self.exchange_rates[from_currency]
        result = amount_in_usd * self.exchange_rates[to_currency]
        
        return round(result, 2)
    
    def display_rates(self):
        print("\nKurs Mata Uang Terhadap USD:")
        print(f"Terakhir diperbarui: {self.last_update}")
        print("-" * 40)
        
        main_currencies = ['EUR', 'IDR', 'SGD', 'MYR', 'JPY', 'GBP', 'AUD', 'CNY', 'HKD', 'KRW']
        for currency in main_currencies:
            if currency in self.exchange_rates:
                rate = self.exchange_rates[currency]
                print(f"1 USD = {rate:,.4f} {currency}")
        print("-" * 40)
    
    def update_from_api(self):
        """Update kurs dari API secara manual."""
        if self.fetch_latest_rates():
            print("Kurs berhasil diperbarui dari API!")
        else:
            print("Gagal memperbarui kurs. Menggunakan data terakhir yang tersedia.")

def main():
    try:
        converter = CurrencyConverter()
        
        while True:
            print("\nMenu Konversi Mata Uang:")
            print("1. Konversi Mata Uang")
            print("2. Lihat Kurs Saat Ini")
            print("3. Update Kurs dari API")
            print("4. Keluar")
            
            choice = input("\nPilih menu (1-4): ")
            
            if choice == '1':
                try:
                    amount = float(input("Masukkan jumlah uang: "))
                    from_curr = input("Masukkan mata uang asal (contoh: USD): ")
                    to_curr = input("Masukkan mata uang tujuan (contoh: IDR): ")
                    
                    result = converter.convert(amount, from_curr, to_curr)
                    print(f"\n{amount:,.2f} {from_curr.upper()} = {result:,.2f} {to_curr.upper()}")
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print("Terjadi kesalahan! Pastikan input valid.")
            
            elif choice == '2':
                converter.display_rates()
            
            elif choice == '3':
                converter.update_from_api()
            
            elif choice == '4':
                print("Terima kasih telah menggunakan aplikasi ini!")
                break
            
            else:
                print("Pilihan tidak valid! Silakan coba lagi.")
                
    except Exception as e:
        print(f"Terjadi kesalahan saat menjalankan aplikasi: {e}")

if __name__ == "__main__":
    main()