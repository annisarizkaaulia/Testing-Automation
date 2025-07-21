import os
import time
import datetime
import pytest
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select  # pastikan import ini ada
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select



# ========== Setup WebDriver ========== #
@pytest.fixture
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_page_load_timeout(30)
    yield driver
    driver.quit()

# ========== Simpan Screenshot ========== #
def save_screenshot(driver, base_name="screenshot", test_name="login_test"):
    folder = os.path.join("TC1", test_name)
    os.makedirs(folder, exist_ok=True)
    waktu = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{waktu}.png"
    path = os.path.join(folder, filename)
    driver.save_screenshot(path)
    print(f"Screenshot disimpan di: {path}")
    return path

# ========== Generate PDF Report ========== #
def generate_pdf_report(
    status,
    screenshot_paths,
    test_name="login_test",
    testcase_id="TC01",
    testcase_name="Login Test",
    actual_result="",
    logo_path="logo askrindo.png"
):
    folder = os.path.join("TC1", test_name)
    os.makedirs(folder, exist_ok=True)
    waktu = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(folder, f"report_{waktu}.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ===== Header + Logo =====
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)
    pdf.set_font("Arial", size=16)
    pdf.set_xy(45, 10)
    pdf.ln(10)

    # ===== Summary Table =====
    summary_data = [
        ["TestCaseID", testcase_id],
        ["TestCaseName", testcase_name],
        ["Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Status", status],
        ["Expected Result", "User berhasil masuk ke dashboard"],
    ]
    pdf.set_font("Arial", size=10)

    for key, value in summary_data:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(50, 10, str(key), border=1, fill=True)
        pdf.cell(130, 10, str(value), border=1)
        pdf.ln()

    pdf.ln(5)

    # ===== Test Steps + Screenshots =====
    test_steps = [
    "[Test Step 1]: Input username dan password yang benar",
    "[Test Step 2]: Klik tombol login",
    "[Test Step 3]: Input field pada Informasi Umum",
    "[Test Step 4]: Input field pada Informasi Principal pada Pilih Debitur",
    "[Test Step 5]: Lanjutkan Input field pada Informasi Principal",
    "[Test Step 6]: Input field pada Informasi Proyek",
    "[Test Step 7]: Input field pada Informasi Lainnya",
    "[Test Step 8]: Input field pada Hasil Pengecekan",
    "[Test Step 9]: Input field pada Disclaimer",
    "[Test Step 10]: Input field pada Pengusul",
    "[Test Step 11]: Validasi Checkbox Dokumen Sesuai",
    "[Test Step 12]: Simpan",
    "[Test Step 13]: Cek data PDF",



]


    for i, step in enumerate(test_steps):
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 10, step, ln=True)
        pdf.ln(2)

        if i < len(screenshot_paths) and os.path.exists(screenshot_paths[i]):
            pdf.image(screenshot_paths[i], x=10, w=190)
            pdf.ln(2)

    # ===== Actual Result =====
    pdf.set_font("Arial", style='', size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(23, 10, "Actual Result :", ln=False)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, actual_result, ln=True)
    pdf.ln(2)

    pdf.output(pdf_path)
    print(f"Laporan PDF disimpan di: {pdf_path}")

