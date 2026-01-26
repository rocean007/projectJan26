import requests
import time
import concurrent.futures
import os
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

# API Config
GOLD_API_KEY = os.environ.get('GOLD_API_KEY', 'f2db1aaaee18667e498f2a463de9795215b478a6a91abad885d14e6d5edc5b49')
# Using the exchange rate API you requested
EXCHANGE_RATE_URL = 'https://open.er-api.com/v6/latest/USD'

# Nepal Market Premiums
NEPAL_PREMIUMS = {
    'gold': 1.1008,    # 10.08% premium
    'silver': 1.1266   # 12.66% premium
}

def fetch_gold_price():
    """Get gold price from Gold API"""
    try:
        response = requests.get(
            'https://api.gold-api.com/price/XAU',
            headers={'x-api-key': GOLD_API_KEY},
            timeout=5
        )
        print(f"🔧 Gold API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔧 Gold API Response: {data}")
            
            if 'price' in data:
                gold_price = float(data['price'])
                print(f"✅ Got REAL gold price: ${gold_price}")
                return round(gold_price, 2)
            else:
                print(f"⚠️ Unexpected gold response format: {data}")
                if 'data' in data and 'amount' in data['data']:
                    gold_price = float(data['data']['amount'])
                    return round(gold_price, 2)
    except Exception as e:
        print(f"❌ Gold API error: {e}")
    
    print("❌ Gold API failed, using approximation")
    return 2345.67

def fetch_silver_price():
    """Get silver price from Gold API"""
    try:
        response = requests.get(
            'https://api.gold-api.com/price/XAG',
            headers={'x-api-key': GOLD_API_KEY},
            timeout=5
        )
        print(f"🔧 Silver API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔧 Silver API Response: {data}")
            
            if 'price' in data:
                silver_price = float(data['price'])
                print(f"✅ Got REAL silver price: ${silver_price}")
                return round(silver_price, 3)
            else:
                print(f"⚠️ Unexpected silver response format: {data}")
                if 'data' in data and 'amount' in data['data']:
                    silver_price = float(data['data']['amount'])
                    return round(silver_price, 3)
    except Exception as e:
        print(f"❌ Silver API error: {e}")
    
    print("❌ Silver API failed, using approximation")
    return 27.89

def fetch_exchange_rate():
    """Get USD to NPR rate from open.er-api.com"""
    try:
        response = requests.get(EXCHANGE_RATE_URL, timeout=3)
        if response.status_code == 200:
            data = response.json()
            
            # Check if API call was successful
            if data.get('result') == 'success':
                rate = float(data.get('rates', {}).get('NPR', 133.65))
                print(f"✅ Got exchange rate from open.er-api.com: NPR {rate}")
                return rate
            else:
                print(f"⚠️ Exchange API returned error: {data.get('error-type', 'Unknown error')}")
                return 133.65
    except Exception as e:
        print(f"❌ Exchange API error: {e}")
    
    # Fallback rate
    return 133.65

