import streamlit as st
import pandas as pd
import pymssql
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import warnings
import hashlib
import uuid
import os
import re
warnings.filterwarnings('ignore')

# SAYFA KONFİGÜRASYONU
st.set_page_config(
    page_title="IRAZ PLATFORMU",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MODERN CSS TASARIMI - MOBILE FRIENDLY
st.markdown("""
<style>
    /* Ana stiller */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
            padding: 0.2rem;
        }
    }
    
    .sub-header {
        font-size: 1.1rem;
        font-weight: 400;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    
    /* YENİ METRİK KARTLARI - DAHA SADE VE MODERN */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.3rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid #667eea;
        border-right: 1px solid #f0f0f0;
        border-top: 1px solid #f0f0f0;
        border-bottom: 1px solid #f0f0f0;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #2c3e50;
    }
    
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.8;
        color: #666;
        font-weight: 500;
    }
    
    @media (max-width: 768px) {
        .metric-card {
            padding: 1rem;
            min-height: 85px;
        }
        .metric-value {
            font-size: 1.5rem;
        }
    }
    
    /* Filtre bölümü */
    .filter-container {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #e0e6ed;
    }
    
    /* AI Öneri kartları */
    .ai-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    
    .ai-card:hover {
        transform: translateY(-2px);
    }
    
    .ai-card.warning {
        border-left-color: #ff6b6b;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
    }
    
    .ai-card.success {
        border-left-color: #51cf66;
        background: linear-gradient(135deg, #f4fff4 0%, #e6ffe6 100%);
    }
    
    .ai-card.info {
        border-left-color: #339af0;
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f2ff 100%);
    }
    
    /* Butonlar */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* YENİ GİRİŞ BUTONU STİLİ */
    .login-btn {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .login-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0, 184, 148, 0.4) !important;
        background: linear-gradient(135deg, #00a085 0%, #008f76 100%) !important;
    }
    
    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: 1px solid #e0e6ed;
    }
    
    /* YENİ KÜÇÜK LOGIN CONTAINER - %60 DAHA KÜÇÜK */
    .modern-login-container {
        max-width: 320px !important;  /* Önceki 420px idi */
        margin: 1rem auto !important;  /* Önceki 3rem idi */
        padding: 1.5rem !important;    /* Önceki 2.5rem idi */
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        box-shadow: 
            0 15px 30px rgba(0,0,0,0.1),
            0 0 0 1px rgba(255,255,255,0.8),
            inset 0 0 0 1px rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .modern-login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: -200% 0; }
        50% { background-position: 200% 0; }
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 1.5rem !important;  /* Önceki 2rem idi */
    }
    
    .login-title {
        font-size: 1.4rem !important;  /* Önceki 1.8rem idi */
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem !important;  /* Önceki 0.5rem idi */
    }
    
    .login-subtitle {
        color: #666;
        font-size: 0.8rem !important;  /* Önceki 0.9rem idi */
        opacity: 0.8;
    }
    
    .login-input {
        margin-bottom: 1rem !important;  /* Önceki 1.2rem idi */
    }
    
    .login-input .stTextInput input,
    .login-input .stSelectbox div {
        border-radius: 10px !important;
        border: 2px solid #e0e6ed !important;
        padding: 0.6rem 0.8rem !important;  /* Önceki 0.8rem 1rem idi */
        font-size: 0.85rem !important;      /* Önceki 0.9rem idi */
        transition: all 0.3s ease !important;
    }
    
    .login-input .stTextInput input:focus,
    .login-input .stSelectbox div:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .login-button {
        margin-top: 1rem !important;  /* Önceki 1.5rem idi */
    }
    
    .login-info {
        text-align: center;
        margin-top: 1rem !important;  /* Önceki 1.5rem idi */
        padding: 0.8rem !important;   /* Önceki 1rem idi */
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    .login-info h4 {
        color: #667eea;
        margin-bottom: 0.3rem !important;  /* Önceki 0.5rem idi */
        font-size: 0.85rem !important;     /* Önceki 0.9rem idi */
    }
    
    .login-info p {
        color: #666;
        font-size: 0.75rem !important;     /* Önceki 0.8rem idi */
        margin: 0.1rem 0 !important;       /* Önceki 0.2rem idi */
        opacity: 0.8;
    }
    
    /* Sil butonu */
    .delete-btn {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .delete-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4) !important;
    }
    
    /* Gizli bilgi alanı */
    .hidden-info {
        display: none;
    }
    
    /* Dashboard gizleme/gösterme ayarları */
    .settings-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    /* YENİ MODERN TABLO STİLLERİ */
    .modern-table {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e0e6ed;
    }
    
    .table-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.2rem;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .table-row {
        display: grid;
        grid-template-columns: 2fr 2fr 2fr 1.5fr 1fr;
        padding: 0.8rem 1.2rem;
        border-bottom: 1px solid #f0f0f0;
        align-items: center;
        transition: background-color 0.2s;
    }
    
    .table-row:hover {
        background-color: #f8f9ff;
    }
    
    .table-row:last-child {
        border-bottom: none;
    }
    
    .table-header-row {
        display: grid;
        grid-template-columns: 2fr 2fr 2fr 1.5fr 1fr;
        padding: 0.7rem 1.2rem;
        background-color: #f8f9fa;
        font-weight: 600;
        color: #495057;
        border-bottom: 2px solid #667eea;
        font-size: 0.85rem;
    }
    
    .table-cell {
        padding: 0.3rem 0;
        font-size: 0.85rem;
    }
    
    .status-active {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        display: inline-block;
    }
    
    .status-inactive {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        display: inline-block;
    }
    
    /* YENİ ÇIKIŞ BUTONU STİLİ - SAĞ ÜST */
    .logout-btn-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
    }
    
    .logout-btn {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.4rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3) !important;
    }
    
    .logout-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4) !important;
    }
    
    /* YENİ KÜÇÜK MAC YÖNETİMİ CONTAINER */
    .compact-mac-management {
        max-width: 700px !important;
        margin: 0 auto !important;
        padding: 1rem !important;
    }
    
    /* YENİ KÜÇÜK MAC EKLEME FORMU */
    .compact-mac-form {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e0e6ed;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .compact-section {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# GÜVENLİK SİSTEMİ
class SecuritySystem:
    def __init__(self):
        self.admin_username = "admin"
        self.admin_password = "Ft12345678"
        self.client_username = "plasiyer"
        self.client_password = "iraz3434"
        self.mac_file = "mac_adresleri.csv"
        self.init_mac_file()
    
    def init_mac_file(self):
        if not os.path.exists(self.mac_file):
            df = pd.DataFrame(columns=['mac_adresi', 'kisi_adi', 'eklenme_tarihi', 'durum'])
            df.to_csv(self.mac_file, index=False, encoding='utf-8-sig')
    
    def get_mac_address(self):
        """MAC adresini al"""
        try:
            mac_num = hex(uuid.getnode()).replace('0x', '').upper()
            mac = ':'.join(mac_num[i: i+2] for i in range(0, 11, 2))
            return self.format_mac_address(mac)
        except:
            return "00:00:00:00:00:00"
    
    def format_mac_address(self, mac):
        """MAC adresini standart formata dönüştür"""
        # Önce tüm özel karakterleri temizle
        mac_clean = re.sub(r'[^a-fA-F0-9]', '', mac)
        
        # 12 karakter olana kadar sıfır ekle
        mac_clean = mac_clean.upper().ljust(12, '0')[:12]
        
        # XX:XX:XX:XX:XX:XX formatına dönüştür
        formatted_mac = ':'.join(mac_clean[i:i+2] for i in range(0, 12, 2))
        return formatted_mac
    
    def normalize_mac(self, mac):
        """MAC adresini normalize et (küçük/büyük harf duyarsız)"""
        return self.format_mac_address(mac).upper()
    
    def hash_mac(self, mac):
        """MAC adresini hash'le"""
        normalized_mac = self.normalize_mac(mac)
        return hashlib.sha256(normalized_mac.encode()).hexdigest()
    
    def is_mac_approved(self, mac):
        """MAC adresi onaylı mı kontrol et"""
        try:
            df = pd.read_csv(self.mac_file, encoding='utf-8-sig')
            hashed_mac = self.hash_mac(mac)
            approved = hashed_mac in df['mac_adresi'].values
            return approved
        except:
            return False
    
    def add_mac_address(self, mac, kisi_adi):
        """Yeni MAC adresi ekle"""
        try:
            df = pd.read_csv(self.mac_file, encoding='utf-8-sig')
            hashed_mac = self.hash_mac(mac)
            
            if hashed_mac not in df['mac_adresi'].values:
                new_row = pd.DataFrame({
                    'mac_adresi': [hashed_mac],
                    'kisi_adi': [kisi_adi],
                    'eklenme_tarihi': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    'durum': ['Aktif']
                })
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(self.mac_file, index=False, encoding='utf-8-sig')
                return True, "MAC adresi başarıyla eklendi!"
            else:
                return False, "Bu MAC adresi zaten kayıtlı!"
        except Exception as e:
            return False, f"Hata oluştu: {str(e)}"
    
    def remove_mac_address(self, mac_hash):
        """MAC adresi sil - TAMAMEN DÜZELTİLMİŞ VERSİYON"""
        try:
            df = pd.read_csv(self.mac_file, encoding='utf-8-sig')
            initial_count = len(df)
            
            # Hash'lenmiş MAC adresini ara ve sil
            df = df[df['mac_adresi'] != mac_hash]
            
            if len(df) < initial_count:
                df.to_csv(self.mac_file, index=False, encoding='utf-8-sig')
                return True, "MAC adresi başarıyla silindi!"
            else:
                return False, "MAC adresi bulunamadı!"
        except Exception as e:
            return False, f"Hata oluştu: {str(e)}"
    
    def get_all_mac_addresses(self):
        """Tüm MAC adreslerini getir"""
        try:
            df = pd.read_csv(self.mac_file, encoding='utf-8-sig')
            return df
        except:
            return pd.DataFrame()
    
    def normalize_username(self, username):
        """Kullanıcı adını normalize et (küçük/büyük harf duyarsız)"""
        turkish_chars = {'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 
                        'ş': 's', 'Ş': 'S', 'ü': 'u', 'Ü': 'U', 
                        'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'}
        
        username = username.lower()
        for turkish_char, english_char in turkish_chars.items():
            username = username.replace(turkish_char.lower(), english_char)
        
        return username

# GÜVENLİK SİSTEMİNİ BAŞLAT
security = SecuritySystem()

# DASHBOARD AYARLARI - TAMAMEN DÜZELTİLMİŞ
class DashboardSettings:
    def __init__(self):
        # Session state'te ayarlar yoksa varsayılan değerleri ayarla
        if 'dashboard_settings' not in st.session_state:
            st.session_state.dashboard_settings = {
                'show_uretici_analiz': True,
                'show_top_satanlar': True,
                'show_detayli_rapor': True,
                'show_sistem_istatistik': True,
                'show_ai_oneriler': True
            }
    
    def get_settings(self):
        """Ayarları getir"""
        return st.session_state.dashboard_settings
    
    def save_settings(self, settings):
        """Ayarları kaydet"""
        st.session_state.dashboard_settings = settings
    
    def should_show(self, section_key):
        """Belirli bir bölümün gösterilip gösterilmeyeceğini kontrol et"""
        return st.session_state.dashboard_settings.get(section_key, True)
    
    def admin_panel(self):
        """Admin ayar paneli"""
        st.markdown("### ⚙️ Dashboard Görünürlük Ayarları")
        st.markdown("Plasiyer ekranlarında hangi bölümlerin gösterileceğini belirleyin:")
        
        current_settings = self.get_settings()
        
        col1, col2 = st.columns(2)
        
        with col1:
            show_uretici_analiz = st.checkbox(
                "Üretici Analizi Göster", 
                value=current_settings['show_uretici_analiz'],
                help="Üretici bazlı satış analizlerini göster"
            )
            show_top_satanlar = st.checkbox(
                "En Çok Satanlar Göster", 
                value=current_settings['show_top_satanlar'],
                help="En çok satan ürünler listesini göster"
            )
            show_ai_oneriler = st.checkbox(
                "AI Önerileri Göster", 
                value=current_settings['show_ai_oneriler'],
                help="Yapay zeka satış önerilerini göster"
            )
        
        with col2:
            show_detayli_rapor = st.checkbox(
                "Detaylı Rapor Göster", 
                value=current_settings['show_detayli_rapor'],
                help="Detaylı alış geçmişi raporunu göster"
            )
            show_sistem_istatistik = st.checkbox(
                "Sistem İstatistikleri Göster", 
                value=current_settings['show_sistem_istatistik'],
                help="Sistem genel istatistiklerini göster"
            )
        
        if st.button("✅ Ayarları Kaydet", use_container_width=True):
            new_settings = {
                'show_uretici_analiz': show_uretici_analiz,
                'show_top_satanlar': show_top_satanlar,
                'show_detayli_rapor': show_detayli_rapor,
                'show_sistem_istatistik': show_sistem_istatistik,
                'show_ai_oneriler': show_ai_oneriler
            }
            self.save_settings(new_settings)
            st.success("✅ Ayarlar başarıyla kaydedildi! Plasiyer ekranları güncellendi.")

# AYARLARI BAŞLAT
dashboard_settings = DashboardSettings()

# ÇIKIŞ BUTONU FONKSİYONU - DÜZELTİLMİŞ
def render_logout_button():
    """Sağ üst köşede çıkış butonu render et"""
    st.markdown(
        """
        <style>
        .stButton button {
            width: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Sağ üst köşeye butonu yerleştir
    col1, col2, col3 = st.columns([3, 3, 1])
    with col3:
        if st.button("🚪 Çıkış Yap", key="logout_top_right"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.rerun()

# MODERN LOGİN SİSTEMİ
def modern_login_system():
    # Arkaplanı temizle
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Modern login container - %60 DAHA KÜÇÜK
    st.markdown('<div class="modern-login-container">', unsafe_allow_html=True)
    
    # Header - DAHA KÜÇÜK
    st.markdown('''
    <div class="login-header">
        <div class="login-title">🔐 IRAZ PLATFORMU</div>
        <div class="login-subtitle">Güvenli Giriş Yapın</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Giriş formu - DAHA KOMPAKT
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Giriş türü
        login_type = st.selectbox(
            "Hesap Türü",
            ["Admin", "Plasiyer"],
            index=0,
            key="login_type"
        )
        
        # Kullanıcı adı
        username = st.text_input(
            "Kullanıcı Adı",
            placeholder="Kullanıcı adınızı girin...",
            key="username"
        )
        
        # Şifre
        password = st.text_input(
            "Şifre",
            type="password",
            placeholder="Şifrenizi girin...",
            key="password"
        )
        
        # Giriş butonu - YENİ YEŞİL RENK
        if st.button(
            "🚀 Giriş Yap",
            use_container_width=True,
            key="login_button"
        ):
            if username and password:
                normalized_username = security.normalize_username(username)
                
                if login_type == "Admin":
                    # Admin giriş kontrolü
                    if (normalized_username == security.normalize_username(security.admin_username) and 
                        password == security.admin_password):
                        st.session_state.logged_in = True
                        st.session_state.user_type = "Admin"
                        st.success("✅ Admin girişi başarılı!")
                        st.rerun()
                    else:
                        st.error("❌ Hatalı kullanıcı adı veya şifre!")
                
                else:  # Plasiyer
                    # Plasiyer giriş kontrolü
                    if (normalized_username == security.normalize_username(security.client_username) and 
                        password == security.client_password):
                        
                        mac_address = security.get_mac_address()
                        if security.is_mac_approved(mac_address):
                            st.session_state.logged_in = True
                            st.session_state.user_type = "Plasiyer"
                            st.session_state.mac_address = mac_address
                            st.success("✅ Plasiyer girişi başarılı!")
                            st.rerun()
                        else:
                            st.error("❌ Bu cihaz yetkili değil! Lütfen admin ile iletişime geçin.")
                            st.info(f"📱 Cihazınızın MAC Adresi: `{mac_address}`")
                    else:
                        st.error("❌ Hatalı kullanıcı adı veya şifre!")
            else:
                st.warning("⚠️ Lütfen tüm alanları doldurun!")
    
    # Gizli bilgi alanı (sadece geliştirici için) - DAHA KÜÇÜK
    with st.expander("ℹ️ Sistem Bilgisi", expanded=False):
        st.caption("Bu bilgiler sadece geliştirme amaçlıdır")
        current_mac = security.get_mac_address()
        st.code(f"MAC: {current_mac}")
        
        # Giriş bilgileri (gizli)
        st.markdown('<div class="hidden-info">', unsafe_allow_html=True)
        st.write("**Test Hesapları:**")
        st.write(f"- Admin: {security.admin_username} / {security.admin_password}")
        st.write(f"- Plasiyer: {security.client_username} / {security.client_password}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# MODERN TABLO GÖRÜNÜMÜ - DÜZELTİLMİŞ
def render_mac_table(mac_list):
    """Modern tablo görünümü ile MAC adreslerini render et"""
    if mac_list.empty:
        st.info("ℹ️ Henüz kayıtlı MAC adresi bulunmuyor.")
        return
    
    st.markdown('<div class="compact-section">', unsafe_allow_html=True)
    st.markdown("#### 📋 Kayıtlı MAC Adresleri")
    
    # Tablo başlığı
    st.markdown("""
    <div class="modern-table">
        <div class="table-header-row">
            <div class="table-cell">MAC Adresi</div>
            <div class="table-cell">Kişi Adı</div>
            <div class="table-cell">Eklenme Tarihi</div>
            <div class="table-cell">Durum</div>
            <div class="table-cell">İşlem</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tablo satırları
    for index, row in mac_list.iterrows():
        st.markdown('<div class="table-row">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1.5, 1])
        
        with col1:
            # Örnek MAC formatı göster
            st.write(f"`{security.normalize_mac('A1B2C3D4E5F6')}`")
            st.caption(f"Hash: {row['mac_adresi'][:12]}...")
        
        with col2:
            st.write(row['kisi_adi'])
        
        with col3:
            st.write(row['eklenme_tarihi'])
        
        with col4:
            if row['durum'] == 'Aktif':
                st.markdown('<div class="status-active">AKTİF</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-inactive">PASİF</div>', unsafe_allow_html=True)
        
        with col5:
            # DÜZELTİLMİŞ SİLME BUTONU - Hash'lenmiş MAC adresini doğrudan kullan
            if st.button("🗑️", key=f"delete_{index}", help="Bu MAC adresini sil"):
                success, message = security.remove_mac_address(row['mac_adresi'])
                if success:
                    st.success("✅ " + message)
                    st.rerun()
                else:
                    st.error("❌ " + message)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ADMIN PANELİ - YENİ TASARIM
def admin_panel():
    # ÇIKIŞ BUTONU - SAĞ ÜST
    render_logout_button()
    
    st.markdown('<div class="main-header">👨‍💼 Admin Paneli - IRAZ PLATFORMU</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 MAC Adres Yönetimi", "⚙️ Dashboard Ayarları", "📊 Sistem Bilgileri"])
    
    with tab1:
        # YENİ KOMPAKT MAC YÖNETİMİ
        st.markdown('<div class="compact-mac-management">', unsafe_allow_html=True)
        
        # YENİ MAC EKLEME FORMU - KOMPAKT
        st.markdown('<div class="compact-mac-form">', unsafe_allow_html=True)
        st.markdown("#### ➕ Yeni MAC Adresi Ekle")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            new_mac = st.text_input(
                "MAC Adresi", 
                placeholder="C85142647BBA",
                help="MAC adresini herhangi bir formatta girebilirsiniz",
                key="new_mac_input"
            )
        
        with col2:
            kisi_adi = st.text_input(
                "Kişi Adı Soyadı", 
                placeholder="Ahmet Yılmaz",
                help="Bu MAC adresinin sahibinin adı",
                key="kisi_adi_input"
            )
        
        with col3:
            st.write("")  # Boşluk için
            st.write("")
            if st.button("✅ Ekle", use_container_width=True, key="add_mac_button"):
                if new_mac and kisi_adi:
                    success, message = security.add_mac_address(new_mac, kisi_adi)
                    if success:
                        st.success("✅ " + message)
                        st.rerun()
                    else:
                        st.error("❌ " + message)
                else:
                    st.warning("⚠️ Lütfen MAC adresi ve kişi adı giriniz!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # KAYITLI MAC ADRESLERİ - MODERN TABLO
        mac_list = security.get_all_mac_addresses()
        render_mac_table(mac_list)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # DASHBOARD AYARLARI
        dashboard_settings.admin_panel()
    
    with tab3:
        st.markdown('<div class="compact-section">', unsafe_allow_html=True)
        st.markdown("#### 📊 Sistem İstatistikleri")
        
        mac_list = security.get_all_mac_addresses()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👥 Toplam Kayıtlı Cihaz", len(mac_list))
        
        with col2:
            active_devices = len(mac_list[mac_list['durum'] == 'Aktif']) if not mac_list.empty else 0
            st.metric("🟢 Aktif Cihazlar", active_devices)
        
        with col3:
            st.metric("📅 Son Güncelleme", datetime.now().strftime("%d.%m.%Y"))
        
        # Mevcut MAC adresi
        current_mac = security.get_mac_address()
        st.info(f"**🖥️ Mevcut Admin Cihaz MAC:** `{current_mac}`")
        st.markdown('</div>', unsafe_allow_html=True)

# VERİ YÜKLEME FONKSİYONU
@st.cache_data
def load_musteri_alis_data():
    try:
        conn = pymssql.connect(
            'DRIVER={SQL Server};'
            'SERVER=IRAZOTOMOTIV;'
            'DATABASE=LOGOGO3;'
            'UID=sa;'
            'PWD=Logo12345678;'
        )
        
        musteri_sorgu = """
        SELECT 
            C.DEFINITION_ AS MusteriAdi,
            S.DATE_ AS AlisTarihi,
            YEAR(S.DATE_) AS Yil,
            MONTH(S.DATE_) AS Ay,
            DATENAME(MONTH, S.DATE_) AS AyAdi,
            I.CODE AS MalzemeKodu,
            I.NAME AS MalzemeAdi,
            I.STGRPCODE AS Uretici,
            I.SPECODE AS AracModeli,
            I.CYPHCODE AS AracMarkasi,
            S.AMOUNT AS Miktar
                
        FROM LG_013_CLCARD C
        INNER JOIN LG_013_01_STLINE S ON S.CLIENTREF = C.LOGICALREF
        INNER JOIN LG_013_ITEMS I ON I.LOGICALREF = S.STOCKREF
        WHERE S.TRCODE IN (7, 8)
            AND S.CANCELLED = 0
            AND S.DATE_ >= DATEADD(YEAR, -2, GETDATE())
        ORDER BY AlisTarihi DESC
        """
        
        df_musteri = pd.read_sql(musteri_sorgu, conn)
        conn.close()
        
        if not df_musteri.empty:
            df_musteri['AlisTarihi'] = pd.to_datetime(df_musteri['AlisTarihi'])
            df_musteri['YilAy'] = df_musteri['AlisTarihi'].dt.strftime('%Y-%m')
            df_musteri['Hafta'] = df_musteri['AlisTarihi'].dt.isocalendar().week
            df_musteri['Gun'] = df_musteri['AlisTarihi'].dt.day_name()
            
            # Türkçe gün isimleri
            gun_cevirimi = {
                'Monday': 'Pazartesi',
                'Tuesday': 'Salı', 
                'Wednesday': 'Çarşamba',
                'Thursday': 'Perşembe',
                'Friday': 'Cuma',
                'Saturday': 'Cumartesi',
                'Sunday': 'Pazar'
            }
            df_musteri['Gun'] = df_musteri['Gun'].map(gun_cevirimi)
            
            # NULL değerleri temizle
            df_musteri['AracModeli'] = df_musteri['AracModeli'].fillna('BELİRSİZ')
            df_musteri['AracMarkasi'] = df_musteri['AracMarkasi'].fillna('BELİRSİZ')
            df_musteri['Uretici'] = df_musteri['Uretici'].fillna('BELİRSİZ')
        
        return df_musteri
        
    except Exception as e:
        st.error(f"Veri yüklenme hatası: {e}")
        return pd.DataFrame()

# İSTATİSTİK FONKSİYONLARI
def get_genel_istatistikler(df, gun_sayisi=30):
    """Genel istatistikleri hesapla - GÜNCELLENMİŞ TARİH FİLTRELİ"""
    bugun = datetime.now().date()
    
    # Seçilen gün sayısına göre filtrele
    baslangic_tarihi = bugun - timedelta(days=gun_sayisi)
    filtreli_df = df[df['AlisTarihi'].dt.date >= baslangic_tarihi]
    
    # Son 30 gün
    son_30_gun = df[df['AlisTarihi'].dt.date >= (bugun - timedelta(days=30))]
    
    # Bu ay en çok satılanlar
    bu_ay = df[df['AlisTarihi'].dt.month == bugun.month]
    bu_ay_top_10 = bu_ay.groupby('MalzemeKodu').agg({
        'Miktar': 'sum',
        'MalzemeAdi': 'first'
    }).nlargest(10, 'Miktar').reset_index()
    
    # Üretici analizi
    uretici_analiz = filtreli_df.groupby('Uretici').agg({
        'Miktar': 'sum',
        'MalzemeKodu': 'nunique'
    }).reset_index()
    uretici_analiz['Yuzde'] = (uretici_analiz['Miktar'] / uretici_analiz['Miktar'].sum() * 100).round(1)
    
    return {
        'toplam_musteri': filtreli_df['MusteriAdi'].nunique(),
        'toplam_alis': filtreli_df['Miktar'].sum(),
        'toplam_islem': len(filtreli_df),
        'ortalama_alis': filtreli_df['Miktar'].mean(),
        'benzersiz_urun': filtreli_df['MalzemeKodu'].nunique(),
        'son_30_gun_alis': son_30_gun['Miktar'].sum(),
        'bu_ay_top_10': bu_ay_top_10,
        'uretici_analiz': uretici_analiz.sort_values('Miktar', ascending=False),
        'son_6_ay_uretim': filtreli_df.groupby('Uretici')['Miktar'].sum().nlargest(10),
        'gun_sayisi': gun_sayisi
    }

# YAPAY ZEKA ANALİZ FONKSİYONLARI
def analyze_customer_behavior(df, musteri_adi):
    """Müşteri davranış analizi"""
    musteri_df = df[df['MusteriAdi'] == musteri_adi].copy()
    
    if musteri_df.empty:
        return None
    
    # Temel metrikler
    toplam_alis = musteri_df['Miktar'].sum()
    ortalama_alis = musteri_df['Miktar'].mean()
    alis_sayisi = len(musteri_df)
    benzersiz_urun = musteri_df['MalzemeKodu'].nunique()
    
    # Aylık trend
    aylik_trend = musteri_df.groupby('YilAy').agg({
        'Miktar': 'sum',
        'MalzemeKodu': 'nunique'
    }).reset_index()
    
    # Haftalık alış pattern
    haftalik_pattern = musteri_df.groupby('Hafta')['Miktar'].sum().reset_index()
    
    # Günlük alış pattern
    gunluk_pattern = musteri_df.groupby('Gun')['Miktar'].sum().reset_index()
    
    # Ürün konsantrasyonu
    urun_konsantrasyon = musteri_df.groupby('MalzemeKodu').agg({
        'Miktar': 'sum',
        'AlisTarihi': 'count'
    }).nlargest(10, 'Miktar')
    
    # Mevsimsel analiz
    mevsimsel_analiz = musteri_df.groupby('Ay').agg({
        'Miktar': 'sum',
        'AlisTarihi': 'count'
    }).reset_index()
    
    return {
        'temel_metrikler': {
            'toplam_alis': toplam_alis,
            'ortalama_alis': ortalama_alis,
            'alis_sayisi': alis_sayisi,
            'benzersiz_urun': benzersiz_urun
        },
        'aylik_trend': aylik_trend,
        'haftalik_pattern': haftalik_pattern,
        'gunluk_pattern': gunluk_pattern,
        'urun_konsantrasyon': urun_konsantrasyon,
        'mevsimsel_analiz': mevsimsel_analiz,
        'ham_veri': musteri_df
    }

def generate_ai_recommendations(analysis):
    """Yapay zeka önerileri oluştur"""
    if not analysis:
        return []
    
    metrikler = analysis['temel_metrikler']
    urun_kons = analysis['urun_konsantrasyon']
    mevsimsel = analysis['mevsimsel_analiz']
    
    oneriler = []
    
    # Alış frekansı analizi
    if metrikler['alis_sayisi'] > 50:
        oneriler.append({
            'type': 'success',
            'title': '🎯 Yüksek Frekanslı Müşteri',
            'message': f"Bu müşteri {metrikler['alis_sayisi']} alış yapmış. Düzenli takip gerektirir.",
            'action': 'Haftalık ziyaret planı oluştur'
        })
    elif metrikler['alis_sayisi'] > 20:
        oneriler.append({
            'type': 'info',
            'title': '📈 Orta Frekanslı Müşteri',
            'message': f"{metrikler['alis_sayisi']} alış ile dengeli bir müşteri.",
            'action': 'Aylık takip planı yap'
        })
    else:
        oneriler.append({
            'type': 'warning',
            'title': '💎 Gelişim Potansiyeli',
            'message': f"Sadece {metrikler['alis_sayisi']} alış. Potansiyel artırılabilir.",
            'action': 'Özel kampanya öner'
        })
    
    # Ürün çeşitliliği
    if metrikler['benzersiz_urun'] < 5:
        oneriler.append({
            'type': 'info',
            'title': '🔄 Ürün Çeşitlendirme',
            'message': f"Sadece {metrikler['benzersiz_urun']} farklı ürün alıyor. Çeşitlilik artırılabilir.",
            'action': 'Benzer ürünler öner'
        })
    else:
        oneriler.append({
            'type': 'success',
            'title': '🌈 Çeşitli Alış',
            'message': f"{metrikler['benzersiz_urun']} farklı ürün ile çeşitli alış yapıyor.",
            'action': 'Yeni ürünler tanıt'
        })
    
    # Mevsimsel öneriler
    if not mevsimsel.empty:
        en_yuksek_ay = mevsimsel.loc[mevsimsel['Miktar'].idxmax(), 'Ay']
        oneriler.append({
            'type': 'info',
            'title': '📅 Mevsimsel Yoğunluk',
            'message': f"En yoğun alışlar {en_yuksek_ay}. ayında gerçekleşmiş.",
            'action': 'Önümüzdeki ay için stok hazırla'
        })
    
    # Toplu alım analizi
    if metrikler['ortalama_alis'] > 20:
        oneriler.append({
            'type': 'success',
            'title': '📦 Toplu Alım Müşterisi',
            'message': f"Ortalama {metrikler['ortalama_alis']:.1f} adet alım. İndirim fırsatı değerlendirilebilir.",
            'action': 'Toplu alım indirimi teklif et'
        })
    elif metrikler['ortalama_alis'] < 5:
        oneriler.append({
            'type': 'warning',
            'title': '🛒 Küçük Miktarlı Alış',
            'message': f"Ortalama {metrikler['ortalama_alis']:.1f} adet alım. Miktarı artırmaya yönelik teklifler yapılabilir.",
            'action': 'Paket teklifleri sun'
        })
    
    return oneriler

# ANA UYGULAMA - DASHBOARD AYARLARI ENTEGRE
def main_app():
    # ÇIKIŞ BUTONU - SAĞ ÜST
    render_logout_button()
    
    # BAŞLIK - YENİ İSİM
    st.markdown('<div class="main-header">🤖 IRAZ PLATFORMU</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Müşteri Davranışları & Akıllı Satış Önerileri</div>', unsafe_allow_html=True)
    
    # VERİ YÜKLEME
    with st.spinner('🤖 Müşteri verileri analiz ediliyor...'):
        df = load_musteri_alis_data()
    
    if df.empty:
        st.error("Veri yüklenemedi. Lütfen bağlantıyı kontrol edin.")
        return
    
    st.success(f"✅ {len(df):,} alış kaydı hazır")
    
    # FİLTRELEME PANELİ - MOBILE FRIENDLY
    st.markdown("### 🔍 Müşteri Analiz Filtreleri")
    
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            musteriler = sorted(df['MusteriAdi'].unique())
            secilen_musteri = st.selectbox(
                "👥 Müşteri Seçin:",
                options=[""] + musteriler,
                help="Analiz etmek istediğiniz müşteriyi seçin",
                placeholder="Müşteri seçin..."
            )
        
        with col2:
            # YENİ TARİH SEÇENEKLERİ
            tarih_secenekleri = {
                "Son 1 Gün": 1,
                "Son 3 Gün": 3,
                "Son 1 Hafta": 7,
                "Son 1 Ay": 30,
                "Son 3 Ay": 90,
                "Son 6 Ay": 180
            }
            secilen_tarih = st.selectbox(
                "📅 Zaman Aralığı:",
                options=list(tarih_secenekleri.keys()),
                index=3  # Varsayılan olarak Son 1 Ay
            )
        
        # İkinci satır filtreler
        col3, col4, col5 = st.columns(3)
        
        with col3:
            ureticiler = sorted([x for x in df['Uretici'].unique() if x != 'BELİRSİZ'])
            secilen_uretici = st.multiselect(
                "🏭 Üretici Filtresi:",
                options=ureticiler,
                help="Belirli üreticileri filtreleyin",
                placeholder="Üretici seçin..."
            )
        
        with col4:
            malzemeler = sorted(df['MalzemeKodu'].unique())
            secilen_malzeme = st.multiselect(
                "📦 Malzeme Filtresi:",
                options=malzemeler,
                help="Belirli malzemeleri filtreleyin",
                placeholder="Malzeme seçin..."
            )
        
        with col5:
            modeller = sorted([x for x in df['AracModeli'].unique() if x != 'BELİRSİZ'])
            secilen_model = st.multiselect(
                "🚗 Araç Modeli Filtresi:",
                options=modeller,
                help="Belirli araç modellerini filtreleyin",
                placeholder="Model seçin..."
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # FİLTRE UYGULA
    filtreli_df = df.copy()
    
    # Tarih filtresi - YENİ TARİH SEÇENEKLERİ
    gun_sayisi = tarih_secenekleri[secilen_tarih]
    baslangic_tarihi = datetime.now() - timedelta(days=gun_sayisi)
    filtreli_df = filtreli_df[filtreli_df['AlisTarihi'] >= baslangic_tarihi]
    
    if secilen_uretici:
        filtreli_df = filtreli_df[filtreli_df['Uretici'].isin(secilen_uretici)]
    
    if secilen_malzeme:
        filtreli_df = filtreli_df[filtreli_df['MalzemeKodu'].isin(secilen_malzeme)]
    
    if secilen_model:
        filtreli_df = filtreli_df[filtreli_df['AracModeli'].isin(secilen_model)]
    
    # MÜŞTERİ ANALİZİ veya GENEL DASHBOARD
    if secilen_musteri:
        # MÜŞTERİ ÖZEL ANALİZ
        st.markdown(f"## 👤 {secilen_musteri} - Detaylı Analiz")
        
        with st.spinner('🤖 Müşteri davranışları analiz ediliyor...'):
            analysis = analyze_customer_behavior(filtreli_df, secilen_musteri)
        
        if not analysis:
            st.warning("Seçilen müşteri için veri bulunamadı.")
            return
        
        # YENİ METRİK PANOSU - DAHA SADE VE MODERN
        st.markdown("### 📊 Temel Performans Metrikleri")
        
        metrikler = analysis['temel_metrikler']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrikler['toplam_alis']:,.0f}</div>
                <div class="metric-label">Toplam Alış (adet)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrikler['alis_sayisi']}</div>
                <div class="metric-label">Alış Sayısı</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrikler['benzersiz_urun']}</div>
                <div class="metric-label">Ürün Çeşidi</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrikler['ortalama_alis']:.1f}</div>
                <div class="metric-label">Ort. Alış (adet)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # SEKMELER - DASHBOARD AYARLARI ENTEGRE
        tab_names = ["📈 Trend Analizi"]
        
        # Dashboard ayarlarına göre sekmeleri kontrol et
        if dashboard_settings.should_show('show_ai_oneriler'):
            tab_names.append("🎯 AI Öneriler")
        
        tab_names.append("📦 Ürün Davranışı")
        
        if dashboard_settings.should_show('show_detayli_rapor'):
            tab_names.append("🔍 Detaylı Rapor")
        
        tabs = st.tabs(tab_names)
        
        current_tab = 0
        
        with tabs[current_tab]:
            # TREND ANALİZİ
            st.markdown("#### 📈 Zaman Bazlı Alış Trendleri")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Aylık trend
                if not analysis['aylik_trend'].empty:
                    fig = px.line(analysis['aylik_trend'], x='YilAy', y='Miktar',
                                 title='📅 Aylık Alış Trendi',
                                 labels={'Miktar': 'Alış Miktarı (adet)', 'YilAy': 'Ay'})
                    fig.update_traces(line=dict(width=4, color='#667eea'))
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Aylık trend verisi bulunamadı")
            
            with col2:
                # Günlük pattern
                if not analysis['gunluk_pattern'].empty:
                    fig = px.bar(analysis['gunluk_pattern'], x='Gun', y='Miktar',
                                title='📊 Haftanın Günlerine Göre Alışlar',
                                labels={'Miktar': 'Alış Miktarı', 'Gun': 'Gün'})
                    fig.update_traces(marker_color='#764ba2')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Günlük pattern verisi bulunamadı")
        
        current_tab += 1
        
        # AI ÖNERİLER - AYAR KONTROLÜ
        if dashboard_settings.should_show('show_ai_oneriler'):
            with tabs[current_tab]:
                st.markdown("#### 🤖 Akıllı Satış Önerileri")
                
                oneriler = generate_ai_recommendations(analysis)
                
                # Öneriler
                st.markdown("##### 💡 Aksiyon Önerileri")
                for oneri in oneriler:
                    st.markdown(f"""
                    <div class="ai-card {oneri['type']}">
                        <h4>{oneri['title']}</h4>
                        <p>{oneri['message']}</p>
                        <strong>🚀 Aksiyon: {oneri['action']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
            current_tab += 1
        
        # ÜRÜN DAVRANIŞI
        with tabs[current_tab]:
            st.markdown("#### 📦 Ürün Alış Davranışları")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Ürün konsantrasyonu
                if not analysis['urun_konsantrasyon'].empty:
                    urun_df = analysis['urun_konsantrasyon'].reset_index()
                    fig = px.bar(urun_df.head(8), x='MalzemeKodu', y='Miktar',
                                title='🏆 En Çok Alınan Ürünler',
                                color='Miktar', color_continuous_scale='viridis')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Ürün konsantrasyon verisi bulunamadı")
            
            with col2:
                # Alış dağılımı
                if not analysis['urun_konsantrasyon'].empty:
                    urun_df = analysis['urun_konsantrasyon'].reset_index()
                    fig = px.pie(urun_df.head(6), values='Miktar', names='MalzemeKodu',
                                title='🥧 Ürün Dağılımı',
                                hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
        
        current_tab += 1
        
        # DETAYLI RAPOR - AYAR KONTROLÜ
        if dashboard_settings.should_show('show_detayli_rapor'):
            with tabs[current_tab]:
                st.markdown("#### 🔍 Detaylı Alış Geçmişi")
                
                detay_df = analysis['ham_veri'][['MalzemeKodu', 'MalzemeAdi', 'Miktar', 'AlisTarihi', 'Uretici']].copy()
                detay_df = detay_df.sort_values('AlisTarihi', ascending=False)
                
                st.dataframe(detay_df, use_container_width=True)
                
                # İndirme butonu
                csv = detay_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Detaylı Raporu İndir",
                    data=csv,
                    file_name=f"{secilen_musteri}_alis_raporu.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    else:
        # GENEL DASHBOARD - MÜŞTERİ SEÇİLMEDİĞİNDE
        st.markdown("## 📊 Genel Dashboard")
        
        # YENİ TARİH FİLTRELİ İSTATİSTİKLER
        gun_sayisi = tarih_secenekleri[secilen_tarih]
        with st.spinner(f'📈 Son {gun_sayisi} gün istatistikleri hesaplanıyor...'):
            stats = get_genel_istatistikler(df, gun_sayisi)
        
        # YENİ GENEL METRİKLER - DAHA SADE VE MODERN
        st.markdown("### 🎯 Genel Performans Metrikleri")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['toplam_musteri']:,}</div>
                <div class="metric-label">Toplam Müşteri</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['toplam_alis']:,.0f}</div>
                <div class="metric-label">Toplam Alış (adet)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['toplam_islem']:,}</div>
                <div class="metric-label">Toplam İşlem</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['benzersiz_urun']:,}</div>
                <div class="metric-label">Ürün Çeşidi</div>
            </div>
            """, unsafe_allow_html=True)
        
        # İSTATİSTİK GRAFİKLERİ - AYAR KONTROLLÜ
        st.markdown("### 📈 Detaylı İstatistikler")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bu ay en çok satılanlar - AYAR KONTROLÜ
            if dashboard_settings.should_show('show_top_satanlar'):
                st.markdown("#### 🏆 En Çok Satanlar")
                if not stats['bu_ay_top_10'].empty:
                    fig = px.bar(stats['bu_ay_top_10'].head(10), 
                                x='MalzemeKodu', y='Miktar',
                                title=f'Son {gun_sayisi} Gün En Çok Satan 10 Ürün',
                                color='Miktar',
                                color_continuous_scale='thermal')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Satış verisi bulunamadı")
            else:
                st.info("ℹ️ En Çok Satanlar bölümü admin tarafından gizlenmiştir.")
        
        with col2:
            # Üretici dağılımı - AYAR KONTROLÜ
            if dashboard_settings.should_show('show_uretici_analiz'):
                st.markdown("#### 🏭 Üretici Performansı")
                if not stats['uretici_analiz'].empty:
                    top_ureticiler = stats['uretici_analiz'].head(8)
                    fig = px.pie(top_ureticiler, 
                                values='Miktar', 
                                names='Uretici',
                                title=f'Son {gun_sayisi} Gün Üretici Dağılımı',
                                hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Üretici verisi bulunamadı")
            else:
                st.info("ℹ️ Üretici Analizi bölümü admin tarafından gizlenmiştir.")
        
        # DETAYLI TABLOLAR - AYAR KONTROLLÜ
        col1, col2 = st.columns(2)
        
        with col1:
            # Üretici bazlı analiz - AYAR KONTROLÜ
            if dashboard_settings.should_show('show_uretici_analiz'):
                st.markdown("#### 📊 Üretici Bazlı Analiz")
                if not stats['uretici_analiz'].empty:
                    display_df = stats['uretici_analiz'].head(10)[['Uretici', 'Miktar', 'Yuzde']]
                    display_df['Yuzde'] = display_df['Yuzde'].astype(str) + '%'
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info("ℹ️ Üretici Analizi bölümü admin tarafından gizlenmiştir.")
        
        with col2:
            # Hızlı İstatistikler - AYAR KONTROLÜ
            if dashboard_settings.should_show('show_sistem_istatistik'):
                st.markdown("#### 🔥 Hızlı İstatistikler")
                st.metric(f"Son {gun_sayisi} Gün Alış", f"{stats['toplam_alis']:,.0f} adet")
                st.metric("Ortalama Alış Miktarı", f"{stats['ortalama_alis']:.1f} adet")
                st.metric("Aktif Ürün Çeşidi", f"{stats['benzersiz_urun']:,}")
                st.metric("İşlem Başına Ortalama", f"{(stats['toplam_alis']/stats['toplam_islem']):.1f} adet")
            else:
                st.info("ℹ️ Sistem İstatistikleri bölümü admin tarafından gizlenmiştir.")

# ANA YÖNETİM
def main():
    # Session state kontrolü
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_type = None
    
    # Giriş kontrolü
    if not st.session_state.logged_in:
        modern_login_system()
        return
    
    # Admin veya Plasiyer panelleri
    if st.session_state.user_type == "Admin":
        admin_panel()
    else:
        main_app()

# UYGULAMAYI ÇALIŞTIR
if __name__ == "__main__":
    main()
    
    # ALT BİLGİ - YENİ İSİM
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🤖 <strong>IRAZ PLATFORMU v4.0</strong> | "
        "Mobil Optimize | MAC Güvenlik Sistemi | Yapay Zeka Destekli"
        "</div>",
        unsafe_allow_html=True

    )

