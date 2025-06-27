import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestDuckDuckGoSearch:
    @pytest.fixture
    def browser(self):
        """Configuración del navegador Chrome en modo headless"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Usar el ChromeDriver instalado por la GitHub Action
        chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "chromedriver")
        service = Service(executable_path=chromedriver_path)
        
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def test_search_inmuebles(self, browser):
        """Test de búsqueda de inmuebles en DuckDuckGo"""
        try:
            # Navegar a DuckDuckGo
            browser.get("https://duckduckgo.com")
            print("Página cargada correctamente")
            
            # Encontrar el campo de búsqueda y escribir el término
            search_input = browser.find_element(By.NAME, "q")
            search_input.send_keys("inmuebles en Bogotá")
            print("Término de búsqueda ingresado")
            search_input.send_keys(Keys.RETURN)
            print("Búsqueda enviada")
            
            # Esperar a que los resultados aparezcan (usando diferentes selectores)
            wait = WebDriverWait(browser, 20)
            try:
                # Intentar diferentes selectores para los resultados
                results = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='result']"))
                )
                print("Resultados encontrados usando article[data-testid='result']")
            except:
                try:
                    results = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".react-results--main"))
                    )
                    print("Resultados encontrados usando .react-results--main")
                except:
                    # Tomar una captura de pantalla para depuración
                    browser.save_screenshot('error_screenshot.png')
                    print("Estado de la página:", browser.page_source[:500])
                    raise
            
            # Verificar que hay resultados
            assert results.is_displayed(), "No se encontraron resultados de búsqueda"
            
            # Verificar que la URL cambió
            current_url = browser.current_url
            assert "q=inmuebles+en+Bogot" in current_url.lower(), "La URL no refleja la búsqueda"
            
        except Exception as e:
            print(f"Error durante la prueba: {str(e)}")
            browser.save_screenshot('error_screenshot.png')
            print("URL actual:", browser.current_url)
            print("HTML de la página:", browser.page_source[:500])
            raise

    @pytest.mark.parametrize("search_term", [
        "inmuebles en Bogotá",
        "apartamentos en Bogotá",
        "casas en venta Bogotá"
    ])
    def test_parametrized_search(self, browser, search_term):
        """Test parametrizado para múltiples términos de búsqueda"""
        try:
            browser.get("https://duckduckgo.com")
            print(f"Página cargada para búsqueda: {search_term}")
            
            search_input = browser.find_element(By.NAME, "q")
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            print("Búsqueda enviada")
            
            wait = WebDriverWait(browser, 20)
            try:
                results = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='result']"))
                )
                print("Resultados encontrados usando article")
            except:
                try:
                    results = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".react-results--main"))
                    )
                    print("Resultados encontrados usando react-results")
                except:
                    browser.save_screenshot(f'error_{search_term.replace(" ", "_")}.png')
                    print("Estado de la página:", browser.page_source[:500])
                    raise
            
            assert results.is_displayed(), f"No se encontraron resultados para: {search_term}"
            assert search_term.lower().split()[0] in browser.current_url.lower(), f"La URL no refleja la búsqueda: {search_term}"
            
        except Exception as e:
            print(f"Error durante la prueba con término '{search_term}': {str(e)}")
            browser.save_screenshot(f'error_{search_term.replace(" ", "_")}.png')
            print("URL actual:", browser.current_url)
            print("HTML de la página:", browser.page_source[:500])
            raise 