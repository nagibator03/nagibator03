from playwright.async_api import async_playwright

sessions = {}  # user_id -> character_url -> page

async def get_session(user_id, character_url):
    if user_id not in sessions:
        sessions[user_id] = {}

    if character_url in sessions[user_id]:
        return sessions[user_id][character_url]

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto(character_url)
    await page.wait_for_selector("textarea")

    sessions[user_id][character_url] = page
    return page

async def send_message(user_id, character_url, text):
    page = await get_session(user_id, character_url)

    await page.fill("textarea", text)
    await page.keyboard.press("Enter")

    await page.wait_for_timeout(4000)
    outputs = await page.query_selector_all(".output-text")

    if not outputs:
        return "…"

    return await outputs[-1].inner_text()
