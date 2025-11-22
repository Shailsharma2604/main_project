"""
Streamlit UI for Asset Allocation Planner
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
from typing import cast

# Import our engine module
from asset_allocation_engine import (
    AssetAllocationEngine,
    RiskProfile,
    UserProfile,
    AssetAllocationPlan,
    estimate_corpus_at_retirement,
    format_inr,
    get_equity_allocation_from_risk_profile,
    get_risk_profile_from_age,
)

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST STREAMLIT COMMAND
# ============================================================================

st.set_page_config(
    page_title="Asset Allocation Planner",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Asset Allocation Planner"},
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

st.markdown(
    """
    <style>
    /* Main content area */
    .main {
        padding: 0rem 1rem;
    }

    /* Alert boxes */
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }

    /* Headers */
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
        font-weight: 700;
    }
    h2 {
        color: #2c3e50;
        padding-top: 1rem;
        font-weight: 600;
    }
    h3 {
        color: #34495e;
        font-weight: 600;
    }

    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
        font-weight: 600;
    }

    /* Buttons */
    .stButton > button {
        font-weight: 600;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Form submit button */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
    }

    /* Sidebar */
    .css-1d391kg {
        padding-top: 2rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Custom info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    /* Welcome icon */
    .welcome-icon {
        text-align: center;
        padding: 2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# CHART CREATION FUNCTIONS
# ============================================================================


def create_donut_chart(
    equity_pct: float, debt_pct: float, title: str = "Asset Allocation"
) -> go.Figure:
    """Create beautiful equity-debt split donut chart"""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Equity", "Debt"],
                values=[equity_pct, debt_pct],
                hole=0.6,
                marker=dict(
                    colors=["#667eea", "#764ba2"], line=dict(color="white", width=2)
                ),
                textposition="outside",
                textinfo="label+percent",
                textfont=dict(size=14, color="#2c3e50", family="Arial, sans-serif"),
                hovertemplate="<b>%{label}</b><br>%{percent}<br><extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=title, x=0.5, xanchor="center", font=dict(size=16, color="#2c3e50")
        ),
        showlegend=False,
        height=400,
        margin=dict(t=60, b=40, l=40, r=40),
        annotations=[
            dict(
                text=f'<b style="font-size:28px">{equity_pct:.0f}%</b><br><span style="font-size:16px">Equity</span>',
                x=0.5,
                y=0.5,
                font=dict(size=14, color="#2c3e50"),
                showarrow=False,
            )
        ],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def create_allocation_breakdown_chart(allocations: dict, title: str) -> go.Figure:
    """Create detailed allocation breakdown pie chart"""
    labels = [alloc.subcategory for alloc in allocations.values()]
    values = [alloc.percentage for alloc in allocations.values()]

    # Use pleasant color palette
    colors = [
        "#667eea",
        "#764ba2",
        "#f093fb",
        "#4facfe",
        "#43e97b",
        "#fa709a",
        "#fee140",
        "#30cfd0",
    ]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=colors[: len(labels)], line=dict(color="white", width=2)
                ),
                textposition="auto",
                textinfo="label+percent",
                textfont=dict(size=12, family="Arial, sans-serif"),
                hovertemplate="<b>%{label}</b><br>%{percent} of portfolio<br><extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=title, x=0.5, xanchor="auto", font=dict(size=16, color="#2c3e50")
        ),
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        height=450,
        margin=dict(t=60, b=40, l=40, r=150),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def create_sip_bar_chart(
    sip_breakdown: dict, equity_allocs: dict, debt_allocs: dict
) -> go.Figure:
    """Create horizontal bar chart for SIP allocation"""
    funds = []
    amounts = []
    categories = []

    for fund, amount in sip_breakdown.items():
        alloc = equity_allocs.get(fund) or debt_allocs.get(fund)
        if alloc:
            funds.append(alloc.subcategory)
            amounts.append(amount)
            categories.append(alloc.category)

    df = pd.DataFrame(
        {"Fund": funds, "Amount": amounts, "Category": categories}
    ).sort_values("Amount", ascending=True)
    df["Amount_str"] = df["Amount"].apply(format_inr)
    fig = px.bar(
        df,
        x="Amount",
        y="Fund",
        color="Category",
        orientation="h",
        title="Monthly SIP Allocation by Fund",
        labels={"Amount": "Monthly SIP (₹)", "Fund": ""},
        color_discrete_map={"Equity": "#667eea", "Debt": "#764ba2"},
        text="Amount_str",
    )

    fig.update_traces(
        # texttemplate="₹%{text:,.0f}",
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>SIP: ₹%{x:,.0f}<extra></extra>",
        textfont=dict(size=12, family="Arial, sans-serif", color="white"),
        marker_line_color="white",
        marker_line_width=1.5,
    )

    fig.update_layout(
        height=max(350, len(funds) * 60),
        margin=dict(t=60, b=40, l=150, r=100),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, family="Arial, sans-serif"),
    )

    return fig


