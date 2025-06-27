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
        chrome_options.add_argument("--headless=new")  # Nueva sintaxis para Chrome >= 109
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
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
            
            # Encontrar el campo de búsqueda y escribir el término
            search_input = browser.find_element(By.NAME, "q")
            search_input.send_keys("inmuebles en Bogotá")
            search_input.send_keys(Keys.RETURN)
            
            # Esperar a que los resultados aparezcan
            wait = WebDriverWait(browser, 10)
            results = wait.until(
                EC.presence_of_element_located((By.ID, "links"))
            )
            
            # Verificar que hay resultados
            assert results.is_displayed(), "No se encontraron resultados de búsqueda"
            
            # Verificar que el título de la página cambió
            assert "inmuebles en Bogotá" in browser.title.lower(), "El título de la página no refleja la búsqueda"
        except Exception as e:
            print(f"Error durante la prueba: {str(e)}")
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
            
            search_input = browser.find_element(By.NAME, "q")
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            
            wait = WebDriverWait(browser, 10)
            results = wait.until(
                EC.presence_of_element_located((By.ID, "links"))
            )
            
            assert results.is_displayed(), f"No se encontraron resultados para: {search_term}"
            assert search_term.lower() in browser.title.lower(), f"El título no refleja la búsqueda: {search_term}"
        except Exception as e:
            print(f"Error durante la prueba con término '{search_term}': {str(e)}")
            raise 