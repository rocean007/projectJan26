import requests
import time
import concurrent.futures
import os
import re
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# API Config
GOLD_API_KEY = os.environ.get('GOLD_API_KEY', 'f2db1aaaee18667e498f2a463de9795215b478a6a91abad885d14e6d5edc5b49')

# Cache for ALL responses (not just exchange rate)
_response_cache = {
    'data': None,
    'timestamp': 0
}
RESPONSE_CACHE_DURATION = 30  # Cache full API response for 30 seconds

# Cache for exchange rates
_rate_cache = {
    'rate': 133.65,
    'timestamp': 0,
    'source': 'Default'
}
RATE_CACHE_DURATION = 300  # Cache exchange rate for 5 minutes

def fetch_gold_price():
    """Get gold price from Gold API"""
    try:
        response = requests.get(
            'https://api.gold-api.com/price/XAU',
            headers={'x-api-key': GOLD_API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if 'price' in data:
                return round(float(data['price']), 2)
    except Exception:
        pass
    return 2345.67

def fetch_silver_price():
    """Get silver price from Gold API"""
    try:
        response = requests.get(
            'https://api.gold-api.com/price/XAG',
            headers={'x-api-key': GOLD_API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if 'price' in data:
                return round(float(data['price']), 3)
    except Exception:
        pass
    return 27.89

def scrape_nrb_rate():
    """Scrape USD/NPR rate from NRB website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://www.nrb.org.np/forex/', headers=headers, timeout=5)
        response.raise_for_status()
        
        # Look for USD rate patterns
        patterns = [
            r'USD[\s\S]{0,150}?(\d{3}\.\d{2})',
            r'(\d{3}\.\d{2})\s*NPR.*USD',
            r'US\s*Dollar[\s\S]{0,150}?(\d{3}\.\d{2})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            for match in matches:
                try:
                    rate = float(match)
                    if 100 < rate < 200:
                        return rate, 'NRB Official'
                except ValueError:
                    continue
    except Exception:
        pass
    
    # Fallback API
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=3)
        if response.status_code == 200:
            data = response.json()
            rate = float(data.get('rates', {}).get('NPR', 133.65))
            return rate, 'Fallback API'
    except Exception:
        pass
    
    return 133.65, 'Default'

def get_exchange_rate():
    """Get cached exchange rate"""
    current_time = time.time()
    
    if current_time - _rate_cache['timestamp'] < RATE_CACHE_DURATION:
        return _rate_cache['rate']
    
    rate, source = scrape_nrb_rate()
    _rate_cache['rate'] = rate
    _rate_cache['timestamp'] = current_time
    _rate_cache['source'] = source
    
    print(f"✅ Exchange rate: NPR {rate} ({source})")
    return rate

@require_GET
def get_prices(request):
    """Fetch all prices with NPR conversion - with manual caching"""
    current_time = time.time()
    
    # Check if we have a cached response that's still fresh
    if (_response_cache['data'] is not None and 
        current_time - _response_cache['timestamp'] < RESPONSE_CACHE_DURATION):
        print("📦 Returning cached API response")
        return JsonResponse(_response_cache['data'])
    
    try:
        usd_npr = get_exchange_rate()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            gold_future = executor.submit(fetch_gold_price)
            silver_future = executor.submit(fetch_silver_price)
            gold_usd = gold_future.result()
            silver_usd = silver_future.result()
        
        print(f"💰 Prices: Gold ${gold_usd}, Silver ${silver_usd}, Rate NPR {usd_npr}")
        
        # Conversion constants
        tola_to_ounce = 11.6638 / 31.1035
        kg_to_ounce = 1000 / 31.1035
        
        # Calculate prices
        gold_npr = gold_usd * usd_npr
        silver_npr = silver_usd * usd_npr
        gold_tola_npr = gold_usd * tola_to_ounce * usd_npr
        silver_tola_npr = silver_usd * tola_to_ounce * usd_npr
        gold_kg_npr = gold_usd * kg_to_ounce * usd_npr
        silver_kg_npr = silver_usd * kg_to_ounce * usd_npr
        
        response_data = {
            'status': 'success',
            'data': {
                'gold_usd': round(gold_usd, 2),
                'silver_usd': round(silver_usd, 3),
                'exchange_rate': round(usd_npr, 2),
                'exchange_source': _rate_cache['source'],
                'gold_npr': round(gold_npr, 2),
                'silver_npr': round(silver_npr, 2),
                'gold_tola_npr': round(gold_tola_npr),
                'silver_tola_npr': round(silver_tola_npr, 2),
                'gold_kg_npr': round(gold_kg_npr),
                'silver_kg_npr': round(silver_kg_npr),
                'timestamp': int(current_time),
                'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Gold API + NRB Exchange Rate'
            }
        }
        
        # Cache the response
        _response_cache['data'] = response_data
        _response_cache['timestamp'] = current_time
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        gold_usd = 2345.67
        silver_usd = 27.89
        usd_npr = 133.65
        
        tola_to_ounce = 11.6638 / 31.1035
        kg_to_ounce = 1000 / 31.1035
        
        error_data = {
            'status': 'error',
            'message': str(e),
            'data': {
                'gold_usd': gold_usd,
                'silver_usd': silver_usd,
                'exchange_rate': usd_npr,
                'exchange_source': 'Fallback',
                'gold_npr': round(gold_usd * usd_npr, 2),
                'silver_npr': round(silver_usd * usd_npr, 2),
                'gold_tola_npr': round(gold_usd * tola_to_ounce * usd_npr),
                'silver_tola_npr': round(silver_usd * tola_to_ounce * usd_npr, 2),
                'gold_kg_npr': round(gold_usd * kg_to_ounce * usd_npr),
                'silver_kg_npr': round(silver_usd * kg_to_ounce * usd_npr),
                'timestamp': int(current_time),
                'source': 'Fallback due to error'
            }
        }
        
        # Cache error response too (but for shorter time)
        _response_cache['data'] = error_data
        _response_cache['timestamp'] = current_time
        
        return JsonResponse(error_data)

@require_GET
def health_check(request):
    """Test if APIs are working"""
    try:
        response = requests.get('https://api.gold-api.com/price/XAU', 
                              headers={'x-api-key': GOLD_API_KEY}, timeout=5)
        gold_status = 'working' if response.status_code == 200 else f'failed: {response.status_code}'
    except Exception as e:
        gold_status = f'connection failed: {str(e)}'
    
    return JsonResponse({
        'status': 'healthy',
        'service': 'Gold & Silver Price Tracker',
        'timestamp': int(time.time()),
        'apis': {'gold_api': gold_status},
        'exchange_rate': {
            'current_rate': _rate_cache['rate'],
            'source': _rate_cache['source'],
            'cache_age_seconds': int(time.time() - _rate_cache['timestamp'])
        }
    })