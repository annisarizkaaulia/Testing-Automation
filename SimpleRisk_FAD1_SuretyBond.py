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
def save_screenshot(driver, base_name="screenshot",test_name="FAD1 SuretyBond"):
    folder = os.path.join("TC1", test_name)
    os.makedirs(folder, exist_ok=True)
    waktu = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{waktu}.png"
    path = os.path.join(folder, filename)
    driver.save_screenshot(path)
    print(f"Screenshot disimpan di: {path}")
    return path

# ============Class PDF ============ #

class CustomPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Arial", 'B', 10)
            self.set_fill_color(255, 255, 255)

            # Ukuran tabel
            page_margin = 20
            total_width = 210 - 2 * page_margin
            logo_width = 50
            right_width = 30
            center_width = total_width - logo_width - right_width
            cell_height = 7
            top_y = self.get_y()

            logo_x = page_margin
            logo_y = top_y
            logo_cell_width = logo_width
            logo_cell_height = cell_height * 3  # tinggi kolom logo (3 baris)

            # ===== CELL KIRI (Logo) =====
            self.set_xy(logo_x, logo_y)
            self.cell(logo_cell_width, logo_cell_height, "", border=1)

            # ====== TAMBAHKAN LOGO ======
            logo_path = "logo askrindo.png"
            if os.path.exists(logo_path):
                # Ukuran asli gambar (ambil langsung)
                from PIL import Image
                img = Image.open(logo_path)
                img_w, img_h = img.size
                aspect_ratio = img_h / img_w

                # Hitung ukuran gambar supaya muat & rata tengah
                max_img_width = logo_cell_width - 6
                max_img_height = logo_cell_height - 4
                draw_w = max_img_width
                draw_h = draw_w * aspect_ratio

                if draw_h > max_img_height:
                    draw_h = max_img_height
                    draw_w = draw_h / aspect_ratio

                img_x = logo_x + (logo_cell_width - draw_w) / 2
                img_y = logo_y + (logo_cell_height - draw_h) / 2
                self.image(logo_path, x=img_x, y=img_y, w=draw_w, h=draw_h)

            # ===== TABEL TENGAH (3 baris) =====
            self.set_font("Arial", '', 10)

            self.set_x(logo_x + logo_cell_width)
            self.cell(center_width, cell_height, "ASKRINDO", border=1, ln=2, align='C')

            self.set_x(logo_x + logo_cell_width)
            self.cell(center_width, cell_height, "DOKUMEN HASIL TESTING", border=1, ln=2, align='C')

            self.set_x(logo_x + logo_cell_width)
            self.cell(center_width, cell_height, "UPR Enhancement Portal Usulan RKAP", border=1, ln=0, align='C')

            # ===== CELL KANAN (UAT) =====
            self.set_xy(logo_x + logo_cell_width + center_width, logo_y)
            self.set_font("Arial", '', 10)
            self.cell(right_width, logo_cell_height, "UAT", border=1, align='C')

            # Spasi ke bawah
            self.ln(logo_cell_height + 8)

        # Jangan tampilkan nomor halaman di halaman pertama
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)

        box_width = 8
        box_height = 8
        page_number_text = f"{self.page_no() -0}"  # agar halaman kedua jadi "1"

        x_position = self.w - self.r_margin - box_width
        y_position = self.get_y()

        self.rect(x_position, y_position, box_width, box_height)
        self.set_xy(x_position, y_position)
        self.cell(box_width, box_height, page_number_text, align='C', fill=True)

