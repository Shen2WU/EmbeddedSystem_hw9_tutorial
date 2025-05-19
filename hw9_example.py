import urequests, ujson
import xtools, utime
from machine import Pin 
import config


xtools.connect_wifi_led()

ADAFRUIT_IO_USERNAME = config.ADAFRUIT_IO_USERNAME	
ADAFRUIT_IO_KEY      = config.ADAFRUIT_IO_KEY

API_key = config.API_key
FEEDS_CITIES = ["new taipei"] 
COUNTRY_CODE = "TW" 

def get_temperature_for_city(city_name, country_code):
    url  = "https://api.openweathermap.org/data/2.5/weather?"
    url += "q=" + city_name + "," + country_code 
    url += "&units=metric&lang=zh_tw&" # 單位：攝氏度，語言：繁體中文
    url += "appid=" + API_key
    
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            data = ujson.loads(response.text)
            main_data = data.get("main", {})
            temp = main_data.get("temp")
            response.close() # 及時釋放資源
            if temp is not None:
                print(f"城市 {city_name} 的溫度: {temp}°C")
                return temp
            else:
                #print(f"ERROR：找不到到城市 {city_name} 的 'temp' 數據。")
                return None 
        else:
            #print(f"獲取城市 {city_name} 的 OWM 數據失敗。狀態碼: {response.status_code}")
            response.close()
            return None
    except Exception as e:
        return None

while True:

        for city_name in FEEDS_CITIES:
                current_temp = get_temperature_for_city(city_name.replace(" ", "%20"), COUNTRY_CODE) #在 URL encoding 中，空格以"%20"或是"+"表示 
                
                if current_temp is not None:       
                    adafruit_feed_key = city_name.replace(" ", "-") # 查看Block Info 的URL，呼叫名稱與城市名稱不相同
                    adafruit_url = "https://io.adafruit.com/api/v2/" + ADAFRUIT_IO_USERNAME
                    adafruit_url += "/feeds/city."+ adafruit_feed_key + "/data?X-AIO-Key=" + ADAFRUIT_IO_KEY     # 在group city下的FEED路徑要改
                    
                    data_to_send = {"value": current_temp}
                    print(f" {adafruit_feed_key} city : {current_temp}")
                    xtools.webhook_post(adafruit_url, data_to_send)
                    
                else:
                    print(f"未能獲取城市 {city_name} 的數據，本次跳過發送。")

                utime.sleep(30) 


