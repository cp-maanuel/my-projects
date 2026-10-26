from playwright.sync_api import sync_playwright
import re

def survey(main_surveys_ur):
    while True:
        do_survey_buttons = page.locator("a, button, input").filter(
        has_text=re.compile(r"\s*Do\s+the\s+Survey\s*", re.IGNORECASE)
            ).filter(
        has_not_text=re.compile(r"Completed|Submitted", re.IGNORECASE)
            )

        if do_survey_buttons.count() == 0:
            #no more surveys left
            break;

        do_survey_buttons.first.click()
        page.wait_for_load_state("networkidle")
        current_survey_url = page.url

        case2(current_survey_url,main_surveys_ur)

def option(current_survey_url,main_surveys_ur,c):
    
    page.evaluate("""
        () => {
            // 1. Select first radio button in table rows (ETLab layout style)
            const rows = document.querySelectorAll('tr');
            rows.forEach(row => {
                const radio = row.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    radio.click();
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            // 2. Fallback: Select first radio button in every unique question group name
            const radioNames = [...new Set(Array.from(document.querySelectorAll('input[type="radio"]')).map(r => r.name))];
            radioNames.forEach(name => {
                const firstRadio = document.querySelector(`input[type="radio"][name="${name}"]`);
                if (firstRadio) {
                    firstRadio.checked = true;
                    firstRadio.click();
                    firstRadio.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }
    """)

    submit_btn = page.get_by_role("button", name=re.compile(r"\s*Save|Submit|Update|Proceed\s*", re.IGNORECASE)).first
    submit_btn.click()

    if (c==0):
        page.goto(main_surveys_ur)
        page.wait_for_load_state("networkidle")
        survey()
    elif(c==1):
        page.goto(current_survey_url)
        page.wait_for_load_state("networkidle")
        case2(current_survey_url,main_surveys_ur)


def case2(current_survey_url,main_surveys_ur):

    c=1
    while True:

        answer_q_buttons = page.locator("a, button, input, div, span").filter(
            has_text=re.compile(r"\s*Answer\s+Questions?\s*", re.IGNORECASE)
        ).filter(
            has_not_text=re.compile(r"Completed|Submitted", re.IGNORECASE)
        )
    
        if answer_q_buttons.count() == 0:
            c=0
            option(current_survey_url,main_surveys_ur,c)
            break
        answer_q_buttons.first.click()
        page.wait_for_load_state("networkidle")
        option(current_survey_url,main_surveys_ur,c)


with sync_playwright() as p:
    
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    
    print("Opening ETLab login page...")
    page.goto("https://jecc.etlab.in/")
    
    page.fill("input[name='LoginForm[username]']", "USERNAME")
    page.fill("input[name='LoginForm[password]']", "PASSWORD")
    
    page.click("button[type='submit']")
    
    page.wait_for_load_state("networkidle")
    print("Logged in successfully!")

    page.click("text=Survey")
    page.wait_for_load_state("networkidle")

    main_surveys_url = page.url
    survey(main_surveys_url)


