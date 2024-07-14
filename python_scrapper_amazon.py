# Importing all the necessory libraries and packages

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import csv
import time

# Function to search for a product name on the website
def search_product(driver, product_name):
    try:
        search_box = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'twotabsearchtextbox')))
        search_box.clear()
        search_box.send_keys(product_name, Keys.ENTER)
    except Exception as e:
        print(f"Error during search for product {product_name}: {e}")
        return False
    return True

# Function to extract reviews for a product
def extract_reviews(driver, product_name):
    reviews = []

    try:
        # Wait for the search results to load and click on the first product link
        first_product_link = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[3]/div/div/span/div/div/div/div[2]/div/div/div[1]/h2/a')))
        href_value = first_product_link.get_attribute("href")
        driver.get(href_value)

        # Wait for the product page to load and scroll to the reviews section
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'reviewsMedley')))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Click on the "See all reviews" button if available
        see_all_reviews_button_clicked = False
        try_count = 0
        while not see_all_reviews_button_clicked and try_count < 3:
            try:
                see_all_reviews_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@data-hook="see-all-reviews-link-foot"]')))
                see_all_reviews_button.click()
                see_all_reviews_button_clicked = True
            except Exception as e:
                print(f"Error clicking 'See all reviews' button, attempt {try_count + 1}: {e}")
                try_count += 1
                time.sleep(2)

        if not see_all_reviews_button_clicked:
            print(f"Failed to click 'See all reviews' button after {try_count} attempts")
            return reviews

        # Extract the reviews
        while True:
            review_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-hook="review"]')))
            for review_element in review_elements:
                try:
                    review_date = review_element.find_element(By.XPATH, './/span[@data-hook="review-date"]').text
                    review_text = review_element.find_element(By.XPATH, './/span[@data-hook="review-body"]').text
                    
                    # Modify the XPath to extract the rating text
                    review_rating_element = review_element.find_element(By.XPATH, './/i[contains(@class, "a-icon-star")]/span')
                    review_rating = review_rating_element.get_attribute("innerHTML").split()[0]  # Extract the numerical rating
                                        
                    reviews.append({
                        "Product Name": product_name,
                        "Review Date": review_date,
                        "Review Text": review_text,
                        "Review Rating": review_rating
                    })
                except Exception as e:
                    print(f"Error occurred while extracting review: {e}")

            # Check if there is a next page of reviews
            try:
                next_page_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//li[@class="a-last"]/a')))
                next_page_button.click()
                time.sleep(2)  # Wait for the next page to load
            except:
                break  # No more pages of reviews
    except Exception as e:
        print(f"Error occurred while extracting reviews for product {product_name}: {e}")

    return reviews

# Function to write reviews to a CSV file
def write_to_csv(reviews, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Product Name", "Review Date", "Review Text", "Review Rating"])
        writer.writeheader()
        writer.writerows(reviews)

# Main function
def main():
    # Define the input and output file paths
    input_file = 'products_raw_test.csv'
    output_file = 'intel_product_reviews.csv'

    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(options=options)

    # Navigate to the website
    driver.get("https://www.amazon.in/")  # Replace with the actual website URL

    # Read product names from CSV file
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header rsow
        reviews_all = []
        for row in reader:
            product_name = row[0]

            # Search for the product
            if not search_product(driver, product_name):
                continue  # Move to the next product if the search fails

            # Extract reviews for the product
            reviews = extract_reviews(driver, product_name)
            reviews_all.extend(reviews)

    # Write reviews to CSV file
    write_to_csv(reviews_all, output_file)

    # Close the WebDriver session
    driver.quit()

if __name__ == "__main__":
    main()
