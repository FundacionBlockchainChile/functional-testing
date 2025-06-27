import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import unquote

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
            
            # Esperar a que los resultados aparezcan usando múltiples selectores posibles
            wait = WebDriverWait(browser, 20)
            try:
                # Intentar encontrar resultados usando diferentes selectores
                selectors = [
                    "div[data-testid='mainline']",
                    "div[data-testid='search-results']",
                    ".react-results--main",
                    ".results",
                    "#links",
                    ".results-wrapper"
                ]
                
                for selector in selectors:
                    try:
                        results = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        print(f"Resultados encontrados usando selector: {selector}")
                        break
                    except:
                        continue
                
                # Si llegamos aquí sin encontrar resultados, tomamos una captura
                if not results:
                    browser.save_screenshot('error_screenshot.png')
                    print("Estado de la página:", browser.page_source[:1000])
                    raise Exception("No se encontraron resultados con ningún selector")
                
            except Exception as e:
                browser.save_screenshot('error_screenshot.png')
                print("Estado de la página:", browser.page_source[:1000])
                raise
            
            # Verificar que la URL cambió (decodificando la URL)
            current_url = unquote(browser.current_url.lower())
            print(f"URL decodificada: {current_url}")
            search_terms = ["inmuebles", "bogotá"]
            for term in search_terms:
                assert term in current_url, f"Término '{term}' no encontrado en la URL"
            
            # Verificar que hay al menos un resultado visible
            assert results.is_displayed(), "Los resultados no son visibles"
            
        except Exception as e:
            print(f"Error durante la prueba: {str(e)}")
            browser.save_screenshot('error_screenshot.png')
            print("URL actual:", browser.current_url)
            print("HTML de la página:", browser.page_source[:1000])
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
            
            # Esperar a que los resultados aparezcan usando múltiples selectores posibles
            wait = WebDriverWait(browser, 20)
            try:
                # Intentar encontrar resultados usando diferentes selectores
                selectors = [
                    "div[data-testid='mainline']",
                    "div[data-testid='search-results']",
                    ".react-results--main",
                    ".results",
                    "#links",
                    ".results-wrapper"
                ]
                
                for selector in selectors:
                    try:
                        results = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        print(f"Resultados encontrados usando selector: {selector}")
                        break
                    except:
                        continue
                
                # Si llegamos aquí sin encontrar resultados, tomamos una captura
                if not results:
                    browser.save_screenshot(f'error_{search_term.replace(" ", "_")}.png')
                    print("Estado de la página:", browser.page_source[:1000])
                    raise Exception("No se encontraron resultados con ningún selector")
                
            except Exception as e:
                browser.save_screenshot(f'error_{search_term.replace(" ", "_")}.png')
                print("Estado de la página:", browser.page_source[:1000])
                raise
            
            # Verificar que la URL cambió (decodificando la URL)
            current_url = unquote(browser.current_url.lower())
            print(f"URL decodificada: {current_url}")
            main_term = search_term.lower().split()[0]
            assert main_term in current_url, f"Término principal '{main_term}' no encontrado en la URL"
            
            # Verificar que hay al menos un resultado visible
            assert results.is_displayed(), f"Los resultados no son visibles para: {search_term}"
            
        except Exception as e:
            print(f"Error durante la prueba con término '{search_term}': {str(e)}")
            browser.save_screenshot(f'error_{search_term.replace(" ", "_")}.png')
            print("URL actual:", browser.current_url)
            print("HTML de la página:", browser.page_source[:1000])
            raise 