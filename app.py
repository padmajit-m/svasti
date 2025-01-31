import streamlit as st
import requests
import random

# API Endpoints
TOKEN_URL = "https://dashboardui.sandbox.kalfin.in/kaleidofin-auth/oauth/token"
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
        files = {"documents": document_file.getvalue() if document_file else None}
        response = requests.post(url, headers=headers, files=files)
        st.json(response.json())
