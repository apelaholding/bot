import asyncio
from playwright.async_api import async_playwright
from supabase import create_client

SUPABASE_URL = "https://lsvajvuxskbtgimtadpt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzdmFqdnV4c2tidGdpbXRhZHB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODYyNDI1NSwiZXhwIjoyMDU0MjAwMjU1fQ.OwVZbvvfstpIF0f_RJGTp40Mtoj5WK_Wpyu2bFXGbQc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

UPSELL_PAGES = [
    "https://safe-space.live/up/g-upsell/upsell-1/",
    "https://safe-space.live/up/g-upsell/upsell-2/",
    "https://safe-space.live/up/g-upsell/upsell-3/",
    "https://safe-space.live/up/g-upsell/upsell-4/",
    "https://safe-space.live/up/g-upsell/upsell-6/",
    "https://safe-space.live/up/g-upsell/upsell-7/"
]

async def obter_fsid_pendente():
    response = supabase.table("hotmart").select("*").eq("status", "pendente").limit(1).execute()
    if response.data:
        return response.data[0]["fsid"], response.data[0]["paginas"]
    return None, None

async def atualizar_status_fsid(fsid, status, paginas_atualizadas, obs):
    supabase.table("hotmart").update({
        "status": status,
        "paginas": f"{paginas_atualizadas}/6",
        "obs": obs
    }).eq("fsid", fsid).execute()

async def abrir_pagina_com_fsid(fsid, paginas_concluidas):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.77 Mobile Safari/537.36",
            device_scale_factor=2,
            is_mobile=True
        )

        page = await context.new_page()
        obs_list = []

        for index in range(paginas_concluidas, len(UPSELL_PAGES)):
            url = f"{UPSELL_PAGES[index]}?fsid={fsid}"
            print(f"[BOT] Iniciando no URL: {url}")
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(3000)

            url_atual = page.url

            while True:
                try:
                    iframe_element = await page.wait_for_selector("iframe.custom-element__iframe", timeout=15000)
                    iframe = await iframe_element.content_frame()

                    if iframe:
                        print(f"[BOT] Iframe encontrado na página {index + 1}. Buscando botão de compra...")

                        botao = await iframe.wait_for_selector('button[data-testid="funnel-buy-button"]', timeout=5000)
                        if botao:
                            await botao.click()
                            print(f"[BOT] Botão de compra clicado na página {index + 1}!")

                            await page.wait_for_timeout(5000)

                            for _ in range(5):
                                await page.wait_for_timeout(1000)
                                if page.url != url_atual:
                                    print("[BOT] Página redirecionada com sucesso!")
                                    paginas_concluidas += 1
                                    await atualizar_status_fsid(fsid, "processando", paginas_concluidas, ", ".join(obs_list))
                                    break
                            else:
                                print("[BOT] Página não redirecionou, verificando mensagens de erro dentro do iframe...")
                                await page.wait_for_timeout(2000)

                                erro_element = await iframe.query_selector("p._text-gray-600._text-2._mb-3")
                                if erro_element:
                                    texto_erro = await erro_element.text_content()
                                    if "saldo do cartão está insuficiente" in texto_erro.lower():
                                        print(f"[BOT] ❌ Erro na página {index + 1}: Saldo insuficiente!")
                                        await atualizar_status_fsid(fsid, "erro", paginas_concluidas, obs="Saldo insuficiente")
                                        return
                                    if "Plano de assinatura já foi comprado anteriormente" in texto_erro:
                                        print(f"[BOT] ❌ Erro na página {index + 1}: Plano já comprado!")
                                        await atualizar_status_fsid(fsid, "erro", paginas_concluidas, obs="Plano já comprado")
                                        return

                                print("[BOT] Nenhuma mensagem de erro detectada, tentando novamente...")
                                await page.wait_for_timeout(2000)
                        else:
                            print("[BOT] ❌ Botão de compra não encontrado!")
                            await page.wait_for_timeout(2000)

                except Exception as e:
                    print(f"[BOT] ❌ Erro ao processar a página {index + 1}: {e}")
                    await page.wait_for_timeout(2000)

            print(f"[BOT] Finalizando processamento da página {index + 1}")
            await atualizar_status_fsid(fsid, "processando", paginas_concluidas, ", ".join(obs_list))

        await browser.close()

async def processar_automatizacao():
    while True:
        fsid, paginas = await obter_fsid_pendente()
        if fsid:
            paginas_concluidas = int(paginas.split("/")[0]) if paginas else 0

            if paginas_concluidas < 6:
                print(f"[BOT] Processando FSID: {fsid} - Progresso atual: {paginas_concluidas}/6")
                await abrir_pagina_com_fsid(fsid, paginas_concluidas)
            else:
                print(f"[BOT] FSID {fsid} já foi processado. Pulando...")

        else:
            print("[BOT] Nenhum FSID pendente encontrado. Aguardando...")

        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(processar_automatizacao())
