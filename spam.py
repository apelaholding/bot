import asyncio
import csv
import os
from telethon import TelegramClient
from telethon.tl.types import InputPeerUser

api_id = 21867835
api_hash = '12350ab8e581ebbb660900679f8ae0ae'

def buscar_sessoes(diretorio_raiz):
    sessoes = []
    for raiz, dirs, arquivos in os.walk(diretorio_raiz):
        for arquivo in arquivos:
            if arquivo.endswith(".session"):
                caminho_completo = os.path.join(raiz, arquivo)
                sessoes.append(caminho_completo.replace(".session", ""))
    return sessoes

sessoes = buscar_sessoes(".")

if not sessoes:
    print("❌ Nenhuma conta .session encontrada em nenhuma pasta.")
    exit()

print("\n📱 Contas disponíveis:")
for i, sessao in enumerate(sessoes):
    print(f"{i + 1}. {sessao}")

idx_sessao = int(input("\nEscolha o número da conta: ").strip()) - 1

if idx_sessao < 0 or idx_sessao >= len(sessoes):
    print("❌ Escolha inválida.")
    exit()

session = sessoes[idx_sessao]

mensagem = input("\nDigite a mensagem que será enviada: ").strip()

csvs = [f for f in os.listdir('.') if f.endswith(".csv")]

if not csvs:
    print("❌ Nenhum arquivo CSV encontrado na pasta atual.")
    exit()

print("\n📄 Arquivos CSV disponíveis:")
for i, nome in enumerate(csvs):
    print(f"{i + 1}. {nome}")

indice = int(input("\nEscolha o número do CSV: ").strip()) - 1

if indice < 0 or indice >= len(csvs):
    print("❌ Escolha inválida.")
    exit()

arquivo_csv = csvs[indice]

async def enviar_mensagens():
    client = TelegramClient(session, api_id, api_hash)
    await client.start()

    with open(arquivo_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for linha in reader:
            try:
                user_id = int(linha[3])
                access_hash = int(linha[4])
                destino = InputPeerUser(user_id, access_hash)
                await client.send_message(destino, mensagem)
                print(f"✅ Enviado para: {linha[1]}")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ Erro ao enviar para {linha[1]}: {e}")
                await asyncio.sleep(2)

    await client.disconnect()

asyncio.run(enviar_mensagens())
