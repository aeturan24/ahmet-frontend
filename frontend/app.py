import streamlit as st
import requests

st.set_page_config(
    page_title="YZ Gezi Rehberi",
    page_icon="🌍",
    layout="wide"
)

DEFAULT_API_URL = ""
DEFAULT_API_TOKEN = ""

st.sidebar.markdown("### ⚙️ Bağlantı Ayarları / Settings")
api_url = st.sidebar.text_input("Strapi API URL", value=DEFAULT_API_URL)
api_token = st.sidebar.text_input("Strapi API Token", value=DEFAULT_API_TOKEN, type="password")

st.sidebar.markdown("### 🌐 Dil Seçimi / Language")
lang = st.sidebar.selectbox(
    "Dil / Language",
    options=["Türkçe (TR)", "English (EN)"]
)

locale = "tr" if "TR" in lang else "en"
t = {
    "tr": {
        "title": "🌍 YZ Destekli Uluslararası Gezi Rehberi",
        "subtitle": "Yapay zekâ ile zenginleştirilmiş modern ve global gezi rehberi.",
        "select_city": "Bir Şehir Seçin",
        "popular_places": "Gezilecek Popüler Mekanlar",
        "rating": "Puan",
        "country": "Ülke",
        "description": "Şehir Açıklaması",
        "no_places": "Bu şehir için henüz bir mekan eklenmemiş.",
        "connection_error": "Strapi backend bağlantısı başarısız! Lütfen backend'in açık olduğundan ve API Token'ın doğru olduğundan emin olun.",
        "enter_token_warning": "Lütfen sol panelden geçerli bir API Token girin.",
        "about_title": "Proje Hakkında",
        "about_desc": "Bu uygulama Strapi v4, Python otomasyonu (çeviri + Pollinations AI görsel üretimi) ve Streamlit kullanılarak geliştirilmiştir."
    },
    "en": {
        "title": "🌍 AI-Powered Global Travel Guide",
        "subtitle": "Modern and smart travel guide enriched with AI-generated visuals.",
        "select_city": "Select a City",
        "popular_places": "Popular Places to Visit",
        "rating": "Rating",
        "country": "Country",
        "description": "City Description",
        "no_places": "No places have been added for this city yet.",
        "connection_error": "Failed to connect to Strapi backend! Please check if the backend is running and the API Token is correct.",
        "enter_token_warning": "Please enter a valid API Token in the left panel.",
        "about_title": "About Project",
        "about_desc": "This application is developed using Strapi v4, Python automation (translation + Pollinations AI image generation), and Streamlit."
    }
}[locale]

# Custom CSS for modern look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0b132b;
    }
    [data-testid="stSidebar"] {
        background-color: #1c2541;
    }
    .stSelectbox label, .stTextInput label {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: #e0e1dd !important;
    }
    p, h1, h2, h3, h4, h5, h6, span, div {
        color: #e0e1dd !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align: center; font-weight: 800; font-size: 4rem; background: linear-gradient(135deg, #4ea8de 0%, #5e60ce 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #a9b3c4 !important; font-size: 1.3rem; margin-top: 10px; margin-bottom: 3rem; font-weight: 400;'>{t['subtitle']}</p>", unsafe_allow_html=True)

if not api_token:
    st.warning(t["enter_token_warning"])
else:
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        response = requests.get(f"{api_url}/api/cities", headers=headers, params={"locale": locale}, timeout=10)
        if response.status_code == 200:
            cities_data = response.json().get('data', [])
            if cities_data:
                city_options = {city['attributes']['name']: city for city in cities_data}
                selected_city_name = st.selectbox(t["select_city"], list(city_options.keys()))
                
                if selected_city_name:
                    selected_city = city_options[selected_city_name]
                    c_attr = selected_city['attributes']
                    
                    with st.container(border=True):
                        st.markdown(f"### 📍 **{c_attr['name']}**")
                        st.markdown(f"**{t['country']}:** {c_attr['country']}")
                        st.write(f"**{t['description']}:** {c_attr.get('description', '')}")
                    
                    st.markdown(f"## 🏛️ {t['popular_places']}")
                    places_params = {
                        "filters[city][id][$eq]": selected_city['id'],
                        "locale": locale,
                        "populate": "image"
                    }
                    places_response = requests.get(f"{api_url}/api/places", headers=headers, params=places_params, timeout=10)
                    
                    if places_response.status_code == 200:
                        places_data = places_response.json().get('data', [])
                        if places_data:
                            cols = st.columns([1,1,1])
                            for idx, place in enumerate(places_data):
                                p_attr = place['attributes']
                                img_url = None
                                img_field = p_attr.get('image')
                                if img_field and isinstance(img_field, dict) and img_field.get('data'):
                                    img_url = img_field['data'].get('attributes', {}).get('url')
                                
                                img_url = f"{api_url}{img_url}" if img_url and img_url.startswith("/") else img_url
                                if not img_url:
                                    img_url = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&q=80&w=800"
                                
                                rating_val = p_attr.get('rating', '0.0')
                                col_to_use = cols[idx % 3]
                                with col_to_use:
                                    card = st.container(border=True)
                                    card.image(img_url, use_container_width=True)
                                    card.markdown(f"### **{p_attr['name']}**")
                                    card.markdown(f"⭐ **{t['rating']}: {rating_val}/10**")
                                    card.write(p_attr.get('description', ''))
                        else:
                            st.info(t["no_places"])
                    else:
                        st.error(t["connection_error"])
            else:
                st.info("Strapi veritabanında henüz şehir bulunmuyor. Lütfen önce otomasyon betiğini çalıştırın.")
        else:
            st.error(t["connection_error"])
            st.sidebar.error(f"HTTP {response.status_code}: {response.text}")
    except Exception as e:
        st.error(t["connection_error"])
        st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown(f"#### ℹ️ {t['about_title']}")
st.sidebar.info(t["about_desc"])

st.divider()
st.markdown("<p style='text-align: center; color: gray !important; font-size: 0.9rem;'>BIP210 Final Projesi | Geliştirici: Ahmet</p>", unsafe_allow_html=True)