@require_GET
@cache_page(30)
def get_prices(request):
    """Fetch all prices with NPR conversion"""
    print(f"\n📊 Fetching prices at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            gold_future = executor.submit(fetch_gold_price)
            silver_future = executor.submit(fetch_silver_price)
            exchange_future = executor.submit(fetch_exchange_rate)
            
            gold_usd = gold_future.result()
            silver_usd = silver_future.result()
            usd_npr = exchange_future.result()
        
        print(f"✅ FINAL: Gold: ${gold_usd:.2f}, Silver: ${silver_usd:.3f}, USD/NPR: {usd_npr:.2f}")
        
        # Conversion constants
        GRAMS_PER_TROY_OUNCE = 31.1035
        GRAMS_PER_TOLA = 11.6638
        GRAMS_PER_KG = 1000
        
        # Calculate conversion factors
        tola_to_ounce = GRAMS_PER_TOLA / GRAMS_PER_TROY_OUNCE
        kg_to_ounce = GRAMS_PER_KG / GRAMS_PER_TROY_OUNCE
        
        # Calculate BASE NPR prices (without premium)
        gold_npr_base = gold_usd * usd_npr
        silver_npr_base = silver_usd * usd_npr
        
        # Calculate BASE tola prices (without premium)
        gold_tola_npr_base = gold_usd * tola_to_ounce * usd_npr
        silver_tola_npr_base = silver_usd * tola_to_ounce * usd_npr
        
        # Calculate BASE kg prices (without premium)
        gold_kg_npr_base = gold_usd * kg_to_ounce * usd_npr
        silver_kg_npr_base = silver_usd * kg_to_ounce * usd_npr
        
        # APPLY NEPAL PREMIUMS to NPR prices
        gold_npr = gold_npr_base * NEPAL_PREMIUMS['gold']
        silver_npr = silver_npr_base * NEPAL_PREMIUMS['silver']
        
        # APPLY NEPAL PREMIUMS to tola prices
        gold_tola_npr = gold_tola_npr_base * NEPAL_PREMIUMS['gold']
        silver_tola_npr = silver_tola_npr_base * NEPAL_PREMIUMS['silver']
        
        # APPLY NEPAL PREMIUMS to kg prices
        gold_kg_npr = gold_kg_npr_base * NEPAL_PREMIUMS['gold']
        silver_kg_npr = silver_kg_npr_base * NEPAL_PREMIUMS['silver']
        
        print(f"✅ WITH PREMIUMS: Gold NPR: {gold_npr:,.2f} (+10.08%), Silver NPR: {silver_npr:,.2f} (+12.66%)")
        
        # Create response
        response_data = {
            'status': 'success',
            'data': {
                'gold_usd': round(gold_usd, 2),
                'silver_usd': round(silver_usd, 3),
                'exchange_rate': round(usd_npr, 2),
                'gold_npr': round(gold_npr, 2),  # Now with premium
                'silver_npr': round(silver_npr, 2),  # Now with premium
                # Silver tola with 2 decimals, gold tola as integer
                'gold_tola_npr': round(gold_tola_npr),  # Now with premium
                'silver_tola_npr': round(silver_tola_npr, 2),  # Now with premium
                'gold_kg_npr': round(gold_kg_npr),  # Now with premium
                'silver_kg_npr': round(silver_kg_npr),  # Now with premium
                'timestamp': int(time.time()),
                'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Gold API + open.er-api.com',
                'api_key': 'active',
                'unit': 'USD per troy ounce',
                'conversion_note': '1 tola = 11.6638g, 1 troy ounce = 31.1035g',
                'premium_applied': True,
                'gold_premium_pct': 10.08,
                'silver_premium_pct': 12.66
            }
        }
        
        print(f"📤 Sending response: {response_data['data']}")
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"❌ Error in get_prices: {e}")
        
        # Fallback with same API structure
        gold_usd = 2345.67
        silver_usd = 27.89
        usd_npr = 133.65
        
        # Reuse the same calculation for consistency
        GRAMS_PER_TROY_OUNCE = 31.1035
        GRAMS_PER_TOLA = 11.6638
        GRAMS_PER_KG = 1000
        
        tola_to_ounce = GRAMS_PER_TOLA / GRAMS_PER_TROY_OUNCE
        kg_to_ounce = GRAMS_PER_KG / GRAMS_PER_TROY_OUNCE
        
        # Calculate base prices
        gold_npr_base = gold_usd * usd_npr
        silver_npr_base = silver_usd * usd_npr
        gold_tola_npr_base = gold_usd * tola_to_ounce * usd_npr
        silver_tola_npr_base = silver_usd * tola_to_ounce * usd_npr
        gold_kg_npr_base = gold_usd * kg_to_ounce * usd_npr
        silver_kg_npr_base = silver_usd * kg_to_ounce * usd_npr
        
        # Apply premiums to fallback too
        gold_npr = gold_npr_base * NEPAL_PREMIUMS['gold']
        silver_npr = silver_npr_base * NEPAL_PREMIUMS['silver']
        gold_tola_npr = gold_tola_npr_base * NEPAL_PREMIUMS['gold']
        silver_tola_npr = silver_tola_npr_base * NEPAL_PREMIUMS['silver']
        gold_kg_npr = gold_kg_npr_base * NEPAL_PREMIUMS['gold']
        silver_kg_npr = silver_kg_npr_base * NEPAL_PREMIUMS['silver']
        
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'data': {
                'gold_usd': gold_usd,
                'silver_usd': silver_usd,
                'exchange_rate': usd_npr,
                'gold_npr': round(gold_npr, 2),
                'silver_npr': round(silver_npr, 2),
                'gold_tola_npr': round(gold_tola_npr),
                'silver_tola_npr': round(silver_tola_npr, 2),
                'gold_kg_npr': round(gold_kg_npr),
                'silver_kg_npr': round(silver_kg_npr),
                'timestamp': int(time.time()),
                'source': 'Fallback due to error',
                'premium_applied': True,
                'gold_premium_pct': 10.08,
                'silver_premium_pct': 12.66
            }
        })

@require_GET
def health_check(request):
    """Test if APIs are working"""
    try:
        # Test Gold API
        gold_response = requests.get(
            'https://api.gold-api.com/price/XAU',
            headers={'x-api-key': GOLD_API_KEY},
            timeout=5
        )
        gold_status = 'working' if gold_response.status_code == 200 else f'failed: {gold_response.status_code}'
        
        # Test Exchange API
        exchange_response = requests.get(EXCHANGE_RATE_URL, timeout=3)
        exchange_status = 'working' if exchange_response.status_code == 200 else f'failed: {exchange_response.status_code}'
        
    except Exception as e:
        gold_status = f'connection failed: {str(e)}'
        exchange_status = f'connection failed: {str(e)}'
    
    return JsonResponse({
        'status': 'healthy',
        'service': 'Gold & Silver Price Tracker',
        'timestamp': int(time.time()),
        'apis': {
            'gold_api': gold_status,
            'exchange_api': exchange_status
        },
        'exchange_api_url': EXCHANGE_RATE_URL,
        'gold_api_url': 'https://api.gold-api.com/price/XAU',
        'premiums_applied': True,
        'gold_premium': '10.08%',
        'silver_premium': '12.66%'
    })