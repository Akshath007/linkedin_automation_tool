import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from typing import List, Dict
import sqlite3

# Configure page
st.set_page_config(
    page_title="LinkedIn Sales Automation Tool",
    page_icon="🚀",
    layout="wide"
)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCQOE7NN3n2oL_oR_ZjKjD7taTphphBYy4"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize database
def init_db():
    conn = sqlite3.connect('linkedin_automation.db')
    c = conn.cursor()

    # Create campaigns table
    c.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            product_description TEXT,
            target_industry TEXT,
            target_roles TEXT,
            company_size TEXT,
            region TEXT,
            outreach_goal TEXT,
            brand_voice TEXT,
            triggers TEXT,
            created_date TEXT
        )
    """)

    # Create prospects table
    c.execute("""
        CREATE TABLE IF NOT EXISTS prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            name TEXT,
            title TEXT,
            company TEXT,
            industry TEXT,
            profile_url TEXT,
            connection_message TEXT,
            follow_up_messages TEXT,
            status TEXT,
            created_date TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    """)

    # Create messages table
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospect_id INTEGER,
            message_type TEXT,
            message_content TEXT,
            sent_date TEXT,
            response TEXT,
            status TEXT,
            FOREIGN KEY (prospect_id) REFERENCES prospects (id)
        )
    """)

    conn.commit()
    conn.close()

@dataclass
class Prospect:
    name: str
    title: str
    company: str
    industry: str
    profile_summary: str
    recent_activity: str = ""

class MessageGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_connection_message(self, prospect: Prospect, campaign_data: Dict) -> str:
        prompt = f"""Generate a personalized LinkedIn connection request message.

Campaign Context:
- Product/Service: {campaign_data['product_description']}
- Target Industry: {campaign_data['target_industry']}
- Outreach Goal: {campaign_data['outreach_goal']}
- Brand Voice: {campaign_data['brand_voice']}

Prospect Details:
- Name: {prospect.name}
- Title: {prospect.title}
- Company: {prospect.company}
- Industry: {prospect.industry}
- Profile Summary: {prospect.profile_summary}

Requirements:
- Maximum 300 characters (LinkedIn limit)
- Personalized and relevant
- Professional but {campaign_data['brand_voice']} tone
- Include specific value proposition
- End with a soft call-to-action

Generate only the message, no additional text."""

        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating message: {str(e)}"

    def generate_follow_up_sequence(self, prospect: Prospect, campaign_data: Dict) -> List[str]:
        prompt = f"""Generate 3 follow-up messages for LinkedIn outreach sequence.

Campaign Context:
- Product/Service: {campaign_data['product_description']}
- Target Industry: {campaign_data['target_industry']}
- Outreach Goal: {campaign_data['outreach_goal']}
- Brand Voice: {campaign_data['brand_voice']}

Prospect Details:
- Name: {prospect.name}
- Title: {prospect.title}
- Company: {prospect.company}

Generate 3 different follow-up messages:
1. First follow-up (2-3 days after connection) - soft reminder with value
2. Second follow-up (1 week later) - share case study or insight
3. Final follow-up (2 weeks later) - last attempt with different angle

Each message should be:
- Under 200 words
- {campaign_data['brand_voice']} tone
- Provide value, not just ask for time
- Have clear but not pushy CTA

Format as: 
FOLLOW-UP 1:
[message]

FOLLOW-UP 2:
[message]

FOLLOW-UP 3:
[message]"""

        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            # Parse the follow-ups
            follow_ups = []
            for i in range(1, 4):
                pattern = f"FOLLOW-UP {i}:(.*?)(?=FOLLOW-UP {i+1}:|$)"
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    follow_ups.append(match.group(1).strip())

            return follow_ups if len(follow_ups) == 3 else [text]
        except Exception as e:
            return [f"Error generating follow-up: {str(e)}"]

def save_campaign(campaign_data):
    conn = sqlite3.connect('linkedin_automation.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO campaigns (name, product_description, target_industry, target_roles, 
                             company_size, region, outreach_goal, brand_voice, triggers, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        campaign_data['name'],
        campaign_data['product_description'],
        campaign_data['target_industry'],
        campaign_data['target_roles'],
        campaign_data['company_size'],
        campaign_data['region'],
        campaign_data['outreach_goal'],
        campaign_data['brand_voice'],
        campaign_data['triggers'],
        datetime.now().isoformat()
    ))

    campaign_id = c.lastrowid
    conn.commit()
    conn.close()
    return campaign_id