def create_projection_chart(
    monthly_sip: float, current_age: int, retirement_age: int, equity_pct: float
) -> go.Figure:
    """Create retirement corpus projection chart"""
    years = []
    corpus = []

    # Estimate returns based on equity allocation
    expected_return = 8 + (equity_pct / 100) * 4  # 8-12% based on equity allocation

    for age in range(current_age, min(retirement_age + 1, 75)):
        years_invested = age - current_age
        if years_invested > 0:
            corpus_value = estimate_corpus_at_retirement(
                monthly_sip, current_age, age, expected_return
            )
            years.append(age)
            corpus.append(corpus_value)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=years,
            y=corpus,
            mode="lines+markers",
            name="Projected Corpus",
            line=dict(color="#667eea", width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(102, 126, 234, 0.1)",
            hovertemplate="Age: %{x}<br>Corpus: ₹%{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Retirement Corpus Projection",
        xaxis_title="Age",
        yaxis_title="Corpus (₹)",
        height=400,
        margin=dict(t=60, b=40, l=80, r=40),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, family="Arial, sans-serif"),
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)")

    return fig


@st.fragment
def render_risk_preferences_fragment() -> tuple:
    """
    Fragment for risk preferences - reruns independently for instant updates.

    This is the KEY to solving the dynamic update issue:
    - Widgets inside this fragment trigger ONLY fragment rerun (fast!)
    - Rest of app remains unchanged
    - Session state bridges data to/from fragment

    Args:
        age: User's age for risk profile suggestions

    Returns:
        tuple: (allocation_method, risk_profile, custom_equity)
    """
    # st.subheader("")
    age = st.slider(
        "Age",
        min_value=18,
        max_value=75,
        value=30,
        help="Your current age (Used for asset allocation suggestions)",
    )
    st.markdown("---")
    st.subheader("☣️ Risk Preference")
    # Radio button - changing this triggers fragment rerun only
    allocation_method = st.radio(
        "Allocation Method",
        ["Risk Profile", "Custom"],
        help="Method to determine equity-debt split",
        key="allocation_method_frag",
    )

    custom_equity = None
    risk_profile = None
    # Conditional widgets appear/disappear with each fragment rerun
    if allocation_method == "Risk Profile":
        suggested_profile = get_risk_profile_from_age(age)
        risk_profile = st.selectbox(
            "Risk Profile",
            ["conservative", "moderate", "aggressive"],
            # index=["conservative", "moderate", "aggressive"].index(suggested_profile),
            help=f"Risk Tolerance to market conditions.",
            key="risk_profile_frag",
        )
        equity_pct = get_equity_allocation_from_risk_profile(
            cast(RiskProfile, risk_profile)
        )
        st.caption(
            f"Ratio of Equity to Debt for {risk_profile.title()} is {equity_pct}:{100-equity_pct}"
        )
        st.caption(f"💡 {suggested_profile.title()} profile recommended for age {age}")

    elif allocation_method == "Custom":
        custom_equity = st.slider(
            "Equity Percentage",
            min_value=0,
            max_value=100,
            value=70,
            help="Custom equity allocation",
            key="custom_equity_frag",
        )
        st.caption(f"💡 Debt allocation will be {100-custom_equity}%")

    # Store in session state for access outside fragment
    st.session_state.allocation_method = allocation_method
    st.session_state.risk_profile = risk_profile
    st.session_state.custom_equity = custom_equity
    suggested_strategy = AssetAllocationEngine.get_age_based_strategy(age)
    equity_strategy_options = {
        "index_core": "Index Core",
        "market_weighted": "Market Weighted",
        "balanced_growth": "Balanced Growth",
        "aggressive_growth": "Aggressive Growth",
    }
    equity_strategy_ui = st.selectbox(
        "Equity Strategy",
        list(equity_strategy_options.values()),
        index=0,
        help="How to distribute your equity allocation across market caps",
    )
    equity_strategy = {v: k for k, v in equity_strategy_options.items()}.get(
        equity_strategy_ui
    )
    st.caption(
        f"{AssetAllocationEngine.equity_strategy_descriptions[equity_strategy]}"  # type: ignore
    )
    st.caption(
        f"💡 {equity_strategy_options[suggested_strategy]} strategy recommended for age {age}"
    )
    st.markdown("---")

    return (
        age,
        risk_profile,
        custom_equity,
        equity_strategy,
    )


