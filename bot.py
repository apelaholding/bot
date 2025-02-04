import asyncio
from playwright.async_api import async_playwright
from supabase import create_client

# TOKENS
SUPABASE_URL = "https://lsvajvuxskbtgimtadpt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzdmFqdnV4c2tidGdpbXRhZHB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODYyNDI1NSwiZXhwIjoyMDU0MjAwMjU1fQ.OwVZbvvfstpIF0f_RJGTp40Mtoj5WK_Wpyu2bFXGbQc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# PAGINAS
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

async def atualizar_status_fsid(fsid, status, paginas_atualizadas):
    supabase.table("hotmart").update({
        "status": status,
        "paginas": f"{paginas_atualizadas}/6"
    }).eq("fsid", fsid).execute()

async def abrir_pagina_com_fsid(fsid, paginas_concluidas):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.77 Mobile Safari/537.36",
            device_scale_factor=2,
            is_mobile=True
        )

        page = await context.new_page()
        

        
        for index, base_url in enumerate(UPSELL_PAGES):
            if paginas_concluidas > index:
                print(f"[BOT] Página {index + 1} já foi processada. Pulando...")
                continue
            
            url = f"{base_url}?fsid={fsid}"
            print(f"[BOT] Acessando URL: {url}")
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)

            
            try:
                iframe_element = await page.wait_for_selector("iframe.custom-element__iframe", timeout=15000)
                iframe = await iframe_element.content_frame()

                if iframe:
                    print("[BOT] Iframe encontrado, tentando clicar no botão...")
                    await iframe.click('button[data-testid="funnel-buy-button"]')
                    print(f"[BOT] Botão de compra clicado na página {index + 1}!")
                else:
                    print("[BOT] Iframe não encontrado na página. Verifique o seletor.")

            except Exception as e:
                print(f"[BOT] Erro ao clicar no botão na página {index + 1}: {e}")

           
            paginas_concluidas += 1
            await atualizar_status_fsid(fsid, "processando", paginas_concluidas)
            print(f"[BOT] Progresso atualizado: {paginas_concluidas}/6")

            await page.wait_for_timeout(2000)  

        await browser.close()

async def processar_automatizacao():
    while True:
        fsid, paginas = await obter_fsid_pendente()
        if fsid:
            paginas_concluidas = int(paginas.split("/")[0]) if paginas else 0

            if paginas_concluidas < 6:
                print(f"[BOT] Processando FSID: {fsid} - Progresso atual: {paginas_concluidas}/6")
                await abrir_pagina_com_fsid(fsid, paginas_concluidas)
                await atualizar_status_fsid(fsid, "processado", 6)
                print(f"[BOT] FSID {fsid} finalizado!")
            else:
                print(f"[BOT] FSID {fsid} já foi processado. Pulando...")

        else:
            print("[BOT] Nenhum FSID pendente encontrado. Aguardando...")

        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(processar_automatizacao())
