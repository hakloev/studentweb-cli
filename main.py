import time
import sys
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from config_parser import StudentWebConfig


class StudentWeb(object):

    def __init__(self):
        self.config = StudentWebConfig().get_config()
        #self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS(executable_path=self.config['phantom_js_executable_path'])
        self.driver.set_window_size(1500, 1000)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(20)

        self.default_implicit_wait = 10
        self.driver.implicitly_wait(self.default_implicit_wait)

    def _shutdown(self):
        self.driver.delete_all_cookies()
        self.driver.close()
        self.driver.quit()

    def get_results(self):
        def ready_state_complete(d):
            return d.execute_script("return document.readyState") == "complete"

        self.driver.get('https://fsweb.no/studentweb/login.jsf?inst=' + self.config['institution'])

        self.driver.find_element_by_class_name('login-name-pin').click()
        login_element = self.driver.find_element_by_xpath("//*[@id='login-box']/div[3]/form[1]")
        login_element_id = login_element.get_attribute('id')

        pnr_element = self.driver.find_element_by_id(login_element_id + ':fodselsnummer')
        pin_element = self.driver.find_element_by_id(login_element_id + ':pincode')
        pnr_element.send_keys(self.config['pnr'])
        pin_element.send_keys(self.config['pin'])

        self.driver.find_element_by_id(login_element_id + ':login').send_keys(Keys.ENTER)

        while self._wait_for_element((By.ID, 'messagesPanelGroup')):
            time.sleep(0.5)

        while self._wait_for_element((By.LINK_TEXT, 'Resultater')):
            time.sleep(0.5)
        self.driver.find_element_by_link_text('Resultater').click()

        while self._wait_for_element((By.TAG_NAME, 'tbody')):
            time.sleep(0.5)

        """
        try:
            WebDriverWait(self.driver, 10).until(ready_state_complete)
        except WebDriverException:
            print('WebDriverException: Timeout while waiting for /studentweb/resultater.jsf')
        finally:
            self._shutdown()
            return
        """

        results = []
        try:
            #WebDriverWait(self.driver, 10).until(lambda s: not self._is_element_present((By.ID, 'resultatlisteForm:HeleResultater:resultaterPanel')))
            #  element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'resultatlisteForm:HeleResultater:resultaterPanel')))
            #  print(element)
            #result_table = self.driver.find_element_by_id('resultatlisteForm:HeleResultater:resultaterPanel')
            #result_table = self.driver.find_element_by_tag_name('tbody')
            result_table = self.driver.find_elements_by_tag_name('tr')
            for row in result_table:
                if row.get_attribute('class') != 'none':
                    continue

                cells = row.find_elements_by_tag_name('td')
                course_info = tuple(cells[1].text.split('\n'))
                course_id, course_name = course_info[0], course_info[1]
                course_grade = cells[5].text

                results.append((course_id, course_name, course_grade))
        except NoSuchElementException as e:
            print(self.driver.current_url)
            print('Could not find results table\n%s' % e)
        finally:
            self._shutdown()
            return results

    def _wait_for_element(self, *locator):
        try:
            print("Waiting... " + str(c) + " for %s" % locator)
            yes = self.driver.find_element(*locator)
            print("Found!")
            return True
        except:
            return False

    def _is_element_present(self, *locator):
        self.driver.implicitly_wait(0)
        try:
            self.driver.find_element(*locator)
            print('is present')
            return True
        except NoSuchElementException:
            print('is not present')
            return False
        finally:
            # set back to where you once belonged
            self.driver.implicitly_wait(self.default_implicit_wait)

if __name__ == "__main__":
    sw = StudentWeb()
    r = sw.get_results()
    for result in r:
        print('%-8s\t%-60s\t%s' % result)



