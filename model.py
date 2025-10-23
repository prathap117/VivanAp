import streamlit as st
import speech_recognition as sr
import ollama  # Using Ollama for local model inference


def calculate_tax_liability(gti, deductions):
    taxable_income_old = gti - sum(deductions.values())
    taxable_income_new = gti  # No deductions in the new regime
    
    # Old Regime Tax Calculation
    old_tax = (
        (0 if taxable_income_old <= 250000 else 
         0.05 * min(taxable_income_old - 250000, 250000)) +
        0.2 * min(max(taxable_income_old - 500000, 0), 500000) +
        0.3 * max(taxable_income_old - 1000000, 0)
    )
    
    # New Regime Tax Calculation
    new_tax = (
        (0 if taxable_income_new <= 300000 else 
         0.05 * min(taxable_income_new - 300000, 300000)) +
        0.1 * min(max(taxable_income_new - 600000, 0), 300000) +
        0.15 * min(max(taxable_income_new - 900000, 0), 300000) +
        0.2 * min(max(taxable_income_new - 1200000, 0), 300000) +
        0.3 * max(taxable_income_new - 1500000, 0)
    )
    
    # Add 4% Cess
    old_total_tax = old_tax + (0.04 * old_tax)
    new_total_tax = new_tax + (0.04 * new_tax)
    
    return old_total_tax, new_total_tax

def get_local_model_response(prompt):
    try:
        response = ollama.generate(model="mistral", prompt=prompt)
        print("Raw Response:", response)  # Debugging line
        return response["response"] if "response" in response else "Could not generate a response."
    except ollama._types.ResponseError as e:
        print(f"Error: {e}")
        return f"Ollama Error: {e}"


def main():
    st.set_page_config(page_title="Tax Assistant Chatbot", layout="wide")
    st.title("Tax Assistant Chatbot")
    st.write("Get ITR recommendations and tax-saving investment suggestions.")
    
    with st.sidebar:
        st.header("Enter Your Income Details")
        language = st.selectbox("Select Language", ["English", "Hindi", "Spanish", "French"])
        salary = st.number_input("Salary/Pension Income (₹)", min_value=0, step=1000)
        rental = st.number_input("Rental Income (₹)", min_value=0, step=1000)
        business = st.number_input("Business/Professional Income (₹)", min_value=0, step=1000)
        presumptive = st.number_input("Presumptive Income (₹)", min_value=0, step=1000)
        capital = st.number_input("Capital Gains (₹)", min_value=0, step=1000)
        foreign = st.number_input("Foreign Income (₹)", min_value=0, step=1000)
        crypto = st.number_input("Crypto Income (₹)", min_value=0, step=1000)
        directorship = st.radio("Are you a director in a company?", ["Yes", "No"])
        equity_shares = st.radio("Do you hold unlisted equity shares?", ["Yes", "No"])
        entity_type = st.selectbox("Select Entity Type", ["Individual", "Firm", "Company"])
        section_11_exemption = st.radio("Section 11 Exemption (for Trusts)?", ["Yes", "No"])
        special_filing = st.radio("Special Filing (Sec 139(4A), 139(4B), etc.)?", ["Yes", "No"])
        
        gti = salary + rental + business + presumptive + capital + foreign + crypto
        st.write(f"Calculated Gross Total Income (GTI): ₹{gti:,.2f}")
        
        deductions = {
            "80C (PPF, ELSS, etc.)": st.number_input("80C Deductions", min_value=0, value=150000),
            "80D (Health Insurance)": st.number_input("80D Deductions", min_value=0, value=50000),
            "Home Loan Interest (Sec 24B)": st.number_input("Home Loan Interest", min_value=0, value=200000)
        }
        
        ai_response = "Enter your income details and click 'Calculate Tax Liability' to get recommendations."

        if st.button("Calculate Tax Liability"):
            old_tax, new_tax = calculate_tax_liability(gti, deductions)
            st.write(f"Old Regime Tax: ₹{old_tax:,.2f}")
            st.write(f"New Regime Tax: ₹{new_tax:,.2f}")
            better_regime = "Old" if old_tax < new_tax else "New"
            st.success(f"Recommended Regime: {better_regime} Tax Regime")
            
            # Generate AI-based recommendation
            ai_prompt = (
                f"User's Gross Total Income: ₹{gti:,.2f}.\n"
                f"Old Regime Tax: ₹{old_tax:,.2f}, New Regime Tax: ₹{new_tax:,.2f}.\n"
                "Recommend the appropriate ITR form and suggest tax-saving investments.Generate in the form of table like professinal with minimal words but informative. And also give another table consisting of new tax regime and old tax regime with respect to given inputs. Also another table with tax polices like 80C, 80D, 80E etc. with actual numbers and how much percentage will be saved also give gti."
            )
            
            ai_response = get_local_model_response(ai_prompt)
    
    st.subheader("AI Recommendation")
    st.write(ai_response)
    
    st.subheader("Ask Your Queries")
    query_text = st.text_input("Type your question here:")
    if st.button("Ask via Text"):
        if query_text:
            query_response = get_local_model_response(query_text)
            st.write("### Answer:")
            st.write(query_response)

if __name__ == "__main__":
    main()
