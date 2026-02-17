import streamlit as st
import requests
from bs4 import BeautifulSoup
import concurrent.futures

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Soft Launch Checker", page_icon="🚀", layout="wide")

# CSS PERSONALIZADO (Para que se vea bonito)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    div.stButton > button { width: 100%; background-color: #ff4b4b; color: white; border: none; }
    div.stButton > button:hover { background-color: #ff2b2b; }
    
    /* TARJETAS */
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }
    .card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3c3d45;
        text-decoration: none;
        color: white !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-5px); border-color: #777; }
    
    .card-ok { border-left: 5px solid #00cc66; }
    .card-pre { border-left: 5px solid #3399ff; }
    .card-no { border-left: 5px solid #ff4b4b; opacity: 0.7; }
    
    .flag { font-size: 1.5rem; margin-right: 10px; }
    .country-name { font-weight: bold; font-size: 1rem; }
    .status-badge { 
        font-size: 0.8rem; 
        padding: 4px 8px; 
        border-radius: 4px; 
        margin-top: 10px; 
        text-align: center; 
        font-weight: bold;
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# --- DATOS ---
PAISES = {
    # AMÉRICAS
    'us': {'n': 'EE.UU.', 'f': '🇺🇸', 'r': 'Américas'}, 'ca': {'n': 'Canadá', 'f': '🇨🇦', 'r': 'Américas'},
    'br': {'n': 'Brasil', 'f': '🇧🇷', 'r': 'Américas'}, 'mx': {'n': 'México', 'f': '🇲🇽', 'r': 'Américas'},
    'co': {'n': 'Colombia', 'f': '🇨🇴', 'r': 'Américas'}, 'cl': {'n': 'Chile', 'f': '🇨🇱', 'r': 'Américas'},
    'ar': {'n': 'Argentina', 'f': '🇦🇷', 'r': 'Américas'},
    # EUROPA
    'es': {'n': 'España', 'f': '🇪🇸', 'r': 'Europa'}, 'gb': {'n': 'Reino Unido', 'f': '🇬🇧', 'r': 'Europa'},
    'de': {'n': 'Alemania', 'f': '🇩🇪', 'r': 'Europa'}, 'fr': {'n': 'Francia', 'f': '🇫🇷', 'r': 'Europa'},
    'it': {'n': 'Italia', 'f': '🇮🇹', 'r': 'Europa'}, 'nl': {'n': 'P. Bajos', 'f': '🇳🇱', 'r': 'Europa'},
    'se': {'n': 'Suecia', 'f': '🇸🇪', 'r': 'Europa'}, 'no': {'n': 'Noruega', 'f': '🇳🇴', 'r': 'Europa'},
    'dk': {'n': 'Dinamarca', 'f': '🇩🇰', 'r': 'Europa'}, 'fi': {'n': 'Finlandia', 'f': '🇫🇮', 'r': 'Europa'},
    'pl': {'n': 'Polonia', 'f': '🇵🇱', 'r': 'Europa'}, 'tr': {'n': 'Turquía', 'f': '🇹🇷', 'r': 'Europa'},
    # ASIA
    'ph': {'n': 'Filipinas', 'f': '🇵🇭', 'r': 'Asia'}, 'au': {'n': 'Australia', 'f': '🇦🇺', 'r': 'Asia'},
    'nz': {'n': 'N. Zelanda', 'f': '🇳🇿', 'r': 'Asia'}, 'sg': {'n': 'Singapur', 'f': '🇸🇬', 'r': 'Asia'},
    'my': {'n': 'Malasia', 'f': '🇲🇾', 'r': 'Asia'}, 'id': {'n': 'Indonesia', 'f': '🇮🇩', 'r': 'Asia'},
    'th': {'n': 'Tailandia', 'f': '🇹🇭', 'r': 'Asia'}, 'vn': {'n': 'Vietnam', 'f': '🇻🇳', 'r': 'Asia'},
    'jp': {'n': 'Japón', 'f': '🇯🇵', 'r': 'Asia'}, 'kr': {'n': 'Corea Sur', 'f': '🇰🇷', 'r': 'Asia'},
    'in': {'n': 'India', 'f': '🇮🇳', 'r': 'Asia'},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"}

def check_country(args):
    code, info, pkg = args
    url = f"https://play.google.com/store/apps/details?id={pkg}&gl={code}&hl=en"
    res = {'c': code, 'n': info['n'], 'f': info['f'], 'r': info['r'], 'u': url, 's': '?', 'o': 9}
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=4)
        if r.status_code == 404:
            res.update({'s': 'missing', 'o': 3})
            return res
        
        txt = r.text
        if "is not available in your country" in txt or "None of your devices" in txt:
            res.update({'s': 'blocked', 'o': 2})
        elif "Pre-register" in txt or "Coming Soon" in txt:
            res.update({'s': 'prereg', 'o': 1})
        elif "Install" in txt or 'itemprop="price"' in txt:
            res.update({'s': 'ok', 'o': 0})
        else:
            res.update({'s': 'blocked', 'o': 2})
    except:
        res.update({'s': 'err', 'o': 4})
    return res

# --- INTERFAZ ---
st.title("🚀 Global Soft Launch Checker")
st.markdown("Herramienta interna para verificar disponibilidad en Google Play Store.")

pkg_input = st.text_input("Package Name", value="com.supercell.clashofclans", placeholder="com.ejemplo.app")
btn = st.button("ESCANEAR DISPONIBILIDAD")

if btn and pkg_input:
    results = []
    tasks = [(k, v, pkg_input) for k, v in PAISES.items()]
    
    with st.status("Escaneando satélites globales...", expanded=True) as status:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exc:
            futures = [exc.submit(check_country, t) for t in tasks]
            for i, f in enumerate(concurrent.futures.as_completed(futures)):
                results.append(f.result())
                status.update(label=f"Escaneando... ({i+1}/{len(tasks)})")
        status.update(label="¡Escaneo Completado!", state="complete", expanded=False)

    # Organizar resultados
    cols = st.columns(3)
    regiones = ['Américas', 'Europa', 'Asia']
    
    for idx, region in enumerate(regiones):
        with cols[idx]:
            st.subheader(f"{region}")
            items = [x for x in results if x['r'] == region]
            items.sort(key=lambda x: x['o']) # Ordenar por status
            
            active_count = len([x for x in items if x['s'] == 'ok'])
            st.caption(f"Activos: {active_count} / {len(items)}")
            
            html_cards = ""
            for item in items:
                # Definir estilos
                if item['s'] == 'ok':
                    css = "card-ok"
                    badge_col = "#00cc66"
                    txt = "DESCARGABLE 🔗"
                    link = f"href='{item['u']}' target='_blank'"
                elif item['s'] == 'prereg':
                    css = "card-pre"
                    badge_col = "#3399ff"
                    txt = "PRE-REG"
                    link = f"href='{item['u']}' target='_blank'"
                else:
                    css = "card-no"
                    badge_col = "#ff4b4b"
                    txt = "BLOQUEADO"
                    link = "" # No link si está bloqueado
                
                # Crear tarjeta HTML
                card_html = f"""
                <a {link} class="card {css}">
                    <div style="display:flex; align-items:center;">
                        <span class="flag">{item['f']}</span>
                        <span class="country-name">{item['n']}</span>
                    </div>
                    <div class="status-badge" style="background-color: {badge_col};">{txt}</div>
                </a>
                """
                html_cards += card_html
            
            st.markdown(f'<div class="card-container">{html_cards}</div>', unsafe_allow_html=True)