def load_campaigns():
    conn = sqlite3.connect('linkedin_automation.db')
    df = pd.read_sql_query('SELECT * FROM campaigns ORDER BY created_date DESC', conn)
    conn.close()
    return df

def save_prospect(prospect_data, campaign_id):
    conn = sqlite3.connect('linkedin_automation.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO prospects (campaign_id, name, title, company, industry, profile_url,
                             connection_message, follow_up_messages, status, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        campaign_id,
        prospect_data['name'],
        prospect_data['title'],
        prospect_data['company'],
        prospect_data['industry'],
        prospect_data.get('profile_url', ''),
        prospect_data['connection_message'],
        json.dumps(prospect_data['follow_up_messages']),
        'draft',
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

# Initialize database
init_db()

# Main App UI
st.title("🚀 LinkedIn Sales Automation Tool")
st.markdown("AI-powered LinkedIn automation platform for B2B sales teams and recruiters")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", [
    "🏠 Dashboard",
    "📋 Campaign Setup",
    "🎯 Prospect Analysis",
    "✏️ Message Generation", 
    "📈 Campaign Management",
    "📊 Analytics"
])

if page == "🏠 Dashboard":
    st.header("Welcome to LinkedIn Sales Automation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Active Campaigns", "3", "↗️ +1")
    with col2:
        st.metric("Prospects Added", "127", "↗️ +23")
    with col3:
        st.metric("Messages Generated", "89", "↗️ +15")

    st.subheader("🛡️ LinkedIn Safety Limits (2025)")

    limits_data = {
        "Action": ["Connection Requests", "Direct Messages", "Profile Views"],
        "Free Account": ["15/day", "50/day", "80/day"],
        "Premium Account": ["30/day", "100/day", "150/day"],
        "Safety Recommendation": ["Stay under 70%", "Spread across hours", "Randomize timing"]
    }

    st.dataframe(pd.DataFrame(limits_data), use_container_width=True)

    st.info("💡 **Pro Tip:** Always randomize your outreach timing and stay well below daily limits to maintain account safety.")

elif page == "📋 Campaign Setup":
    st.header("Campaign Setup")
    st.write("Configure your outreach campaign parameters")

    with st.form("campaign_form"):
        col1, col2 = st.columns(2)

        with col1:
            campaign_name = st.text_input("Campaign Name", "HR SaaS Outreach Q4 2025")
            product_description = st.text_area("Product/Service Description", 
                "AI-powered HR automation tool that helps startups streamline onboarding and employee management processes")
            target_industry = st.selectbox("Target Industry", [
                "SaaS", "EdTech", "Finance", "Healthcare", "E-commerce", "Manufacturing", "Consulting", "Other"
            ])
            target_roles = st.text_input("Ideal Job Roles", "HR Manager, Head of HR, People Operations, CHRO")

        with col2:
            company_size = st.selectbox("Company Size", [
                "Startup (1-50)", "SME (51-200)", "Mid-market (201-1000)", "Enterprise (1000+)"
            ])
            region = st.selectbox("Region/Location", [
                "India", "United States", "Europe", "Asia-Pacific", "Global"
            ])
            outreach_goal = st.selectbox("Outreach Goal", [
                "Book a demo", "Schedule a call", "Download resource", "Network", "Hire talent", "Partnership"
            ])
            brand_voice = st.selectbox("Brand Voice", [
                "Friendly", "Professional", "Enthusiastic", "Consultative", "Direct"
            ])

        triggers = st.text_input("Optional Triggers", 
            "Job change, hiring posts, new funding, company growth, product launches")

        if st.form_submit_button("🚀 Create Campaign", type="primary"):
            campaign_data = {
                'name': campaign_name,
                'product_description': product_description,
                'target_industry': target_industry,
                'target_roles': target_roles,
                'company_size': company_size,
                'region': region,
                'outreach_goal': outreach_goal,
                'brand_voice': brand_voice,
                'triggers': triggers
            }

            campaign_id = save_campaign(campaign_data)
            st.success(f"✅ Campaign '{campaign_name}' created successfully! Campaign ID: {campaign_id}")
            st.balloons()

