import re
from playwright.sync_api import sync_playwright

def solve_all_surveys():
    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("Opening ETLab login page...")
        page.goto("https://jecc.etlab.in/")

        page.fill("input[name='LoginForm[username]']", "USERNAME")
        page.fill("input[name='LoginForm[password]']", "PASSWORD")
        page.click("button[type='submit']")

        page.wait_for_load_state("networkidle")

        print("Navigating to Surveys...")
        page.click("text=Survey")
        page.wait_for_load_state("networkidle")

        main_surveys_url = page.url

        while True:
            
            do_survey_buttons = page.locator("a, button, input").filter(
                has_text=re.compile(r"\s*Do\s+the\s+Survey\s*", re.IGNORECASE)
            ).filter(
                has_not_text=re.compile(r"Completed|Submitted", re.IGNORECASE)
            )

            if do_survey_buttons.count() == 0:
                print("\nNo more active 'Do the Survey' links remaining! All finished.")
                break

            print(f"\n[Main] Remaining active surveys: {do_survey_buttons.count()}. Opening next...")
            do_survey_buttons.first.click()
            page.wait_for_load_state("networkidle")

            current_survey_url = page.url

            while True:
                
                answer_q_buttons = page.locator("a, button, input, div, span").filter(
                    has_text=re.compile(r"\s*Answer\s+Questions?\s*", re.IGNORECASE)
                ).filter(
                    has_not_text=re.compile(r"Completed|Submitted", re.IGNORECASE)
                )

                if answer_q_buttons.count() == 0:
                    print("  All active 'Answer Questions' sub-tasks cleared for this survey.")
                    break

                print(f"  [Sub-task] Found active button. Clicking it...")
                
                answer_q_buttons.first.click(force=True)
                page.wait_for_load_state("networkidle")

                page.evaluate("""
                    () => {
                        // 1. Select first radio button in table rows
                        const rows = document.querySelectorAll('tr');
                        rows.forEach(row => {
                            const radio = row.querySelector('input[type="radio"]');
                            if (radio) {
                                radio.checked = true;
                                radio.click();
                                radio.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        });

                        // 2. Select first radio button in every unique question group
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
                if submit_btn.is_visible():
                    print("  Submitting form...")
                    submit_btn.click()
                    try:
                        page.wait_for_load_state("networkidle", timeout=5000)
                    except:
                        pass

                if "answer" in page.url.lower():
                    page.goto(current_survey_url)
                    page.wait_for_load_state("networkidle")

            page.goto(main_surveys_url)
            page.wait_for_load_state("networkidle")

        print("\nAll surveys completed successfully!")
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    solve_all_surveys()