def generate_pdf_report(
    testcase_id="TC01",
    testcase_name="Output FAD1 Surety Bond",
    actual_result=None,
    logo_path="logo askrindo.png",
    tester="chevin",
    expected_result="Sistem menampilkan FAD1 COB SuretyBond",
    folder_pdf="Laporan Passed",
    status=None,
    screenshot_paths=None,
):
    #-------Simpan Folder PDF-----------#
    folder = os.path.join("TC1", folder_pdf)
    os.makedirs(folder, exist_ok=True)
    waktu = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(folder, f"report_{waktu}.pdf")

    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ===== Halaman 1: Judul =====
    pdf.add_page()

    if os.path.exists(logo_path):
         pdf.image(logo_path, x=20, y=16, w=45)  # Rata kiri
    else:
         print("Logo tidak ditemukan")
  
    pdf.set_font("Arial", 'B', 25)
    pdf.set_xy(20,60)
    pdf.cell(0, 12, "Laporan Hasil Pengujian SIT", ln=True, align='L')
    pdf.set_x(20)
    pdf.cell(0, 12, "Aplikasi Simple Risk", ln=True, align='L')
    pdf.set_x(20)
    pdf.cell(0, 12, "12/08/2025", ln=True, align='L')
    pdf.set_x(20)
    pdf.cell(0, 12, "V.I.II", ln=True, align='L')
    

    # ===== Halaman 2: Header, Logo, Ringkasan =====
    pdf.add_page()
    pdf.set_y(40)
    pdf.set_font("Arial", size=10)

    summary_data = [
        ["TestCaseID", testcase_id],
        ["TestCaseName", testcase_name],
        ["Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Tester", tester],
        ["Status", status],
        ["Expected Result", expected_result],
    ]

    for key, value in summary_data:
        pdf.set_x(20)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 6, str(key), border=1, fill=True)
        pdf.cell(115, 6, str(value), border=1)
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

    steps_per_page = 2
    y_start = 35  # Y awal supaya tidak terlalu jauh dari header
    for i, step in enumerate(test_steps):
        if i != 0 and i % steps_per_page == 0:
            pdf.add_page()
            pdf.set_y(y_start)  # Mulai dari bawah header lagi

        pdf.set_x(20)
        pdf.set_font("Arial", size=11)
        pdf.cell(20, 10, step, ln=True)
        pdf.ln(2)

        if i < len(screenshot_paths) and os.path.exists(screenshot_paths[i]):
            pdf.set_x(20)
            pdf.image(screenshot_paths[i], x=20, w=150)
            pdf.ln(2)
        

    # Simpan PDF
    pdf.set_font("Arial", '', 11)
    pdf.set_x(20)
    pdf.cell(0, 10, f"Actual Result: {actual_result}", ln=True)
    
    pdf.output(pdf_path)
    print(f"PDF berhasil disimpan ke: {pdf_path}")

