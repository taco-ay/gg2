import sqlite3
import matplotlib
import os

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

class DB_Map():
    def __init__(self, database):
        self.database = database
        if not os.path.exists(self.database):
            self.create_cities_table()
            self.create_user_table()

    def create_cities_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS cities (
                                id TEXT PRIMARY KEY,
                                city TEXT,
                                lat REAL,
                                lng REAL
                            )''')
            conn.commit()

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cities")
            if cursor.fetchone()[0] == 0:
                sample_cities = [
                    ('ankara', 'ankara', 39.9334, 32.8597),
                    ('tokyo', 'tokyo', 35.6895, 139.6917),
                    ('london', 'london', 51.5074, -0.1278),
                    ('paris', 'paris', 48.8566, 2.3522),
                    ('new york', 'new york', 40.7128, -74.0060)
                ]
                conn.executemany('INSERT INTO cities VALUES (?, ?, ?, ?)', sample_cities)
                conn.commit()

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Sorgulama yaparken city_name'i küçük harfe dönüştür
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name.lower(),))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0
            

    def add_new_city(self, city_name, lat, lng):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cities VALUES (?, ?, ?, ?)",
                (city_name.lower(), city_name.lower(), lat, lng)
            )
            conn.commit()

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Sorgulama yaparken city_name'i küçük harfe dönüştür
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name.capitalize(),))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()

        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, long = coordinates
                plt.plot([long], [lat], 'o', color='red', markersize=8, transform=ccrs.Geodetic())
                plt.text(long, lat - 2, city, transform=ccrs.Geodetic())
            else:
                print(f"Uyarı: '{city}' şehri veritabanında bulunamadı veya koordinatları eksik.")
        
        plt.savefig(path)
        plt.close()

    def draw_distance(self, city1, city2):
        city1_c = self.get_coordinates(city1)
        city2_c = self.get_coordinates(city2)

        fig, ax = plt.subplots(projection=ccrs.PlateCarree())
        ax.stock_img()

        if city1_c and city2_c:
            plt.plot([city1_c[1], city2_c[1]], [city1_c[0], city2_c[0]], color='blue', linewidth=2, marker='o', transform=ccrs.Geodetic())
            plt.text(city1_c[1], city1_c[0]+10, city1, transform=ccrs.Geodetic())
            plt.text(city2_c[1], city2_c[0]+10, city2, transform=ccrs.Geodetic())
            plt.savefig('distance_map.png')
            plt.close()
        else:
            print("Uyarı: En az bir şehir veritabanında bulunamadı.")


if __name__ == "__main__":
    m = DB_Map("database.db")
