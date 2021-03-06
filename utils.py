import time
import os
import sys

from lookup_dict import lookup_dict

def get_command_line_arguments(input_argument_list):
    # get company name
    if len(input_argument_list) >= 2 and input_argument_list[1] not in lookup_dict.keys():
        print(input_argument_list[1], "not in DB.")
        print("2nd argument should be company name. It should also be in DB.")
        sys.exit()
    company = input_argument_list[1]
    current_company = lookup_dict[company]

    # defaults to send 10 invitation
    invitation_count = 10
    if len(input_argument_list) >= 3:
        try:
            invitation_count = int(input_argument_list[2])
        except ValueError:
            print("3rd argument should be integer. Now setting invitation_count to 10.")

    # defaults to scroll 10 times
    scroll_times = 10
    if len(input_argument_list) >= 4:
        try:
            scroll_times = int(input_argument_list[3])
        except ValueError:
            print("4th argument should be integer. Now setting scroll_times to 10.")

    return current_company, invitation_count, scroll_times

def signin_to_linkedin(driver):
    # Open LinkedIn 
    driver.get('https://www.linkedin.com/')

    # Load and WAIT for 3 seconds 
    time.sleep(3)

    # click 'signin'
    driver.find_element_by_xpath('/html/body/nav/a[3]').click()

    input_email = 'xxx'
    input_password = 'xxx'
    
    # //*[@id="username"]
    try:
        time.sleep(3)

        # Find the email or username input  
        email = driver.find_element_by_xpath("/html/body/div/main/div[2]/form/div[1]/input")

        # Find password input 
        password = driver.find_element_by_xpath("/html/body/div/main/div[2]/form/div[2]/input")


        # Set your login Credentials  
        email.send_keys(input_email)
        password.send_keys(input_password)

        time.sleep(3)

        # Find and Click upon the Login Button
        try: 
            driver.find_element_by_xpath('/html/body/div/main/div[2]/form/div[3]/button').click()
        except Exception as e:
            driver.find_element_by_xpath('/html/body/div/main/div[2]/form/div[4]/button').click()

    # different login page
    except Exception as e:

        # click sign-in button
        driver.find_element_by_class_name("nav__button-secondary").click()

        # Find the email or username input 
        email = driver.find_element_by_id("username")

        # Find password input 
        password = driver.find_element_by_id("password")

        # Set your login Credentials  
        email.send_keys(input_email)
        password.send_keys(input_password)

        time.sleep(1)

        # Find and Click upon the Login Button 
        driver.find_element_by_class_name('btn__primary--large').click()
    
    # Logging In happens here and wait 
    time.sleep(10)

def get_a_person_to_connect(already_connected_list, 
                            file, driver, scroll_times, 
                            keywords_in_status_list = ['hiring', 'recruiting', \
                                    'technical recruiter', \
                                    'data engineering manager'], 
                            stopwords_in_status_list = ['hiring product manager', \
                                        'hiring product design', 'design hiring', \
                                        'hiring android', 'hiring specialist', \
                                        'business']
                            ):
        
        someone_to_connect = []
        scroll_amount = 0

        time.sleep(10)
        
        
        # run this loop until at least 1 person is found
        while not someone_to_connect and scroll_times:
            scroll_times -= 1
            
            a = driver.find_elements_by_xpath('//*[@class="org-people-profiles-module ember-view"]/ul/li')

            for a_link in a:
                if a_link.text.endswith('Connect') and \
                    any(kw in a_link.text.lower() for kw in keywords_in_status_list) and \
                    not any(kw in a_link.text.lower() for kw in stopwords_in_status_list):
                    full_name = a_link.text.split("\n")[0].strip('.')
                    if full_name not in already_connected_list:
                        someone_to_connect.append(a_link)
                        break

            # scroll a bit
            if not someone_to_connect:
                print("Scrolling!")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(10)
        return someone_to_connect

def send_invitations(current_company, invitation_count, scroll_times, driver):

    my_message, url, file = current_company['my_message'], current_company['url'], current_company['file']

    if not os.path.exists(file): 
        print(file, " doesn't exist. Creating one.")
        with open(file, 'w'): pass
    already_connected_list = [line.strip() for line in open(file, 'r')]
    someone_to_connect = get_a_person_to_connect(already_connected_list, file, \
                                        driver, scroll_times, \
                                        current_company['keywords_in_status_list'], \
                                        current_company['stopwords_in_status_list'])

    while someone_to_connect and invitation_count:
        invitation_count -= 1
        a_link = someone_to_connect[0]
        hiring_person = a_link.text.split("\n")[0].strip('.').split()[0]
        full_name = a_link.text.split("\n")[0].strip('.')
        print("Connecting to ", full_name)

        time.sleep(5)
        # click connect
        print("Click connect button!")
        try:
            a_link.find_element_by_xpath('.//button').click()
        except Exception as e:
            # auto scroll to element
            driver.execute_script("arguments[0].scrollIntoView();", a_link)
            time.sleep(3)
            a_link.find_element_by_xpath('.//button').click()

        time.sleep(5)

        # add note
        print("Click add note")

        # try:
        #     driver.find_element_by_xpath('//button[@class="button-secondary-large mr1"]').click()
        # except:
        #     driver.find_element_by_xpath('//button[@class="artdeco-button artdeco-button--secondary artdeco-button--3 mr1"]').click()
        time.sleep(3)

        # write message
        print("Adding in my message")
        inputElement = driver.find_element_by_xpath('/html/body/div[4]/div/div/div[2]/div[1]/textarea')
        message = "Hi " + hiring_person + my_message
        inputElement.send_keys(message)
        time.sleep(1)

        # send invitation
        print("Click send invitation")
        try:
            driver.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]/span"]').click()
        except:
            driver.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]').click()
        already_connected_list.append(full_name)

        # refresh the page
        time.sleep(5)
#         driver.get("https://www.linkedin.com/company/uber-com/people/?keywords=hiring")
#         time.sleep(15)
#         a = driver.find_elements_by_xpath('//*[@class="org-people-profiles-module ember-view"]/ul/li')

        # invitation sent list is put to uber.txt
        with open(file, 'w') as f:
            for item in set(already_connected_list):
                f.write("%s\n" % item)

        someone_to_connect = get_a_person_to_connect(already_connected_list, file, driver, \
                                                    scroll_times, \
                                                    current_company['keywords_in_status_list'], \
                                                    current_company['stopwords_in_status_list'])
        print("-"*45)
    return invitation_count