# ========== Test Case01 ========== #
def test_login_success(driver):
    username = "1939"
    password = "@Askrindo123"
    target_url = "http://10.100.20.53:8084/"

    driver.get(target_url)
    wait = WebDriverWait(driver, 20)
    driver.delete_all_cookies()
    time.sleep(2)

    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='login-email']"))).send_keys(username)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Masukan Password']"))).send_keys(password)

        screenshot_path1 = save_screenshot(driver, "sebelum_login")

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Sign in']"))).click()

        # Tunggu halaman berhasil login
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='SimpleRisk']")))
        screenshot_path2 = save_screenshot(driver, "login_berhasil")

        
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
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Jaminan Penawaran")

        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_awal"))).send_keys("17/07/2025")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_akhir"))).send_keys("30/12/2025")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_permohonan"))).send_keys("17/07/2025")

        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='sumber_anggaran']")))
        Select(select_elem).select_by_visible_text("BUMN")
        wait.until(EC.visibility_of_element_located((By.NAME, "nomor_surat_permohonan"))).send_keys("NSP/ASK/09088")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_penerimaan_dokumen"))).send_keys("18/07/2025")
        screenshot_path3 = save_screenshot(driver, "Informasi Umum")

        #Informasi Principal
        wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/vertical-layout/div/content/div/app-form/form/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div/button"))).click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/form/div/div/div/div[2]/div/input"))).send_keys("Tunas Jaya")
        wait.until(EC.element_to_be_clickable(( By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/form/div/div/div/div[2]/div/div/button"))).click() 
        wait.until(lambda driver: len(driver.find_elements(By.XPATH, "//datatable-body-row")) > 0)
        screenshot_path4 = save_screenshot(driver, "Pilih Debitur")

        wait.until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/ngb-modal-window[1]/div[1]/div[1]/div[2]/section[1]/ngx-datatable[1]/div[1]/datatable-body[1]/datatable-selection[1]/datatable-scroller[1]/datatable-row-wrapper[1]/datatable-body-row[1]/div[2]/datatable-body-cell[6]/div[1]/a[1]/*[name()='svg'][1]"))).click()
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='provinsi']")))
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='kota']")))
        time.sleep(1)
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
        screenshot_path5 = save_screenshot(driver, "Informasi Principal")

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
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lokasi_proyek_kota']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Kota Pangkal Pinang")
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_obligee"))).send_keys("Arlina")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='bentuk_obligee']")))
        Select(select_elem).select_by_visible_text("Pemerintahan")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lokasi_obligee_provinsi']")))
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        time.sleep(1)   
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='lokasi_obligee_kota']")))
        Select(select_elem).select_by_visible_text("Kota Pangkal Pinang")
        screenshot_path6 = save_screenshot(driver, "Informasi Proyek")

        #Informasi Lainnya
        wait.until(EC.visibility_of_element_located((By.NAME, "nomor_underlying"))).send_keys("NU/ASK/190807")
        wait.until(EC.visibility_of_element_located((By.NAME, "tanggal_underlying"))).send_keys("NU/ASK/190807")
        screenshot_path7 = save_screenshot(driver, "Informasi Lainnya")

        #Hasil Pengecekan
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='nasabah_blacklist']")))
        time
        Select(select_elem).select_by_visible_text("Tidak (Bukan Nasabah Blacklist)")
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='ketentuan_collateral']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")   
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='tarif_rate_premi_sesuai']")))
        time.sleep(1)   
        Select(select_elem).select_by_visible_text("Ya")  
        wait.until(EC.visibility_of_element_located((By.NAME, "besaran_cash_collateral"))).send_keys("10")
        screenshot_path8 = save_screenshot(driver, "Hasil Pengecekan")

        #Disclaimer
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='menggunakan_hukum_indonesia']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")  
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='isi_wording_sesuai_sop']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")  
        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='spkmgr_sesuai_sop']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")  
        screenshot_path9 = save_screenshot(driver, "Disclaimer")

        #Pengusul
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_admin_polis"))).send_keys("Chevin Rifan P")
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_pemutus"))).send_keys("Cynthia")
        wait.until(EC.visibility_of_element_located((By.NAME, "nama_fungsional_pemasaran"))).send_keys("Abdurrahman")
        screenshot_path8 = save_screenshot(driver, "Informasi Lainnya")
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Preview']"))).click()
        screenshot_path10 = save_screenshot(driver, "Pengusul")

        #Checkbox Validasi Dokumen Sesuai
        checkbox = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='validasi_dokumen_sesuai']")))

        if not checkbox.is_selected():checkbox.click()
        screenshot_path11 = save_screenshot(driver, "Validasi Dokumen")

        # Klik tombol Accept dan Simpan
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Accept']"))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Simpan']"))).click()
        screenshot_path12 = save_screenshot(driver, "Simpan")
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Ya']"))).click()
        time.sleep(2)
        #pindah ke tab baru untuk melihat laporan
        driver.switch_to.window(driver.window_handles[1])
        screenshot_path13 = save_screenshot(driver, "Report Selesai")

        # Generate report berhasil
        generate_pdf_report(
            status="Passed",
            screenshot_paths=[screenshot_path1, screenshot_path2,screenshot_path3,screenshot_path4, screenshot_path5, screenshot_path6, screenshot_path7,screenshot_path8, screenshot_path9, screenshot_path10, screenshot_path11, screenshot_path12, screenshot_path13],
            actual_result="Berhasil Input dan Generate PDF SimpleRisk"
        )
        assert True

    except Exception as e:
        screenshot_path_fail = save_screenshot(driver, "login_gagal")
        generate_pdf_report(
            status="Not Passed",
            screenshot_paths=[screenshot_path_fail],
            actual_result="Gagal Input " + str(e)
        )
        assert False, str(e)
