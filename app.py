import os
import string
import sys

from flask import Flask, request, send_from_directory, abort, redirect
from flask_caching import Cache
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'secret-pw'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'huma'
app.config['MYSQL_CONNECTION_OPTIONS'] = {
    'allow_multi_statements': True
}
mysql = MySQL(app)

app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = '127.0.0.1'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
# app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Default cache timeout in seconds
cache = Cache(app)

# redis_client = Redis(host='localhost', port=6379, db=0)
redis_cache_ttl = 3600

app.run(host='0.0.0.0', port=8080, debug=True)


@app.get('/')
def hello_world():  # put application's code here
    return 'Post URL to https://humaurl.io/ to create a new entry or just get https://humaurl.io/{short-code} to redirect to the original one'


in_use_characters_dict = string.digits + string.ascii_lowercase + string.ascii_uppercase
reverse_code_dict = {in_use_characters_dict[i]: i for i in range(len(in_use_characters_dict))}


def number_to_base(n: int):
    base = len(in_use_characters_dict)
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % base))
        n //= base
    return digits[::-1]


def base_to_number(code: str) -> int:
    base = len(in_use_characters_dict)
    result = 0
    for char in code[::]:
        char_value = reverse_code_dict[char]
        result = (result * base) + char_value
    return result


def convert_id_to_short_url(id: int) -> str:
    return "".join(in_use_characters_dict[n] for n in number_to_base(id))


def log_error(message: str, **args):
    print(f"E: message", **args, file=sys.stderr)


@app.get('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.post("/")
def create_url():
    url = request.get_data(as_text=True).strip()
    if not url:
        abort(403)
    # Try to save the New URL
    with mysql.connection.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO url (url) VALUES (%s)", (url,))
            row_id = cursor.lastrowid
            code = convert_id_to_short_url(row_id)
            cursor.execute("UPDATE url SET url = %s WHERE id = %s", (code, row_id))
            cache.set(f"id:{code}", url, redis_cache_ttl)
            return code, 200
        except Exception as e:
            log_error(f"Can not save {code}->{url}. error: {e}")
            return f"Error happened: {e}", 500


def get_code_from_db(code: str):
    with mysql.connection.cursor() as cursor:
        cnt = cursor.execute('SELECT code FROM url WHERE code = %s LIMIT 1', (code,))
        if cnt < 1:
            return None
        return cursor.fetchone()[0]


@app.get("/<code>")
@cache.cached(timeout=10, key_prefix="get", query_string=True)
def redirect_to_url(code: str):
    # Try get it from the cache
    url = cache.get(code)
    if url:
        return redirect(str(url), 302)
    # Try to get it from DB
    url = get_code_from_db(code)
    if not url:
        abort(404)
    # Cache the result
    cache.set(f"id:{code}", url, redis_cache_ttl)
    return redirect(url, 301)


if __name__ == "__main__":
    app.run()