# ============================================================================
# SIDEBAR INPUT FORM
# ============================================================================


def render_sidebar() -> tuple:
    """
    Render sidebar with optimal UX using form + fragment.

    FORM: Batches basic inputs (age, income, investments)
    FRAGMENT: Handles dynamic risk preferences

    This combination gives:
    - Efficient batching (form prevents constant reruns)
    - Instant updates (fragment reruns independently)
    - Best user experience!
    """
    with st.sidebar:
        age, risk_profile, custom_equity, equity_strategy = (
            render_risk_preferences_fragment()
        )
        with st.form("user_profile_form"):
            st.subheader("📝 Finacial Information")

            monthly_income = st.number_input(
                "Monthly Income (₹)",
                min_value=0,
                value=100000,
                step=10000,
                format="%d",
                help="Your monthly take-home salary",
            )

            st.markdown("---")
            st.subheader("💳 Investment Details")

            monthly_investment = st.number_input(
                "Monthly SIP Amount (₹)",
                min_value=0,
                value=30000,
                step=5000,
                format="%d",
                help="Amount you want to invest monthly via SIP",
            )

            lump_sum = st.number_input(
                "Lumpsum Investment (₹)",
                min_value=0,
                value=0,
                step=50000,
                format="%d",
                help="One-time investment amount (optional)",
            )

            st.markdown("---")
            st.subheader("🛡️ Financial Readiness")

            col1, col2 = st.columns(2)
            with col1:
                emergency_fund = st.checkbox(
                    "Emergency Fund",
                    value=False,
                    help="6 months expenses in liquid savings",
                )
            with col2:
                insurance = st.checkbox(
                    "Adequate Insurance",
                    value=False,
                    help="Term life + health insurance",
                )

            st.markdown("---")

            # Submit button
            submit_button = st.form_submit_button(
                "🚀 Generate Plan", use_container_width=True
            )

        # Return all form values
        return (
            age,
            monthly_income,
            monthly_investment,
            lump_sum,
            emergency_fund,
            insurance,
            custom_equity,
            risk_profile,
            equity_strategy,
            submit_button,
        )


# ============================================================================
# MAIN CONTENT RENDERING FUNCTIONS
# ============================================================================