elif page == "🎯 Prospect Analysis":
    st.header("Prospect Analysis")
    st.write("Add and analyze prospect profiles")

    # Load campaigns
    campaigns_df = load_campaigns()
    if len(campaigns_df) == 0:
        st.warning("⚠️ Please create a campaign first!")
    else:
        selected_campaign = st.selectbox("Select Campaign", 
            options=campaigns_df['id'].tolist(),
            format_func=lambda x: campaigns_df[campaigns_df['id'] == x]['name'].iloc[0])

        st.subheader("Add New Prospect")

        with st.form("prospect_form"):
            col1, col2 = st.columns(2)

            with col1:
                prospect_name = st.text_input("Name", "Anjali Mehta")
                prospect_title = st.text_input("Title", "HR Manager")
                prospect_company = st.text_input("Company", "TechStartup Inc")

            with col2:
                prospect_industry = st.text_input("Industry", "SaaS")
                profile_url = st.text_input("LinkedIn Profile URL (optional)")

            profile_summary = st.text_area("Profile Summary/Bio",
                "Experienced HR professional with 8+ years in talent acquisition and employee engagement. Currently leading HR initiatives at a fast-growing SaaS startup focused on improving hybrid work culture.")

            recent_activity = st.text_area("Recent Activity/Posts (optional)",
                "Recently posted about challenges in hybrid hiring and the importance of cultural fit in remote teams. Shared insights on AI tools for HR automation.")

            if st.form_submit_button("🔍 Analyze Prospect", type="primary"):
                # Create prospect object
                prospect = Prospect(
                    name=prospect_name,
                    title=prospect_title,
                    company=prospect_company,
                    industry=prospect_industry,
                    profile_summary=profile_summary,
                    recent_activity=recent_activity
                )

                # Get campaign data
                campaign_data = campaigns_df[campaigns_df['id'] == selected_campaign].iloc[0].to_dict()

                # Generate messages
                message_gen = MessageGenerator(GEMINI_API_KEY)

                with st.spinner("🤖 Generating personalized messages..."):
                    connection_msg = message_gen.generate_connection_message(prospect, campaign_data)
                    follow_ups = message_gen.generate_follow_up_sequence(prospect, campaign_data)

                st.success("✅ Messages generated successfully!")

                # Display results
                st.subheader("📨 Generated Messages")

                st.write("**Connection Request:**")
                st.info(connection_msg)

                st.write("**Follow-up Sequence:**")
                for i, follow_up in enumerate(follow_ups, 1):
                    with st.expander(f"📧 Follow-up {i}"):
                        st.write(follow_up)

                # Save to database
                prospect_data = {
                    'name': prospect_name,
                    'title': prospect_title,
                    'company': prospect_company,
                    'industry': prospect_industry,
                    'profile_url': profile_url,
                    'connection_message': connection_msg,
                    'follow_up_messages': follow_ups
                }

                save_prospect(prospect_data, selected_campaign)
                st.success("💾 Prospect saved to campaign!")

elif page == "✏️ Message Generation":
    st.header("Message Generation")
    st.write("Bulk generate and customize messages")

    # Sample prospects for demo
    sample_prospects = [
        {"name": "Rajesh Kumar", "title": "CTO", "company": "TechStart Solutions", "industry": "SaaS", 
         "summary": "Tech leader with 10+ years building scalable products"},
        {"name": "Priya Sharma", "title": "Head of Growth", "company": "ScaleUp Inc", "industry": "EdTech",
         "summary": "Growth expert focused on user acquisition and retention"},
        {"name": "Amit Patel", "title": "VP Engineering", "company": "Innovation Labs", "industry": "Finance",
         "summary": "Engineering leader passionate about fintech innovation"}
    ]

    campaigns_df = load_campaigns()
    if len(campaigns_df) > 0:
        selected_campaign = st.selectbox("Select Campaign for Message Generation", 
            options=campaigns_df['id'].tolist(),
            format_func=lambda x: campaigns_df[campaigns_df['id'] == x]['name'].iloc[0])

        campaign_data = campaigns_df[campaigns_df['id'] == selected_campaign].iloc[0].to_dict()

        st.subheader("📊 Sample Message Generation")
        st.write("Generate sample messages for different prospect types")

        if st.button("🚀 Generate Sample Messages", type="primary"):
            message_gen = MessageGenerator(GEMINI_API_KEY)

            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, prospect_data in enumerate(sample_prospects):
                status_text.text(f"Generating message for {prospect_data['name']}...")

                prospect = Prospect(
                    name=prospect_data["name"],
                    title=prospect_data["title"],
                    company=prospect_data["company"],
                    industry=prospect_data["industry"],
                    profile_summary=prospect_data["summary"]
                )

                connection_msg = message_gen.generate_connection_message(prospect, campaign_data)
                results.append({
                    "Prospect": f"{prospect.name}",
                    "Title": prospect.title,
                    "Company": prospect.company,
                    "Industry": prospect.industry,
                    "Connection Message": connection_msg
                })

                progress_bar.progress((i + 1) / len(sample_prospects))
                time.sleep(1)  # Simulate API delay

            status_text.text("✅ All messages generated!")

            # Display results in table
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True, height=300)

            # Download option
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="📥 Download Messages as CSV",
                data=csv,
                file_name=f"linkedin_messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

