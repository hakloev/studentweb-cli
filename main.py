import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config_parser import StudentWebConfig


class StudentWeb(object):

    def __init__(self):
        self.config = StudentWebConfig().get_config()

        self.driver = webdriver.PhantomJS(executable_path=self.config['phantom_js_executable_path'])
        self.driver.set_window_size(1500, 1000)
        self.driver.maximize_window()
        self._element_wait = 0.5  # Default timeout for _wait_for_element
        self._implicit_wait = 20  # Default timeout for webdriver.implicity_wait and page_load_timeout
        self.driver.set_page_load_timeout(self._implicit_wait)
        self.driver.implicitly_wait(self._implicit_wait)

    def _shutdown(self):
        """
        Shutdown webdriver, and delete cookies
        """
        self.driver.delete_all_cookies()
        self.driver.close()
        self.driver.quit()

    def get_results(self):
        """
        Do click sequence through studentweb to locate and return grades
        TODO: The get-requests need some error handling (TimeoutException and so on)
        :return: The grades as a list of tuples for each subject
        """
        self.driver.get('https://fsweb.no/studentweb/login.jsf?inst=' + self.config['institution'])

        while self._wait_for_element((By.CLASS_NAME, 'login-name-pin')):
            time.sleep(self._element_wait)

        self.driver.find_element_by_class_name('login-name-pin').click()
        login_element = self.driver.find_element_by_xpath("//*[@id='login-box']/div[3]/form[1]")
        login_element_id = login_element.get_attribute('id')

        pnr_element = self.driver.find_element_by_id(login_element_id + ':fodselsnummer')
        pin_element = self.driver.find_element_by_id(login_element_id + ':pincode')
        pnr_element.send_keys(self.config['pnr'])
        pin_element.send_keys(self.config['pin'])

        self.driver.find_element_by_id(login_element_id + ':login').send_keys(Keys.ENTER)

        # TODO: Add timeout check for the following three while loops
        while self._wait_for_element((By.ID, 'messagesPanelGroup')):
            time.sleep(self._element_wait)

        while self._wait_for_element((By.LINK_TEXT, 'Resultater')):
            time.sleep(self._element_wait)
        self.driver.find_element_by_link_text('Resultater').click()

        while self._wait_for_element((By.TAG_NAME, 'tbody')):
            time.sleep(self._element_wait)

        results = []
        # TODO: After the reformatting, this try/catch is most likely not needed
        try:
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
            print('Could not locate the results table at %s\n%s' % (self.driver.current_url, e))
        finally:
            self._shutdown()
            return results

    def _wait_for_element(self, *locator):
        """
        Function to check if an element has been located on page yet
        :param locator: tuple of By.TYPE and search string
        :return: Boolean telling if element is located or not
        """
        try:
            print('Waiting (' + str(c) + ') for %s' % locator)
            element = self.driver.find_element(*locator)
            return True
        except Exception as e:
            return False

    # TODO: This function may be removed later on
    def _is_element_present(self, *locator):
        self.driver.implicitly_wait(0)
        try:
            self.driver.find_element(*locator)
            print('Element is present %s' % locator)
            return True
        except NoSuchElementException:
            print('Element is not present %s' % locator)
            return False
        finally:
            self.driver.implicitly_wait(self._implicit_wait)

if __name__ == "__main__":
    sw = StudentWeb()
    r = sw.get_results()
    for result in r:
        print('%-8s\t%-40s\t%s' % result)



