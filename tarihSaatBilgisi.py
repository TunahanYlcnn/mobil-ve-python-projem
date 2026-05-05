from datetime import date

print(date.today()) # sadece tarih

from datetime import datetime

print(datetime.now().strftime("%H:%M:%S")) # sadece saat

from datetime import datetime

now = datetime.now()
print(now.strftime("%d.%m.%Y %H:%M:%S")) # tarih ve saat birlikte
