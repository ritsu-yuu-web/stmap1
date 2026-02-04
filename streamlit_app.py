import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="日本全国の現在気温 3Dマップ", layout="wide")
st.title("日本全国主要都市の現在の気温 3Dカラムマップ")

# 九州7県のデータ
japan_capitals = {
    "Sapporo": {"lat": 43.0642, "lon": 141.3469},
    "Aomori": {"lat": 40.8246, "lon": 140.7400},
    "Morioka": {"lat": 39.7036, "lon": 141.1527},
    "Sendai (Miyagi)": {"lat": 38.2682, "lon": 140.8694},
    "Akita": {"lat": 39.7186, "lon": 140.1024},
    "Yamagata": {"lat": 38.2404, "lon": 140.3633},
    "Fukushima": {"lat": 37.7503, "lon": 140.4676},

    "Mito": {"lat": 36.3418, "lon": 140.4468},
    "Utsunomiya": {"lat": 36.5551, "lon": 139.8828},
    "Maebashi": {"lat": 36.3895, "lon": 139.0604},
    "Saitama": {"lat": 35.8617, "lon": 139.6455},
    "Chiba": {"lat": 35.6073, "lon": 140.1063},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917},
    "Yokohama": {"lat": 35.4437, "lon": 139.6380},

    "Niigata": {"lat": 37.9024, "lon": 139.0232},
    "Toyama": {"lat": 36.6953, "lon": 137.2113},
    "Kanazawa": {"lat": 36.5613, "lon": 136.6562},
    "Fukui": {"lat": 36.0652, "lon": 136.2216},
    "Kofu": {"lat": 35.6639, "lon": 138.5683},
    "Nagano": {"lat": 36.6513, "lon": 138.1810},

    "Gifu": {"lat": 35.3912, "lon": 136.7223},
    "Shizuoka": {"lat": 34.9756, "lon": 138.3828},
    "Nagoya": {"lat": 35.1815, "lon": 136.9066},
    "Tsu": {"lat": 34.7303, "lon": 136.5086},

    "Otsu": {"lat": 35.0045, "lon": 135.8686},
    "Kyoto": {"lat": 35.0116, "lon": 135.7681},
    "Osaka": {"lat": 34.6937, "lon": 135.5023},
    "Kobe": {"lat": 34.6901, "lon": 135.1956},
    "Nara": {"lat": 34.6851, "lon": 135.8048},
    "Wakayama": {"lat": 34.2260, "lon": 135.1675},

    "Tottori": {"lat": 35.5039, "lon": 134.2377},
    "Matsue": {"lat": 35.4723, "lon": 133.0505},
    "Okayama": {"lat": 34.6551, "lon": 133.9195},
    "Hiroshima": {"lat": 34.3853, "lon": 132.4553},
    "Yamaguchi": {"lat": 34.1859, "lon": 131.4706},

    "Tokushima": {"lat": 34.0703, "lon": 134.5548},
    "Takamatsu": {"lat": 34.3401, "lon": 134.0434},
    "Matsuyama": {"lat": 33.8416, "lon": 132.7657},
    "Kochi": {"lat": 33.5597, "lon": 133.5311},

    "Fukuoka": {"lat": 33.5904, "lon": 130.4017},
    "Saga": {"lat": 33.2494, "lon": 130.2988},
    "Nagasaki": {"lat": 32.7503, "lon": 129.8777},
    "Kumamoto": {"lat": 32.8031, "lon": 130.7079},
    "Oita": {"lat": 33.2382, "lon": 131.6126},
    "Miyazaki": {"lat": 31.9111, "lon": 131.4239},
    "Kagoshima": {"lat": 31.5602, "lon": 130.5581},
    "Naha": {"lat": 26.2124, "lon": 127.6809}
}

# --- データ取得関数 ---
@st.cache_data(ttl=600)
def fetch_weather_data():
    weather_info = []
    BASE_URL = 'https://api.open-meteo.com/v1/forecast'
    
    for city, coords in kyushu_capitals.items():
        params = {
            'latitude':  coords['lat'],
            'longitude': coords['lon'],
            'current': 'temperature_2m'
        }
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            weather_info.append({
                'City': city,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'Temperature': data['current']['temperature_2m']
                'Time': data["current"]["time"]
            })
        except Exception as e:
            st.error(f"Error fetching {city}: {e}")
            
    return pd.DataFrame(weather_info)

# データの取得
with st.spinner('最新の気温データを取得中...'):
    df = fetch_weather_data()

# 気温を高さ（メートル）に変換（例：1度 = 3000m）
df['elevation'] = df['Temperature'] * 3000

# --- メインレイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("取得したデータ")
    st.dataframe(df[['City', 'Temperature', 'Time']], use_container_width=True)
    
    if st.button('データを更新'):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("3D カラムマップ")

    # Pydeck の設定
    view_state = pdk.ViewState(
        latitude=36.2,
        longitude=131.0,
        zoom=6.2,
        pitch=45,  # 地図を傾ける
        bearing=0
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=12000,        # 柱の太さ
        get_fill_color='[255, 100, 0, 180]', # 柱の色（オレンジ系）
        pickable=True,       # ホバーを有効に
        auto_highlight=True,
    )

    # 描画
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{City}</b><br>気温: {Temperature}°C",
            "style": {"color": "white"}
        }
    ))
