import warnings
warnings.filterwarnings("ignore")

import requests
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
import streamlit as st

# ══════════════════════════════════════════════════════════
TELEGRAM_TOKEN   = "8873844474:AAHlkjzubj9skBop74jWk3kVE8ZF_7rf8og"
TELEGRAM_CHAT_ID = "8687873908"
# ══════════════════════════════════════════════════════════

st.set_page_config(page_title="52-Week High Screener", page_icon="📈", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #161b27; }
[data-testid="stSidebar"] * { color: #f1f5f9; }
.signal-card {
    background: #1c2333; border-radius: 10px; padding: 12px 16px;
    border-left: 4px solid #22c55e; margin-bottom: 8px;
}
.signal-card.warn { border-left-color: #f59e0b; }
.signal-card.bad  { border-left-color: #ef4444; }
.badge {
    display:inline-block; padding:2px 8px; border-radius:20px;
    font-size:11px; font-weight:600; margin-right:4px;
}
.b-green { background:#166534; color:#86efac; }
.b-red   { background:#7f1d1d; color:#fca5a5; }
</style>
""", unsafe_allow_html=True)

# ── Tickers ───────────────────────────────────────────────

SP500_TICKERS = [
    "MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A","APD","ABNB","AKAM","ALB","ARE",
    "ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN","AMCR","AEE","AAL","AEP","AXP","AIG",
    "AMT","AWK","AMP","AME","AMGN","APH","ADI","ANSS","AON","APA","AAPL","AMAT","APTV","ACGL",
    "ADM","ANET","AJG","AIZ","T","ATO","ADSK","ADP","AZO","AVB","AVY","AXON","BKR","BALL","BAC",
    "BK","BBWI","BAX","BDX","BRK-B","BBY","BIO","BIIB","BLK","BX","BA","BSX","BMY","AVGO","BR",
    "BRO","BLDR","BG","CDNS","CPT","CPB","COF","CAH","KMX","CCL","CARR","CAT","CBOE","CBRE","CDW",
    "CE","COR","CNC","CNP","CF","CRL","SCHW","CHTR","CVX","CMG","CB","CHD","CI","CINF","CTAS",
    "CSCO","C","CFG","CLX","CME","CMS","KO","CTSH","CL","CMCSA","CAG","COP","ED","STZ","CEG",
    "COO","CPRT","GLW","CTVA","CSGP","COST","CTRA","CCI","CSX","CMI","CVS","DHR","DRI","DVA",
    "DE","DAL","DVN","DXCM","FANG","DLR","DFS","DG","DLTR","D","DPZ","DOV","DOW","DHI","DTE",
    "DUK","DD","EMN","ETN","EBAY","ECL","EIX","EW","EA","ELV","EMR","ENPH","ETR","EOG","EFX",
    "EQIX","EQR","ESS","EL","ETSY","EG","ES","EXC","EXPE","EXPD","EXR","XOM","FFIV","FDS","FICO",
    "FAST","FRT","FDX","FIS","FITB","FSLR","FE","FI","FMC","F","FTNT","FTV","FOXA","FOX","BEN",
    "FCX","GRMN","IT","GE","GEHC","GEV","GEN","GNRC","GD","GIS","GM","GPC","GILD","GPN","GL",
    "GDDY","GS","HAL","HIG","HAS","HCA","HSIC","HSY","HES","HPE","HLT","HOLX","HD","HON","HRL",
    "HST","HWM","HPQ","HUBB","HUM","HBAN","HII","IBM","IEX","IDXX","ITW","INCY","IR","INTC","ICE",
    "IFF","IP","IPG","INTU","ISRG","IVZ","INVH","IQV","IRM","J","JBL","JPM","K","KVUE","KDP",
    "KEY","KEYS","KMB","KIM","KMI","KKR","KLAC","KHC","KR","LHX","LH","LRCX","LW","LVS","LDOS",
    "LEN","LII","LIN","LYV","LKQ","LMT","L","LOW","LULU","LYB","MTB","MRO","MPC","MKTX","MAR",
    "MMC","MLM","MAS","MA","MTCH","MKC","MCD","MCK","MDT","MRK","META","MET","MTD","MGM","MCHP",
    "MU","MSFT","MAA","MRNA","MHK","MOH","TAP","MDLZ","MPWR","MNST","MCO","MS","MOS","MSI","MSCI",
    "NDAQ","NTAP","NFLX","NEM","NWSA","NWS","NEE","NKE","NI","NDSN","NSC","NTRS","NOC","NCLH",
    "NRG","NUE","NVDA","NVR","NXPI","ORLY","OXY","ODFL","OMC","ON","OKE","ORCL","OTIS","PCAR",
    "PKG","PLTR","PH","PAYX","PAYC","PYPL","PNR","PEP","PFE","PCG","PM","PSX","PNW","PNC","POOL",
    "PPG","PPL","PFG","PG","PGR","PLD","PRU","PEG","PTC","PSA","PHM","PWR","QCOM","DGX","RL",
    "RJF","RTX","O","REG","REGN","RF","RSG","RMD","RVTY","ROK","ROL","ROP","ROST","RCL","SPGI",
    "CRM","SBAC","SLB","STX","SRE","NOW","SHW","SPG","SWKS","SJM","SNA","SOLV","SO","LUV","SWK",
    "SBUX","STT","STLD","STE","SYK","SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TRGP","TGT",
    "TEL","TDY","TFX","TER","TSLA","TXN","TXT","TMO","TJX","TSCO","TT","TDG","TRV","TRMB","TFC",
    "TYL","TSN","USB","UBER","UDR","ULTA","UNP","UAL","UPS","URI","UNH","UHS","VLO","VTR","VRSN",
    "VRSK","VZ","VRTX","VICI","V","VST","VMC","WRB","GWW","WAB","WBA","WMT","DIS","WBD","WM",
    "WAT","WEC","WFC","WELL","WST","WDC","WY","WMB","WTW","WYNN","XEL","XYL","YUM","ZBRA","ZBH","ZTS"
]
NASDAQ100_TICKERS = [
    "ADBE","ADP","ABNB","GOOGL","GOOG","AMZN","AMD","AEP","AMGN","ADI","ANSS","AAPL","AMAT",
    "ANET","ASML","TEAM","ADSK","AVGO","CDNS","CHTR","CTAS","CSCO","CTSH","CMCSA","CEG","CPRT",
    "CSGP","COST","CRWD","CSX","DDOG","DXCM","FANG","DLTR","EA","ENPH","EXC","FAST","FTNT",
    "GEHC","GILD","HON","IDXX","INTC","INTU","ISRG","KDP","KLAC","KHC","LRCX","LULU","MAR",
    "MRVL","MTCH","MELI","META","MCHP","MU","MSFT","MRNA","MDLZ","MDB","MNST","NDAQ","NFLX",
    "NVDA","NXPI","ODFL","ORLY","ON","PCAR","PANW","PAYX","PYPL","PEP","QCOM","REGN","ROP",
    "ROST","SBUX","SNPS","TTWO","TMUS","TSLA","TXN","VRSK","VRTX","WBD","WBA","WDAY","XEL",
    "ZS","ZM","BIIB","BKNG","EBAY","ILMN"
]
DJIA_TICKERS = [
    "MMM","AXP","AMGN","AAPL","BA","CAT","CVX","CSCO","KO","DOW",
    "GS","HD","HON","IBM","JNJ","JPM","MCD","MRK","MSFT","NKE",
    "PG","CRM","TRV","UNH","VZ","V","WBA","WMT","DIS","RTX"
]
NIFTY500_TICKERS = [
    "360ONE.NS","3MINDIA.NS","ABB.NS","ACC.NS","ACMESOLAR.NS","AIAENG.NS","APLAPOLLO.NS",
    "AUBANK.NS","AWL.NS","AADHARHFC.NS","AARTIIND.NS","AAVAS.NS","ABBOTINDIA.NS","ACE.NS",
    "ACUTAAS.NS","ADANIENSOL.NS","ADANIENT.NS","ADANIGREEN.NS","ADANIPORTS.NS","ADANIPOWER.NS",
    "ATGL.NS","ABCAPITAL.NS","ABFRL.NS","ABLBL.NS","ABREL.NS","ABSLAMC.NS","CPPLUS.NS",
    "AEGISLOG.NS","AEGISVOPAK.NS","AFCONS.NS","AFFLE.NS","AJANTPHARM.NS","ALKEM.NS","ABDL.NS",
    "ARE&M.NS","AMBER.NS","AMBUJACEM.NS","ANANDRATHI.NS","ANANTRAJ.NS","ANGELONE.NS","ANTHEM.NS",
    "ANURAS.NS","APARINDS.NS","APOLLOHOSP.NS","APOLLOTYRE.NS","APTUS.NS","ASAHIINDIA.NS",
    "ASHOKLEY.NS","ASIANPAINT.NS","ASTERDM.NS","ASTRAL.NS","ATHERENERG.NS","ATUL.NS",
    "AUROPHARMA.NS","AIIL.NS","DMART.NS","AXISBANK.NS","BEML.NS","BLS.NS","BSE.NS",
    "BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BAJAJHLDNG.NS","BAJAJHFL.NS",
    "BALKRISIND.NS","BALRAMCHIN.NS","BANDHANBNK.NS","BANKBARODA.NS","BANKINDIA.NS",
    "MAHABANK.NS","BATAINDIA.NS","BAYERCROP.NS","BELRISE.NS","BERGEPAINT.NS","BDL.NS",
    "BEL.NS","BHARATFORG.NS","BHEL.NS","BPCL.NS","BHARTIARTL.NS","BHARTIHEXA.NS","BIKAJI.NS",
    "GROWW.NS","BIOCON.NS","BSOFT.NS","BLUEDART.NS","BLUEJET.NS","BLUESTARCO.NS","BBTC.NS",
    "BOSCHLTD.NS","FIRSTCRY.NS","BRIGADE.NS","BRITANNIA.NS","MAPMYINDIA.NS","CCL.NS","CESC.NS",
    "CGPOWER.NS","CIEINDIA.NS","CRISIL.NS","CANFINHOME.NS","CANBK.NS","CANHLIFE.NS",
    "CAPLIPOINT.NS","CGCL.NS","CARBORUNIV.NS","CARTRADE.NS","CASTROLIND.NS","CEATLTD.NS",
    "CEMPRO.NS","CENTRALBK.NS","CDSL.NS","CHALET.NS","CHAMBLFERT.NS","CHENNPETRO.NS",
    "CHOICEIN.NS","CHOLAHLDNG.NS","CHOLAFIN.NS","CIPLA.NS","CUB.NS","CLEAN.NS","COALINDIA.NS",
    "COCHINSHIP.NS","COFORGE.NS","COHANCE.NS","COLPAL.NS","CAMS.NS","CONCORDBIO.NS","CONCOR.NS",
    "COROMANDEL.NS","CRAFTSMAN.NS","CREDITACC.NS","CROMPTON.NS","CUMMINSIND.NS","CYIENT.NS",
    "DCMSHRIRAM.NS","DLF.NS","DOMS.NS","DABUR.NS","DALBHARAT.NS","DATAPATTNS.NS",
    "DEEPAKFERT.NS","DEEPAKNTR.NS","DELHIVERY.NS","DEVYANI.NS","DIVISLAB.NS","DIXON.NS",
    "LALPATHLAB.NS","DRREDDY.NS","EIDPARRY.NS","EIHOTEL.NS","EICHERMOT.NS","ELECON.NS",
    "ELGIEQUIP.NS","EMAMILTD.NS","EMCURE.NS","EMMVEE.NS","ENDURANCE.NS","ENGINERSIN.NS",
    "ERIS.NS","ESCORTS.NS","ETERNAL.NS","EXIDEIND.NS","NYKAA.NS","FEDERALBNK.NS","FACT.NS",
    "FINCABLES.NS","FSL.NS","FIVESTAR.NS","FORCEMOT.NS","FORTIS.NS","GAIL.NS","GVT&D.NS",
    "GMRAIRPORT.NS","GABRIEL.NS","GALLANTT.NS","GRSE.NS","GICRE.NS","GILLETTE.NS","GLAND.NS",
    "GLAXO.NS","GLENMARK.NS","MEDANTA.NS","GODIGIT.NS","GPIL.NS","GODFRYPHLP.NS","GODREJCP.NS",
    "GODREJIND.NS","GODREJPROP.NS","GRANULES.NS","GRAPHITE.NS","GRASIM.NS","GRAVITA.NS",
    "GESHIP.NS","FLUOROCHEM.NS","GMDCLTD.NS","HEG.NS","HBLENGINE.NS","HCLTECH.NS","HDBFS.NS",
    "HDFCAMC.NS","HDFCBANK.NS","HDFCLIFE.NS","HFCL.NS","HAVELLS.NS","HEROMOTOCO.NS","HEXT.NS",
    "HSCL.NS","HINDALCO.NS","HAL.NS","HINDCOPPER.NS","HINDPETRO.NS","HINDUNILVR.NS",
    "HINDZINC.NS","POWERINDIA.NS","HOMEFIRST.NS","HONASA.NS","HONAUT.NS","HUDCO.NS",
    "HYUNDAI.NS","ICICIBANK.NS","ICICIGI.NS","ICICIAMC.NS","ICICIPRULI.NS","IDBI.NS",
    "IDFCFIRSTB.NS","IFCI.NS","IIFL.NS","IRB.NS","IRCON.NS","ITCHOTELS.NS","ITC.NS","ITI.NS",
    "INDGN.NS","INDIACEM.NS","INDIAMART.NS","INDIANB.NS","IEX.NS","INDHOTEL.NS","IOC.NS",
    "IOB.NS","IRCTC.NS","IRFC.NS","IREDA.NS","IGL.NS","INDUSTOWER.NS","INDUSINDBK.NS",
    "NAUKRI.NS","INFY.NS","INOXWIND.NS","INTELLECT.NS","INDIGO.NS","IGIL.NS","IKS.NS",
    "IPCALAB.NS","JBCHEPHARM.NS","JKCEMENT.NS","JBMA.NS","JKTYRE.NS","JMFINANCIL.NS",
    "JSWCEMENT.NS","JSWDULUX.NS","JSWENERGY.NS","JSWINFRA.NS","JSWSTEEL.NS","JAINREC.NS",
    "JPPOWER.NS","J&KBANK.NS","JINDALSAW.NS","JSL.NS","JINDALSTEL.NS","JIOFIN.NS",
    "JUBLFOOD.NS","JUBLINGREA.NS","JUBLPHARMA.NS","JWL.NS","JYOTICNC.NS","KPRMILL.NS",
    "KEI.NS","KPITTECH.NS","KAJARIACER.NS","KPIL.NS","KALYANKJIL.NS","KARURVYSYA.NS",
    "KAYNES.NS","KEC.NS","KFINTECH.NS","KIRLOSENG.NS","KOTAKBANK.NS","KIMS.NS","LTF.NS",
    "LTTS.NS","LGEINDIA.NS","LICHSGFIN.NS","LTFOODS.NS","LTM.NS","LT.NS","LATENTVIEW.NS",
    "LAURUSLABS.NS","THELEELA.NS","LEMONTREE.NS","LENSKART.NS","LICI.NS","LINDEINDIA.NS",
    "LLOYDSME.NS","LODHA.NS","LUPIN.NS","MMTC.NS","MRF.NS","MGL.NS","M&MFIN.NS","M&M.NS",
    "MANAPPURAM.NS","MRPL.NS","MANKIND.NS","MARICO.NS","MARUTI.NS","MFSL.NS","MAXHEALTH.NS",
    "MAZDOCK.NS","MEESHO.NS","MINDACORP.NS","MSUMI.NS","MOTILALOFS.NS","MPHASIS.NS","MCX.NS",
    "MUTHOOTFIN.NS","NATCOPHARM.NS","NBCC.NS","NCC.NS","NHPC.NS","NLCINDIA.NS","NMDC.NS",
    "NSLNISP.NS","NTPCGREEN.NS","NTPC.NS","NH.NS","NATIONALUM.NS","NAVA.NS","NAVINFLUOR.NS",
    "NESTLEIND.NS","NETWEB.NS","NEULANDLAB.NS","NEWGEN.NS","NAM-INDIA.NS","NIVABUPA.NS",
    "NUVAMA.NS","NUVOCO.NS","OBEROIRLTY.NS","ONGC.NS","OIL.NS","OLAELEC.NS","OLECTRA.NS",
    "PAYTM.NS","ONESOURCE.NS","OFSS.NS","POLICYBZR.NS","PCBL.NS","PGEL.NS","PIIND.NS",
    "PNBHOUSING.NS","PTCIL.NS","PVRINOX.NS","PAGEIND.NS","PARADEEP.NS","PATANJALI.NS",
    "PERSISTENT.NS","PETRONET.NS","PFIZER.NS","PHOENIXLTD.NS","PWL.NS","PIDILITIND.NS",
    "PINELABS.NS","PIRAMALFIN.NS","PPLPHARMA.NS","POLYMED.NS","POLYCAB.NS","POONAWALLA.NS",
    "PFC.NS","POWERGRID.NS","PREMIERENE.NS","PRESTIGE.NS","PNB.NS","RRKABEL.NS","RBLBANK.NS",
    "RECLTD.NS","RHIM.NS","RITES.NS","RADICO.NS","RVNL.NS","RAILTEL.NS","RAINBOW.NS",
    "RKFORGE.NS","REDINGTON.NS","RELIANCE.NS","RPOWER.NS","SBFC.NS","SBICARD.NS","SBILIFE.NS",
    "SJVN.NS","SRF.NS","SAGILITY.NS","SAILIFE.NS","SAMMAANCAP.NS","MOTHERSON.NS","SAPPHIRE.NS",
    "SARDAEN.NS","SAREGAMA.NS","SCHAEFFLER.NS","SCHNEIDER.NS","SCI.NS","SHREECEM.NS",
    "SHRIRAMFIN.NS","SHYAMMETL.NS","ENRIN.NS","SIEMENS.NS","SIGNATURE.NS","SOBHA.NS",
    "SOLARINDS.NS","SONACOMS.NS","SONATSOFTW.NS","STARHEALTH.NS","SBIN.NS","SAIL.NS",
    "SUMICHEM.NS","SUNPHARMA.NS","SUNTV.NS","SUNDARMFIN.NS","SUPREMEIND.NS","SPLPETRO.NS",
    "SUZLON.NS","SWANCORP.NS","SWIGGY.NS","SYNGENE.NS","SYRMA.NS","TBOTEK.NS","TVSMOTOR.NS",
    "TATACAP.NS","TATACHEM.NS","TATACOMM.NS","TCS.NS","TATACONSUM.NS","TATAELXSI.NS",
    "TATAINVEST.NS","TMCV.NS","TMPV.NS","TATAPOWER.NS","TATASTEEL.NS","TATATECH.NS",
    "TTML.NS","TECHM.NS","TECHNOE.NS","TEGA.NS","TEJASNET.NS","TENNIND.NS","NIACL.NS",
    "RAMCOCEM.NS","THERMAX.NS","TIMKEN.NS","TITAGARH.NS","TITAN.NS","TORNTPHARM.NS",
    "TORNTPOWER.NS","TARIL.NS","TRAVELFOOD.NS","TRENT.NS","TRIDENT.NS","TRITURBINE.NS",
    "TIINDIA.NS","UCOBANK.NS","UNOMINDA.NS","UPL.NS","UTIAMC.NS","ULTRACEMCO.NS",
    "UNIONBANK.NS","UBL.NS","UNITDSPR.NS","URBANCO.NS","USHAMART.NS","VTL.NS","VBL.NS",
    "VAML.NS","VEDL.NS","VOGL.NS","VIJAYA.NS","VMM.NS","IDEA.NS","VOLTAS.NS","WAAREEENER.NS",
    "WELCORP.NS","WELSPUNLIV.NS","WHIRLPOOL.NS","WIPRO.NS","WOCKPHARMA.NS","YESBANK.NS",
    "ZFCVINDIA.NS","ZEEL.NS","ZENTEC.NS","ZENSARTECH.NS","ZYDUSLIFE.NS","ZYDUSWELL.NS",
    "ECLERX.NS",
]

INDEX_MAP = {
    "S&P 500":       ("sp500",    SP500_TICKERS),
    "Nasdaq-100":    ("nasdaq",   NASDAQ100_TICKERS),
    "Dow Jones 30":  ("djia",     DJIA_TICKERS),
    "Nifty 500 🇮🇳": ("nifty500", NIFTY500_TICKERS),
}

# ── Core screener + strategy filters ─────────────────────

def find_previous_high(series, current_date):
    before = series[series.index < current_date]
    if before.empty:
        return None, None
    rolling = before.rolling(window=min(252, len(before)), min_periods=1).max()
    return rolling.idxmax().strftime("%Y-%m-%d"), round(float(rolling.max()), 2)


@st.cache_data(ttl=600, show_spinner=False)
def run_screener(index_key: str, tickers: tuple):
    end   = datetime.today()
    start = end - timedelta(days=420)

    raw = yf.download(list(tickers), start=start.strftime("%Y-%m-%d"),
                      end=end.strftime("%Y-%m-%d"), auto_adjust=True,
                      progress=False, threads=True)
    if raw.empty:
        return pd.DataFrame(), "N/A"

    is_multi = isinstance(raw.columns, pd.MultiIndex)
    high   = (raw["High"]   if is_multi else raw[["High"]]).dropna(how="all")
    close  = (raw["Close"]  if is_multi else raw[["Close"]]).dropna(how="all")
    volume = (raw["Volume"] if is_multi else raw[["Volume"]]).dropna(how="all")

    last_day       = high.index[-1]
    lookback_start = high.index[high.index >= last_day - timedelta(days=365)][0]

    rows = []
    for ticker in tickers:
        if ticker not in high.columns: continue
        hs = high[ticker].dropna()
        cs = close[ticker].dropna()  if ticker in close.columns  else hs
        vs = volume[ticker].dropna() if ticker in volume.columns else None
        if len(hs) < 50 or len(cs) < 200: continue

        window = hs[hs.index >= lookback_start]
        if window.empty: continue

        today_high = float(window.iloc[-1])
        w52_high   = float(window.max())
        if abs(today_high - w52_high) / w52_high > 0.001: continue

        current_date = window.idxmax()
        prev_date, prev_price = find_previous_high(hs, current_date)
        today_close  = float(cs.iloc[-1])
        pct_above    = round((today_high - prev_price) / prev_price * 100, 2) if prev_price else None
        pct_from_high= round((w52_high - today_close) / w52_high * 100, 2)

        # Filter 1: Consolidation (close within 5% of high)
        consolidated = pct_from_high <= 5.0

        # Filter 2: Volume spike (≥150% of 50-day avg)
        vol_ok, vol_ratio = False, None
        if vs is not None and len(vs) >= 51:
            vol50     = float(vs.iloc[-51:-1].mean())
            today_vol = float(vs.iloc[-1])
            vol_ratio = round(today_vol / vol50 * 100, 1) if vol50 > 0 else None
            vol_ok    = vol_ratio is not None and vol_ratio >= 150

        # Filter 3: MA alignment
        ma_ok = False
        ema20 = sma50 = sma200 = None
        if len(cs) >= 200:
            ema20  = float(cs.ewm(span=20, adjust=False).mean().iloc[-1])
            sma50  = float(cs.rolling(50).mean().iloc[-1])
            sma200 = float(cs.rolling(200).mean().iloc[-1])
            ma_ok  = today_close > ema20 > sma50 > sma200

        # Filter 4: SMA200 trending up
        sma200_up = False
        if len(cs) >= 221 and sma200:
            sma200_20ago = float(cs.rolling(200).mean().iloc[-21])
            sma200_up    = sma200 > sma200_20ago

        score = sum([consolidated, vol_ok, ma_ok, sma200_up])

        rows.append({
            "Ticker":          ticker.replace(".NS", ""),
            "52W High Date":   current_date.strftime("%Y-%m-%d"),
            "52W High":        round(today_high, 2),
            "Close":           round(today_close, 2),
            "% From High":     pct_from_high,
            "Prev High Date":  prev_date or "N/A",
            "Prev High":       prev_price,
            "% Above Prev":    pct_above,
            "Vol Ratio %":     vol_ratio,
            "EMA20":           round(ema20,  2) if ema20  else None,
            "SMA50":           round(sma50,  2) if sma50  else None,
            "SMA200":          round(sma200, 2) if sma200 else None,
            "Consolidated":    consolidated,
            "Vol Spike":       vol_ok,
            "MA Aligned":      ma_ok,
            "SMA200 Up":       sma200_up,
            "Score":           score,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Score","% Above Prev"], ascending=[False,False]).reset_index(drop=True)
    return df, last_day.strftime("%Y-%m-%d")


def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
                      timeout=10)
    except Exception as e:
        st.error(f"Telegram error: {e}")


# ── Sidebar ───────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📈 52W High Screener")
    st.markdown("---")
    index_label  = st.selectbox("Index", list(INDEX_MAP.keys()))
    min_pct      = st.number_input("Min % above prev high", min_value=0.0, value=0.0, step=0.5)
    min_score    = st.slider("Min strategy score (0–4)", 0, 4, 0)
    only_quality = st.toggle("High-quality only (score ≥ 3)", value=False)
    st.markdown("---")
    run_btn   = st.button("🚀 Run Screener", use_container_width=True)
    alert_btn = st.button("📲 Send Telegram Alert", use_container_width=True)
    st.markdown("---")
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")


# ── Main ──────────────────────────────────────────────────

st.title("📈 52-Week High Screener")
st.caption("Live intraday highs · Strategy filters: Consolidation · Volume · MA Alignment · SMA200 Trend")

index_key, tickers = INDEX_MAP[index_label]

if run_btn or "df" not in st.session_state or st.session_state.get("last_index") != index_key:
    with st.spinner(f"Fetching {index_label} · Running strategy filters…"):
        df, last_day = run_screener(index_key, tuple(tickers))
        st.session_state.df, st.session_state.last_day, st.session_state.last_index = df, last_day, index_key

df       = st.session_state.get("df", pd.DataFrame())
last_day = st.session_state.get("last_day", "—")

df_f = df.copy()
if not df_f.empty:
    df_f = df_f[df_f["% Above Prev"] >= min_pct]
    df_f = df_f[df_f["Score"] >= (3 if only_quality else min_score)]

# KPIs
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("Scanned", len(tickers))
with c2: st.metric("52W Highs", len(df) if not df.empty else 0)
with c3: st.metric("Quality Setups ≥3", int((df["Score"] >= 3).sum()) if not df.empty else 0)
with c4: st.metric("Showing", len(df_f))
with c5: st.metric("Last Trading Day", last_day)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Results Table", "🎯 Strategy Signals", "📈 Charts"])

with tab1:
    search = st.text_input("🔍 Filter by ticker", placeholder="e.g. AAPL")
    if search:
        df_f = df_f[df_f["Ticker"].str.contains(search.upper())]

    if df_f.empty:
        st.info("No stocks match your filters. Try lowering the score filter.")
    else:
        disp = df_f.copy()
        disp["% Above Prev"] = disp["% Above Prev"].apply(lambda x: f"+{x:.2f}%" if pd.notna(x) else "N/A")
        disp["% From High"]  = disp["% From High"].apply(lambda x: f"{x:.2f}%"  if pd.notna(x) else "N/A")
        disp["Vol Ratio %"]  = disp["Vol Ratio %"].apply(lambda x: f"{x:.0f}%"  if pd.notna(x) else "N/A")
        disp["Consolidated"] = disp["Consolidated"].map({True: "✅", False: "❌"})
        disp["Vol Spike"]    = disp["Vol Spike"].map({True: "✅", False: "❌"})
        disp["MA Aligned"]   = disp["MA Aligned"].map({True: "✅", False: "❌"})
        disp["SMA200 Up"]    = disp["SMA200 Up"].map({True: "✅", False: "❌"})

        st.dataframe(disp[[
            "Ticker","Score","52W High Date","52W High","Close","% From High",
            "Prev High Date","Prev High","% Above Prev",
            "Vol Ratio %","Consolidated","Vol Spike","MA Aligned","SMA200 Up"
        ]], use_container_width=True, height=450)

        csv = df_f.to_csv(index=False)
        st.download_button("⬇️ Export to Excel (CSV)", data=csv,
                           file_name=f"52w_{index_key}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                           mime="text/csv", use_container_width=True)

with tab2:
    st.markdown("### 🎯 Strategy Signal Cards")
    st.caption("Green border = score 3–4 (high quality) · Yellow = 2 · Red = 0–1")

    if df_f.empty:
        st.info("Run the screener first.")
    else:
        for _, r in df_f.head(20).iterrows():
            score = int(r["Score"])
            cls   = "signal-card" if score >= 3 else ("signal-card warn" if score == 2 else "signal-card bad")
            dots  = "🟢" * score + "⚫" * (4 - score)

            def b(cond, label):
                c = "b-green" if cond else "b-red"
                i = "✅" if cond else "❌"
                return f'<span class="badge {c}">{i} {label}</span>'

            vr = f"{r['Vol Ratio %']:.0f}%" if pd.notna(r['Vol Ratio %']) else "N/A"
            st.markdown(f"""
            <div class="{cls}">
                <b style="font-size:16px">{r['Ticker']}</b>
                <span style="color:#64748b;margin-left:8px">{dots} ({score}/4)</span><br/>
                <span style="color:#94a3b8;font-size:13px">
                    High: <b>${r['52W High']:.2f}</b> &nbsp;|&nbsp;
                    Close: <b>${r['Close']:.2f}</b> &nbsp;|&nbsp;
                    {r['% From High']:.2f}% from high &nbsp;|&nbsp;
                    Vol: {vr}
                </span><br/><br/>
                {b(r['Consolidated'], 'Consolidated ≤5%')}
                {b(r['Vol Spike'],    'Vol Spike ≥150%')}
                {b(r['MA Aligned'],   'MA Aligned')}
                {b(r['SMA200 Up'],    'SMA200 Trending Up')}
            </div>""", unsafe_allow_html=True)

with tab3:
    if not df_f.empty:
        import plotly.express as px
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Score Distribution**")
            sd = df_f["Score"].value_counts().sort_index().reset_index()
            sd.columns = ["Score","Count"]
            fig1 = px.bar(sd, x="Score", y="Count",
                          color="Score", color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],
                          range_color=[0,4])
            fig1.update_layout(paper_bgcolor="#1c2333", plot_bgcolor="#1c2333",
                               font_color="#94a3b8", showlegend=False, height=250,
                               margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("**Top 10 — Score vs % Above Prev High**")
            top10 = df_f.head(10)
            fig2  = px.bar(top10, x="% Above Prev", y="Ticker", orientation="h",
                           color="Score", color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],
                           range_color=[0,4])
            fig2.update_layout(paper_bgcolor="#1c2333", plot_bgcolor="#1c2333",
                               font_color="#94a3b8", showlegend=False, height=250,
                               margin=dict(l=10,r=10,t=10,b=10),
                               yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**Scatter — % From High vs % Above Prev (closer to 0 = tighter base)**")
        fig3 = px.scatter(df_f, x="% From High", y="% Above Prev", color="Score",
                          hover_data=["Ticker","Vol Ratio %"],
                          color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],
                          range_color=[0,4])
        fig3.add_vline(x=5, line_dash="dash", line_color="#f59e0b",
                       annotation_text="5% threshold", annotation_font_color="#f59e0b")
        fig3.update_layout(paper_bgcolor="#1c2333", plot_bgcolor="#1c2333",
                           font_color="#94a3b8", height=300,
                           margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Run the screener first.")

# Telegram alert
if alert_btn and not df_f.empty:
    quality = df_f[df_f["Score"] >= 3]
    lines   = [f"📈 <b>52W High Alert — {index_label}</b>",
               f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
               f"Total: {len(df_f)} | Quality ≥3: {len(quality)}\n"]
    for _, r in quality.head(10).iterrows():
        pct = f"+{r['% Above Prev']:.2f}%" if pd.notna(r['% Above Prev']) else "N/A"
        lines.append(
            f"<b>{r['Ticker']}</b> — {r['Score']}/4\n"
            f"  High: ${r['52W High']:.2f} | {pct} above prev\n"
            f"  {'✅' if r['Consolidated'] else '❌'} Consolidated "
            f"{'✅' if r['Vol Spike'] else '❌'} Vol "
            f"{'✅' if r['MA Aligned'] else '❌'} MA "
            f"{'✅' if r['SMA200 Up'] else '❌'} SMA200"
        )
    send_telegram("\n".join(lines))
    st.success("✅ Telegram alert sent!")