def render_welcome_screen():
    """Render welcome screen when no plan is generated"""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class='welcome-icon' style='display: flex; align-items: center; justify-content: center; gap: 1rem;'>
    <img src='https://img.icons8.com/color/200/investment-portfolio.png' width='80'>
    <h2 style='margin: 0;'> Welcome to Your Asset Allocation Planner!</h2>
</div>
<p style='color: #666; font-size: 1.1rem; max-width: 700px; margin: 1rem auto;'>
    This tool helps you in asset allocation across Equity and Debt Mutual Funds. Fill in your details in the sidebar and 
    click <b>"Generate Plan"</b> to get started.
</p>

    """,
            unsafe_allow_html=True,
        )

    with col2:
        # Prerequisites
        st.info(
            """
        **💡 Before You Start - Important Prerequisites:**

        1. **Emergency Fund**: Build 6 months of expenses in liquid savings before investing
        2. **Life Insurance**: Get term life insurance (10-15x annual income)
        3. **Health Insurance**: Ensure comprehensive health coverage for family
        4. **Investment Horizon**: Understand your goals and time horizon (short/medium/long-term)
        5. **Risk Understanding**: Be prepared for market volatility, especially in equity investments
        """
        )

    # Quick tips
    with st.expander("📚 Quick Tips for New Investors", expanded=True):
        st.markdown(
            """
        - **Start Small**: Begin with what you can afford, increase gradually
        - **Stay Consistent**: Continue SIPs even in market downturns
        - **Diversify**: Don't put all money in one fund or asset class
        - **Think Long-term**: Equity investments need 10+ years to truly shine
        - **Avoid Timing Market**: Nobody can predict market movements consistently
        - **Review Portfolio**: Check portfolio atleast quarterly
        - **Learn Continuously**: Read books, blogs, and understand basics
        """
        )

    # Key concepts to understand
    with st.expander("💡 Basic Concepts Every Investor Should Know"):
        st.markdown(
            """
        1. **Expense Ratio**: Annual fee charged by fund (lower is better, aim <1%)
        2. **Exit Load**: Fee for selling units before specified period
        3. **NAV (Net Asset Value)**: Per-unit price of mutual fund
        4. **LTCG/STCG**: Long-term/Short-term capital gains tax
        5. **SIP vs Lumpsum**: Systematic vs one-time investment
        6. **Direct vs Regular Plans**: Direct has lower expenses, no commission
        7. **Asset Allocation**: Division of investments across asset classes
        8. **Rebalancing**: Restoring portfolio to original allocation
        9. **Diversification**: Spreading investments to reduce risk
        10. **Risk Tolerance**: Your ability to endure market volatility
        """
        )


def render_detailed_breakdown(plan: AssetAllocationPlan):
    """Render detailed breakdown tab"""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💼 Equity Allocation")
        if plan.equity_allocations:
            fig_equity = create_allocation_breakdown_chart(
                plan.equity_allocations,
                f"Equity Distribution ({plan.equity_percentage}% of portfolio)",
            )
            st.plotly_chart(fig_equity, use_container_width=True)

            # Detailed table
            equity_data = []
            for fund, alloc in plan.equity_allocations.items():
                equity_data.append(
                    {
                        "Fund Category": alloc.subcategory,
                        "% of Total Portfolio": f"{alloc.percentage}%",
                        "% of Equity Allocation": f"{(alloc.percentage/plan.equity_percentage*100):.1f}%",
                    }
                )

            equity_df = pd.DataFrame(equity_data)
            st.dataframe(equity_df, use_container_width=True, hide_index=True)
        else:
            st.info("No equity allocation in this plan")

    with col2:
        st.subheader("🏦 Debt Allocation")
        if plan.debt_allocations:
            fig_debt = create_allocation_breakdown_chart(
                plan.debt_allocations,
                f"Debt Distribution ({plan.debt_percentage}% of portfolio)",
            )
            st.plotly_chart(fig_debt, use_container_width=True)

            # Detailed table
            debt_data = []
            for fund, alloc in plan.debt_allocations.items():
                debt_data.append(
                    {
                        "Fund Category": alloc.subcategory,
                        "% of Total Portfolio": f"{alloc.percentage}%",
                        "% of Debt Allocation": f"{(alloc.percentage/plan.debt_percentage*100):.1f}%",
                    }
                )

            debt_df = pd.DataFrame(debt_data)
            st.dataframe(debt_df, use_container_width=True, hide_index=True)
        else:
            st.info("No debt allocation in this plan")
            # Risk-return profile
        st.markdown("### 📈 Expected Risk-Return Profile")
        if plan.equity_percentage >= 70:
            st.success(
                "**High Growth Portfolio**: Suitable for long-term wealth building (10+ years). Expect higher volatility."
            )
        elif plan.equity_percentage >= 50:
            st.info(
                "**Balanced Portfolio**: Mix of growth and stability (5-10 years). Moderate volatility."
            )
        else:
            st.warning(
                "**Conservative Portfolio**: Capital preservation focus (3-5 years). Lower volatility."
            )


def render_investment_plan(plan: AssetAllocationPlan):
    """Render investment plan tab"""

    # SIP Allocation
    if plan.user_profile.monthly_investment > 0:
        st.subheader("💰 Monthly SIP Allocation")

        fig_sip = create_sip_bar_chart(
            plan.monthly_sip_breakdown, plan.equity_allocations, plan.debt_allocations
        )
        st.plotly_chart(fig_sip, use_container_width=True)

        # Detailed SIP table with download option
        sip_data = []
        for fund, amount in plan.monthly_sip_breakdown.items():
            alloc = plan.equity_allocations.get(fund) or plan.debt_allocations.get(fund)
            if alloc:
                sip_data.append(
                    {
                        "Fund Category": alloc.subcategory,
                        "Asset Type": alloc.category,
                        "% of Portfolio": f"{alloc.percentage}%",
                        "Monthly SIP (₹)": amount,
                        "Annual Investment (₹)": amount * 12,
                    }
                )

        sip_df = pd.DataFrame(sip_data)
        st.dataframe(sip_df, use_container_width=True, hide_index=True)

        # Download CSV
        csv = sip_df.to_csv(index=False)
        st.download_button(
            label="📥 Download SIP Plan (CSV)",
            data=csv,
            file_name=f"sip_plan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # Lumpsum Allocation
    if plan.user_profile.lump_sum_investment > 0:
        st.markdown("---")
        st.subheader("💵 Lumpsum Investment Allocation")

        lump_data = []
        for fund, amount in plan.lumpsum_breakdown.items():
            alloc = plan.equity_allocations.get(fund) or plan.debt_allocations.get(fund)
            if alloc:
                lump_data.append(
                    {
                        "Fund Category": alloc.subcategory,
                        "Asset Type": alloc.category,
                        "% of Portfolio": f"{alloc.percentage}%",
                        "Investment Amount": f"₹{amount:,.0f}",
                    }
                )

        lump_df = pd.DataFrame(lump_data)
        st.dataframe(lump_df, use_container_width=True, hide_index=True)

    # Rebalancing guidelines
    st.markdown("---")
    st.subheader("🔄 Rebalancing Guidelines")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(
            """
        **When to Rebalance:**
        - Review your portfolio **annually** (mark calendar reminder)
        - Rebalance when any fund's allocation drifts **5-10%** from target
        - Don't rebalance based on short-term market movements

        **How to Rebalance:**
        - Sell from outperforming categories (above target)
        - Buy underperforming categories (below target)
        - This maintains your risk profile and forces "buy low, sell high"
        """
        )

    with col2:
        st.warning(
            """
        **⚠️ Avoid:**
        - Daily portfolio checking
        - Panic selling in downturns
        - Over-rebalancing (costly)
        - Chasing performance
        """
        )

    # Rebalancing trigger table
    with st.expander("📊 View Detailed Rebalancing Triggers"):
        trigger_data = []
        for fund, (lower, upper) in plan.rebalancing_triggers.items():
            alloc = plan.equity_allocations.get(fund) or plan.debt_allocations.get(fund)
            if alloc:
                trigger_data.append(
                    {
                        "Fund": alloc.subcategory,
                        "Target Allocation": f"{alloc.percentage}%",
                        "Lower Trigger": f"{lower}%",
                        "Upper Trigger": f"{upper}%",
                        "Action": "Rebalance if outside range",
                    }
                )

        trigger_df = pd.DataFrame(trigger_data)
        st.dataframe(trigger_df, use_container_width=True, hide_index=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================


def main():
    """Main application function"""

    # Render sidebar and get inputs
    (
        age,
        monthly_income,
        monthly_investment,
        lump_sum,
        emergency_fund,
        insurance,
        custom_equity,
        risk_profile,
        equity_strategy,
        submit_button,
    ) = render_sidebar()

    # Generate and display plan
    if submit_button or "plan" in st.session_state:

        if submit_button:
            try:
                # Create user profile
                profile = UserProfile(
                    age=age,
                    monthly_income=monthly_income,
                    monthly_investment=monthly_investment,
                    lump_sum_investment=lump_sum,
                    risk_profile=risk_profile,
                    has_emergency_fund=emergency_fund,
                    has_adequate_insurance=insurance,
                    custom_equity_percentage=custom_equity,
                )

                # Validate profile
                is_valid, errors = profile.validate()
                if not is_valid:
                    st.error("❌ **Validation Errors:**")
                    for error in errors:
                        st.error(f"• {error}")
                    return

                # Generate plan
                engine = AssetAllocationEngine()
                plan = engine.create_plan(
                    profile=profile,
                    equity_strategy=equity_strategy,
                )
                # Store in session state
                st.session_state.plan = plan
                st.session_state.profile_data = {
                    "age": age,
                    "monthly_income": monthly_income,
                    "monthly_investment": monthly_investment,
                    "lump_sum": lump_sum,
                }

            except Exception as e:
                st.error(f"❌ **Error generating plan:** {str(e)}")
                return

        # Retrieve plan from session state
        plan = st.session_state.plan

        # Success message
        st.toast("✅ Your personalized asset allocation plan is ready!")

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Equity Allocation",
                f"{plan.equity_percentage}%",
                help="Percentage allocated to equity funds",
            )
        with col2:
            st.metric(
                "Debt Allocation",
                f"{plan.debt_percentage}%",
                help="Percentage allocated to debt funds",
            )
        with col3:
            st.metric(
                "Monthly SIP",
                f"₹{plan.user_profile.monthly_investment:,.0f}",
                help="Total monthly investment",
            )
        with col4:
            plan_dict = plan.export_to_dict()
            plan_json = json.dumps(plan_dict, indent=2)
            st.download_button(
                label="📥 Download Complete Plan (JSON)",
                data=plan_json,
                file_name=f"asset_allocation_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )

        # Tabbed interface
        tab1, tab2 = st.tabs(
            [
                "💳 Detailed Breakdown",
                "💰 Investment Plan",
            ]
        )

        with tab1:
            render_detailed_breakdown(plan)

        with tab2:
            render_investment_plan(plan)
        # Display warnings if any
        if plan.warnings:
            st.markdown("---")
            st.subheader("Warnings")
            for warning in plan.warnings:
                st.warning(warning)

    else:
        # Show welcome screen
        render_welcome_screen()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 2rem 0;'>
            <p style='margin: 0; font-size: 0.9rem;'>
                Made with ❤️ using Streamlit<br>
                <strong>Disclaimer:</strong> This tool provides educational guidance only. 
                Consult a certified financial advisor before making investment decisions.
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
