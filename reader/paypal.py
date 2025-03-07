import requests
import json
from .models import Subscription

def get_access_token():
    data={
        'grant_type': "client_credentials",
    }
    headers={
        'Accept':'application/json',
        'Accept-Language':'en_US',
    }
    client_id="AXSnZGWecd9YWYINcPRPPGegSAM2Hc-cLt-yUc38jq6lqBNnAxo0E5Gwf_N3udPQqsByEuIHvvG-UjVd"
    secret_id="EADl16zsqNmh35VeYpdW9jH_rHtE1Mkftql3OIYa-NrvwuT4Wt7jIeMMlEoulFYGy8-s-0vEYKs0VUmO"
    url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    r=requests.post(url,auth=(client_id,secret_id),headers=headers,data=data).json()
    access_token=r['access_token']
    return access_token

def cancel_subscription(access_token,subId):
    bearer_token = f"Bearer {access_token}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token,
    }
    url='https://api.sandbox.paypal.com/v1/billing/subscriptions/'+subId+'/cancel'
    r=requests.post(url, headers=headers)
    print(r.status_code)

def get_subscription_details(access_token, subId):
    bearer_token = f"Bearer {access_token}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token,
    }
    url='https://api.sandbox.paypal.com/v1/billing/subscriptions/'+subId
    r=requests.get(url, headers=headers)
    response=r.json()
    if r.status_code == 200:
        return response
    else:
        return None

def update_subscription_plan(access_token, subId):
    bearer_token = f"Bearer {access_token}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token,
    }
    subDetails=Subscription.objects.get(paypal_subscription_id=subId)
    current_plan=subDetails.subscription_plan
    if current_plan == "Standard":
        new_plan_id="P-2EA74263YC2500708M6KPIXI"
    elif current_plan == "Premium":
        new_plan_id="P-38363656RR1276033M6KPIII"
    url='https://api.sandbox.paypal.com/v1/billing/subscriptions/'+subId+'/revise'
    data={
        "plan_id": new_plan_id
    }
    r=requests.post(url, headers=headers,data=json.dumps(data))
    response=r.json()
    for link in response['links']:
        if link['rel'] == 'approve':
            approval_url = link['href']
    if r.status_code == 200:
        return approval_url
    print(response)

def update_current_subscription_plan(access_token, subId):
    bearer_token = f"Bearer {access_token}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token,
    }
    subDetails=Subscription.objects.get(paypal_subscription_id=subId)
    current_plan=subDetails.subscription_plan
    if current_plan == "Standard":
        new_plan_id="P-38363656RR1276033M6KPIII"
    elif current_plan == "Premium":
        new_plan_id="P-2EA74263YC2500708M6KPIXI"
    url='https://api.sandbox.paypal.com/v1/billing/subscriptions/'+subId+'/revise'
    data={
        "plan_id": new_plan_id
    }
    r=requests.post(url, headers=headers,data=json.dumps(data))
    response=r.json()
    for link in response['links']:
        if link['rel'] == 'approve':
            approval_url = link['href']
    if r.status_code == 200:
        return approval_url
    print(response)