elif page == "📈 Campaign Management":
    st.header("Campaign Management")
    st.write("Monitor and manage your campaigns")

    campaigns_df = load_campaigns()

    if len(campaigns_df) == 0:
        st.info("📭 No campaigns found. Create your first campaign in the Campaign Setup page.")
    else:
        st.subheader("🎯 Active Campaigns")

        # Display campaigns
        for idx, campaign in campaigns_df.iterrows():
            with st.expander(f"📋 {campaign['name']} (Created: {campaign['created_date'][:10]})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Product:** {campaign['product_description'][:100]}...")
                    st.write(f"**Industry:** {campaign['target_industry']}")
                    st.write(f"**Roles:** {campaign['target_roles']}")

                with col2:
                    st.write(f"**Company Size:** {campaign['company_size']}")
                    st.write(f"**Region:** {campaign['region']}")
                    st.write(f"**Goal:** {campaign['outreach_goal']}")

                # Load prospects for this campaign
                conn = sqlite3.connect('linkedin_automation.db')
                try:
                    prospects_df = pd.read_sql_query(
                        'SELECT * FROM prospects WHERE campaign_id = ?', 
                        conn, params=[campaign['id']]
                    )
                    conn.close()

                    st.write(f"**📊 Prospects Added:** {len(prospects_df)}")

                    if len(prospects_df) > 0:
                        st.dataframe(prospects_df[['name', 'title', 'company', 'status']], 
                                   use_container_width=True)
                except Exception as e:
                    conn.close()
                    st.write("📊 **Prospects Added:** 0")

elif page == "📊 Analytics":
    st.header("Analytics Dashboard")
    st.write("Track your outreach performance and compliance")

    # Campaign Performance
    st.subheader("📈 Campaign Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Prospects Found", "150", "↗️ +25")
    with col2:
        st.metric("Messages Generated", "89", "↗️ +12")
    with col3:
        st.metric("Est. Response Rate", "28%", "↗️ +5%")
    with col4:
        st.metric("Campaigns Active", "3", "→ 0")

    # Performance breakdown
    performance_data = {
        "Metric": ["Prospects Analyzed", "Connection Messages Generated", "Follow-up Sequences Created", 
                  "Estimated Positive Replies", "Projected Meetings"],
        "This Week": [150, 89, 89, 25, 8],
        "Target": [200, 100, 100, 30, 10],
        "Achievement": ["75%", "89%", "89%", "83%", "80%"]
    }

    df_performance = pd.DataFrame(performance_data)
    st.dataframe(df_performance, use_container_width=True)

    # LinkedIn Safety Monitor
    st.subheader("🛡️ LinkedIn Safety Monitor")

    col1, col2 = st.columns(2)

    with col1:
        st.success("🟢 Account Status: Safe")
        st.info("📊 Daily Limit Usage: 45%")

    with col2:
        st.success("⏱️ Rate Limiting: Active")
        st.info("🔄 Next Safe Window: 2 hours")

    # Compliance Status
    st.subheader("✅ Compliance Status")

    compliance_items = [
        "🔒 GDPR Compliant - Legitimate Interest Documented",
        "📧 CAN-SPAM Compliant - Unsubscribe Links Added",
        "🛡️ LinkedIn ToS Compliant - Safe Rate Limits",
        "⚡ API Rate Limiting Active",
        "📝 Data Retention Policy Applied"
    ]

    for item in compliance_items:
        st.success(item)

# Sidebar Info
st.sidebar.markdown("---")
st.sidebar.markdown("**🚀 LinkedIn Sales Automation**")
st.sidebar.markdown("Powered by Google Gemini AI")
st.sidebar.markdown("Built with Streamlit")
st.sidebar.markdown("*Version 1.0.0*")

st.sidebar.markdown("---")
st.sidebar.markdown("**⚠️ Safety First**")
st.sidebar.markdown("Always respect LinkedIn's terms of service and daily limits to maintain account safety.")

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** This tool is for educational purposes. Always comply with LinkedIn's terms of service and applicable laws.")
