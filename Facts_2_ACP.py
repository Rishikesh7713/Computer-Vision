import requests

url="https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"

def get_random_technology_fact():
    response=requests.get(url)
    if response.status_code==200:
        fact_data=response.json()
        print(f"Did you know? {fact_data['text']}")
    else:
        print("Failed to Fetch Fact")

while True:
    user_inp=input("Press Enter to get a random technology fact or type 'q' to quit....")
    if user_inp.lower()=='q':
        break
    get_random_technology_fact()