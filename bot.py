from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Veri tabanı yöneticisini başlatma
manager = DB_Map("database.db")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot başlatıldı!")


@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Merhaba, {ctx.author.name}. Mevcut komutların listesini keşfetmek için !help_me yazın.")


@bot.command()
async def help_me(ctx: commands.Context):
    await ctx.send(
        "Mevcut komutlar:\n"
        "!start\n"
        "!show_city [şehir adı]\n"
        "!show_my_cities\n"
        "!remember_city [şehir adı]\n"
        "!add_city [şehir adı] [enlem] [boylam]"
    )


@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    """Belirtilen şehirle birlikte haritayı gösterecek komut."""
    try:
        if city_name:
            manager.create_graph(f"{ctx.author.id}.png", [city_name])
            with open(f"{ctx.author.id}.png", "rb") as res:
                file = discord.File(res, filename=f"{city_name}.png")
                await ctx.send(file=file)
        else:
            await ctx.send("Lütfen bir şehir adı girin. Örneğin: !show_city Ankara")
            
    except Exception as e:
        await ctx.send("Hatalı şehir adı girdiniz.")
        print(f"Hata: {e}")


@bot.command()
async def show_my_cities(ctx: commands.Context):
    """Kullanıcının kaydettiği tüm şehirleri gösterecek komut."""
    try:
        cities = manager.select_cities(ctx.author.id)
        if cities:
            manager.create_graph(f"{ctx.author.id}.png", cities)
            with open(f"{ctx.author.id}.png", "rb") as res:
                file = discord.File(res, filename="my_cities.png")
                await ctx.send("Kaydettiğiniz şehirler:", file=file)
        else:
            await ctx.send("Henüz hiçbir şehir kaydetmemişsiniz. Şehir kaydetmek için !remember_city [şehir_adı] komutunu kullanın.")
            
    except Exception as e:
        await ctx.send("Bir hata oluştu, lütfen daha sonra tekrar deneyin.")
        print(f"Hata: {e}")


@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    """Kullanıcının seçtiği şehri veritabanına kaydeder."""
    if manager.add_city(ctx.author.id, city_name):  
        await ctx.send(f'{city_name} şehri başarıyla kaydedildi!')
    else:
        await ctx.send("Hatalı format. Lütfen şehir adını İngilizce olarak ve komuttan sonra bir boşluk bırakarak girin.")


@bot.command()
async def add_city(ctx: commands.Context, city_name: str, lat: float, lng: float):
    """Yeni şehir ekleme komutu"""
    try:
        manager.add_new_city(city_name, lat, lng)
        await ctx.send(f"{city_name} başarıyla eklendi! Artık !show_city {city_name} kullanabilirsin.")
    except Exception as e:
        await ctx.send("Şehir eklenirken hata oluştu.")
        print(f"Hata: {e}")


if __name__ == "__main__":
    bot.run(TOKEN)
