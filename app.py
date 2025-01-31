import streamlit as st
import requests
import random

# API Endpoints
TOKEN_URL = "https://dashboardui.sandbox.kalfin.in/kaleidofin-auth/oauth/token"
KISCORE_API_URL = "https://dashboardui.sandbox.kalfin.in/kaleidofin-server/api/v2/services/creditAnalytics"
LOAN_CREATION_URL = "https://dashboardui.sandbox.kalfin.in/kaleidofin-server/api/v2/services/creditAnalytics"
DOCUMENT_UPLOAD_URL = "https://dashboardui.sandbox.kalfin.in/krediline-server/api/v1/partner/loanApplications/{loanApplicationId}/kycDocuments"

def generate_random_number(length=10):
    return str(random.randint(10**(length-1), 10**length - 1))

st.title("Loan API UI")

# Token Generation
st.subheader("Generate Token")
client_id = st.text_input("Client ID")
client_secret = st.text_input("Client Secret", type="password")
if st.button("Generate Token"):
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "read write"
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        st.session_state["token"] = token
        st.success("Token generated successfully!")
    else:
        st.error("Failed to generate token")

# Kiscore API Call
st.subheader("Kiscore API")
partner_id = st.text_input("Partner ID")
customer_id = st.text_input("Customer ID", generate_random_number(10))
loan_application_number = st.text_input("Loan Application Number", generate_random_number(18))
loan_applied_amt = st.number_input("Loan Applied Amount", value=100000)
loan_purpose = st.text_input("Loan Purpose", "Asset Purchase")
proposed_disbursement_date = st.text_input("Proposed Disbursement Date", "2025/01/03")

if st.button("Call Kiscore API"):
    if "token" not in st.session_state:
        st.error("Please generate a token first")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['token']}", "Content-Type": "application/json"}
        payload = {
            "partner_id": partner_id,
            "partner_type": "kcpl",
            "customer_id": customer_id,
            "current_loan_details": {
                "loan_application_number": loan_application_number,
                "loan_purpose": loan_purpose,
                "proposed_disbursement_date": proposed_disbursement_date,
                "loan_applied_amt": loan_applied_amt,
                "loan_cycle": 1,
                "product_type": "WEL",
                "repayment_frequency": "Monthly",
                "no_of_installments": 24,
                "interest_rate": "NaN",
                "instalment_amount": None,
                "loan_category": "WEL"
            }
        }
        response = requests.post(KISCORE_API_URL, json=payload, headers=headers)
        st.json(response.json())

# Loan Creation
st.subheader("Create Loan")
partnerCustomerId = st.text_input("Partner Customer ID", generate_random_number(10))
partnerLoanId = st.text_input("Partner Loan ID", generate_random_number(18))
groupId = st.text_input("Group ID", "G082350")
branchCode = st.text_input("Branch Code")
partnerId = st.text_input("Partner ID")

if st.button("Create Loan"):
    if "token" not in st.session_state:
        st.error("Please generate a token first")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['token']}", "Content-Type": "application/json"}
        payload = {
            "partner_id": partnerId,
            "partnerCustomerId": partnerCustomerId,
            "partnerLoanId": partnerLoanId,
            "groupId": groupId
        }
        response = requests.post(LOAN_CREATION_URL, json=payload, headers=headers)
        st.json(response.json())

# Document Upload
st.subheader("Upload Loan Document")
loanApplicationId = st.text_input("Loan Application ID")
document_file = st.file_uploader("Upload Document")
if st.button("Upload Document"):
    if "token" not in st.session_state:
        st.error("Please generate a token first")
    else:
        url = DOCUMENT_UPLOAD_URL.format(loanApplicationId=loanApplicationId)
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        files = {"documents": (document_file.name, document_file.getvalue())} if document_file else None
        response = requests.post(url, headers=headers, files=files)
        st.json(response.json())
