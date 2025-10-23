import streamlit as st
import speech_recognition as sr
import google.generativeai as genai

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

def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text if response else "Could not generate a response."

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
        
        # Checkbox for Defense Personnel
        is_defense = st.checkbox("Are you a Defense Personnel?")
        
        deductions = {
            "80C (PPF, ELSS, etc.)": st.number_input("80C Deductions", min_value=0, value=150000),
            "80D (Health Insurance)": st.number_input("80D Deductions", min_value=0, value=50000),
            "Home Loan Interest (Sec 24B)": st.number_input("Home Loan Interest", min_value=0, value=200000)
        }

        # Additional deductions for Defense Personnel
        if is_defense:
            deductions["Gallantry Award Exemption"] = st.number_input("Gallantry Award Exemption (₹)", min_value=0, value=0)
            deductions["Disability Pension Exemption"] = st.number_input("Disability Pension Exemption (₹)", min_value=0, value=0)
    
    gti = salary + rental + business + presumptive + capital + foreign + crypto
    st.subheader("Income and Tax Liability")
    st.write(f"Calculated Gross Total Income (GTI): ₹{gti:,.2f}")
    
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
    "Recommend the appropriate ITR form and suggest tax-saving investments.\n"
    "Generate structured tables with the following details:\n\n"
    
    "1. **Tax Saving Investments Table**\n"
    "| Tax Category | Investment Options | Maximum Limit | Benefits | Special Conditions |\n"
    "|-------------|--------------------|---------------|----------|--------------------|\n"
    "(Fill with applicable tax-saving options)\n\n"
    
    "2. **Old vs New Tax Regime Comparison**\n"
    "| Income Slab | Old Regime Tax (₹) | New Regime Tax (₹) | Difference (₹) | Recommendation |\n"
    "|------------|------------------|------------------|----------------|---------------|\n"
    "(Fill with computed values based on user input)\n\n"
    
    "3. **Tax Deductions Analysis**\n"
    "| Deduction Type | Section | Amount (₹) | Percentage Saved | Impact on Tax |\n"
    "|---------------|---------|------------|----------------|---------------|\n"
    "(Include 80C, 80D, 80E, etc., with actual savings impact)\n\n"
    
    "4. **Final Tax Savings Strategies**\n"
    "| Strategy | Estimated Savings (₹) | Additional Benefits | Applicability |\n"
    "|---------|--------------------|------------------|---------------|\n"
    "(Provide personalized tax-saving strategies based on computed data)\n"
    
    "Ensure the data is based on actual calculations rather than assumptions. Keep the response concise, professional, and informative."
)

        ai_response = get_gemini_response(ai_prompt)
        
        st.subheader("AI Recommendation")
        st.write(ai_response)
    
    st.subheader("Ask Your Queries")
    query_text = st.text_input("Type your question here:")
    if st.button("Ask via Text"):
        if query_text:
            query_response = get_gemini_response(query_text)
            st.write("### Answer:")
            st.write(query_response)

if __name__ == "__main__":
    main()