# ========== Test Case: Login & Pilih Dropdown ========== #
def test_login_success(driver):
    username = "1939"
    password = "@Askrindo123"
    target_url = "http://10.100.20.53:8084/"
    test_name = "Menampilkan Report FAD sesuai dengan analisa"
    testcase_id = "TC01"
    testcase_name = "Login Test"

    driver.get(target_url)
    wait = WebDriverWait(driver, 20)
    driver.delete_all_cookies()
    time.sleep(2)

    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='login-email']"))).send_keys(username)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Masukan Password']"))).send_keys(password)

        screenshot_path1 = save_screenshot(driver, "sebelum_login", test_name)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Sign in']"))).click()

        # Tunggu halaman berhasil login
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='SimpleRisk']")))
        screenshot_path2 = save_screenshot(driver, "login_berhasil", test_name)
        # Informasu Umum
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='sumber_bisnis']")))
        Select(select_elem).select_by_visible_text("Direct")

        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='cob']")))
        Select(select_elem).select_by_visible_text("Surety Bond")

        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='currency']")))
        Select(select_elem).select_by_visible_text("IDR")

        wait.until(EC.visibility_of_element_located((By.NAME, "nilaiPenjaminan"))).send_keys("230000000")

        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='jenis_permohonan']")))
        Select(select_elem).select_by_visible_text("Permohonan Baru")

        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='jenis_penjaminan']")))
        Select(select_elem).select_by_visible_text("Jaminan Penawaran")

        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_awal"))).send_keys("17/07/2025")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_akhir"))).send_keys("30/12/2025")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_permohonan"))).send_keys("17/07/2025")

        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='sumber_anggaran']")))
        Select(select_elem).select_by_visible_text("BUMN")
        wait.until(EC.visibility_of_element_located((By.NAME, "nomor_surat_permohonan"))).send_keys("NSP/ASK/09088")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_penerimaan_dokumen"))).send_keys("18/07/2025")
        screenshot_path3 = save_screenshot(driver, "Informasi Umum", test_name)

        #Informasi Principal
        wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/vertical-layout/div/content/div/app-form/form/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div/button"))).click()
        wait = WebDriverWait(driver, 30)
        wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/form/div/div/div/div[2]/div/input"))).send_keys("Tunas Jaya")
        wait.until(EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/form/div/div/div/div[2]/div/div/button"))).click() 
        wait.until(lambda driver: len(driver.find_elements(By.XPATH, "//datatable-body-row")) > 0)
        screenshot_path4 = save_screenshot(driver, "Pilih Debitur", test_name)

        wait.until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/ngb-modal-window[1]/div[1]/div[1]/div[2]/section[1]/ngx-datatable[1]/div[1]/datatable-body[1]/datatable-selection[1]/datatable-scroller[1]/datatable-row-wrapper[1]/datatable-body-row[1]/div[2]/datatable-body-cell[6]/div[1]/a[1]/*[name()='svg'][1]"))).click()
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='provinsi']")))
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='kota']")))
        Select(select_elem).select_by_visible_text("Kota Pangkal Pinang")
        wait.until(EC.visibility_of_element_located((By.NAME, "pic"))).send_keys("Annisa Rizka Aulia")
        wait.until(EC.visibility_of_element_located((By.NAME, "telp"))).send_keys("8785683445")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='nsa']")))
        Select(select_elem).select_by_visible_text("Nasabah Baru")
        wait.until(EC.visibility_of_element_located((By.NAME, "pengalaman_kerja"))).send_keys("1")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='bentuk_principal']")))
        Select(select_elem).select_by_visible_text("Non KSO")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lk_1tahun_terakhir']")))
        Select(select_elem).select_by_visible_text("Ya")
        screenshot_path5 = save_screenshot(driver, "Informasi Principal", test_name)

        #Informasi Proyek
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_proyek"))).send_keys("Proyek Pembangunan Jembatan")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='jenis_proyek']")))
        Select(select_elem).select_by_visible_text("Non Konstruksi")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='sektor_pekerjaan']")))
        Select(select_elem).select_by_visible_text("Lainnya")
        wait.until(EC.visibility_of_element_located((By.NAME, "nilai_proyek"))).send_keys("100000000")
        wait.until(EC.visibility_of_element_located((By.NAME, "nilai_penjaminan"))).send_keys("100000000")
        wait.until(EC.visibility_of_element_located((By.NAME, "jkw_awal_proyek"))).send_keys("17/07/2025")
        wait.until(EC.visibility_of_element_located((By.NAME, "jkw_akhir_proyek"))).send_keys("30/07/2025")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lokasi_proyek_provinsi']")))
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lokasi_proyek_kota']")))
        Select(select_elem).select_by_visible_text("Kota Pangkal Pinang")
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_obligee"))).send_keys("Arlina")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='bentuk_obligee']")))
        Select(select_elem).select_by_visible_text("Pemerintahan")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lokasi_obligee_provinsi']")))
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lokasi_obligee_kota']")))
        Select(select_elem).select_by_visible_text("Kota Pangkal Pinang")
        screenshot_path6 = save_screenshot(driver, "Informasi Proyek", test_name)

        #Informasi Lainnya
        wait.until(EC.visibility_of_element_located((By.NAME, "nomor_underlying"))).send_keys("NU/ASK/190807")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_underlying"))).send_keys("NU/ASK/190807")
        screenshot_path7 = save_screenshot(driver, "Informasi Lainnya", test_name)

        #Hasil Pengecekan
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='nasabah_blacklist']")))
        Select(select_elem).select_by_visible_text("Tidak (Bukan Nasabah Blacklist)")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='ketentuan_collateral']")))
        Select(select_elem).select_by_visible_text("Ya")   
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='tarif_rate_premi_sesuai']")))
        Select(select_elem).select_by_visible_text("Ya")  
        wait.until(EC.visibility_of_element_located((By.NAME, "besaran_cash_collateral"))).send_keys("10")
        screenshot_path8 = save_screenshot(driver, "Hasil Pengecekan", test_name)

        #Disclaimer
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='menggunakan_hukum_indonesia']")))
        Select(select_elem).select_by_visible_text("Ya")  
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='isi_wording_sesuai_sop']")))
        Select(select_elem).select_by_visible_text("Ya")  
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='spkmgr_sesuai_sop']")))
        Select(select_elem).select_by_visible_text("Ya")  
        screenshot_path9 = save_screenshot(driver, "Disclaimer", test_name)

        #Pengusul
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_admin_polis"))).send_keys("Chevin Rifan P")
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_pemutus"))).send_keys("Cynthia")
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_fungsional_pemasaran"))).send_keys("Abdurrahman")
        screenshot_path8 = save_screenshot(driver, "Informasi Lainnya", test_name)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Preview']"))).click()
        screenshot_path10 = save_screenshot(driver, "Pengusul", test_name)

        #Checkbox Validasi Dokumen Sesuai
        checkbox = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='validasi_dokumen_sesuai']")))

        if not checkbox.is_selected():checkbox.click()
        screenshot_path11 = save_screenshot(driver, "Validasi Dokumen", test_name)

        # Klik tombol Accept dan Simpan
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Accept']"))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Simpan']"))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Ya']"))).click()
        
        screenshot_path12 = save_screenshot(driver, "Simpan", test_name)


        # Generate report berhasil
        generate_pdf_report(
            status="Passed",
            screenshot_paths=[screenshot_path1, screenshot_path2,screenshot_path3,screenshot_path4, screenshot_path5, screenshot_path6, screenshot_path7,screenshot_path8, screenshot_path9, screenshot_path10, screenshot_path11, screenshot_path12],
            test_name=test_name,
            testcase_id=testcase_id,
            testcase_name=testcase_name,
            actual_result="Berhasil Input dan Generate PDF SimpleRisk"
        )
        assert True

    except Exception as e:
        screenshot_path_fail = save_screenshot(driver, "login_gagal", test_name)
        generate_pdf_report(
            status="Not Passed",
            screenshot_paths=[screenshot_path_fail],
            test_name=test_name,
            testcase_id=testcase_id,
            testcase_name=testcase_name,
            actual_result="Gagal Input " + str(e)
        )
        assert False, str(e)
