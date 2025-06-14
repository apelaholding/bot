import os
import requests
from telethon.sync import TelegramClient

api_id = 29827849
api_hash = '77c41295b2bc1cc6cb5780b230f6f24c'
arquivo_proxys = "proxys.txt"

def carregar_proxys():
    if not os.path.exists(arquivo_proxys):
        open(arquivo_proxys, 'w').close()
    with open(arquivo_proxys, 'r', encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip()]

def escolher_tipo_proxy():
    print("\n🌐 Tipo de proxy:")
    print("1. SOCKS5")
    print("2. SOCKS4")
    print("3. HTTP")
    escolha = input("Escolha o tipo (1-3): ").strip()
    if escolha == "1":
        return "socks5"
    elif escolha == "2":
        return "socks4"
    elif escolha == "3":
        return "http"
    else:
        print("❌ Tipo inválido. Usando SOCKS5.")
        return "socks5"

def escolher_ou_adicionar_proxy(proxys):
    print("\n📡 Proxys disponíveis:")
    print("0. ➕ Adicionar novo proxy")
    for i, proxy in enumerate(proxys):
        print(f"{i + 1}. {proxy}")

    escolha = input("\nEscolha o número do proxy: ").strip()

    if escolha == "0":
        novo = input("Digite o novo proxy (host:porta:user:senha): ").strip()
        if novo and len(novo.split(":")) == 4:
            with open(arquivo_proxys, 'a', encoding='utf-8') as f:
                f.write(novo + "\n")
            return novo
        else:
            print("❌ Formato inválido.")
            return None
    elif escolha.isdigit() and 1 <= int(escolha) <= len(proxys):
        return proxys[int(escolha) - 1]
    else:
        print("❌ Escolha inválida.")
        return None

def testar_proxy(proxy_str, tipo_proxy):
    host, porta, usuario, senha = proxy_str.split(":")
    proxy_telegram = (tipo_proxy, host, int(porta), True, usuario, senha)

    print("\n🔌 Testando conexão com Telegram...")
    try:
        client = TelegramClient("teste_proxy", api_id, api_hash, proxy=proxy_telegram)
        client.connect()
        if client.is_user_authorized():
            print("✅ Proxy funcionando no Telegram (logado).")
        else:
            print("✅ Proxy funcionando no Telegram (sem login).")
        client.disconnect()
    except Exception as e:
        print(f"❌ Proxy falhou no Telegram: {e}")

    print("\n🌐 Testando conexão HTTP com o proxy...")
    proxies_http = {
        "http": f"{tipo_proxy}://{usuario}:{senha}@{host}:{porta}",
        "https": f"{tipo_proxy}://{usuario}:{senha}@{host}:{porta}"
    }
    try:
        r = requests.get("https://httpbin.org/ip", proxies=proxies_http, timeout=10)
        if r.status_code == 200:
            print(f"✅ Proxy HTTP funcionando. IP detectado: {r.json().get('origin')}")
        else:
            print(f"⚠️ Proxy HTTP respondeu com código {r.status_code}")
    except Exception as e:
        print(f"❌ Proxy falhou no teste HTTP")

proxys = carregar_proxys()
proxy_escolhido = escolher_ou_adicionar_proxy(proxys)
if proxy_escolhido:
    tipo = escolher_tipo_proxy()
    testar_proxy(proxy_escolhido, tipo)
