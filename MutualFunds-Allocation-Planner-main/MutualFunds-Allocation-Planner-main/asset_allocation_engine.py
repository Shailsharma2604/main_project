"""
Mutual Fund Asset Allocation Plan Generator
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal, Tuple
from datetime import datetime

# Type definitions
RiskProfile = Literal["conservative", "moderate", "aggressive"]
"""Represents the risk tolerance level of an investor.
- conservative: Lower risk, lower potential returns (recommended for age 55+)
- moderate: Balanced risk-return profile (recommended for age 35-55)
- aggressive: Higher risk, higher potential returns (recommended for age <35)
"""

EquityStrategy = Literal[
    "index_core", "market_weighted", "balanced_growth", "aggressive_growth"
]
"""Defines the strategy for equity allocation across market capitalizations.
- index_core: 100% large-cap index funds for low-cost market returns
- market_weighted: Mirrors market composition (70% large, 20% mid, 10% small)
- balanced_growth: Growth-focused (45% large, 30% mid, 25% small)
- aggressive_growth: Maximum growth potential (35% large, 35% mid, 30% small)
"""

GoalTimeframe = Literal["short_term", "medium_term", "long_term"]
"""Classification of investment goals based on time horizon.
- short_term: Less than 3 years
- medium_term: 3-7 years
- long_term: More than 7 years
"""


# TODO: Add goal-based allocation adjustments and recommendations
@dataclass
class FinancialGoal:
    """Represents a specific financial goal for goal-based investment allocation.

    The class encapsulates key attributes of a financial goal including target amount,
    timeline, and priority level. It automatically categorizes goals into short,
    medium, or long-term timeframes based on years to goal.

    Attributes:
        name: A descriptive name for the financial goal (e.g., "House Down Payment")
        target_amount: The target amount to achieve for this goal in currency units
        years_to_goal: Number of years until the goal needs to be achieved
        priority: Priority level from 1 (highest) to 5 (lowest)
        monthly_allocation: Monthly amount allocated towards this goal

    Example:
        >>> house_goal = FinancialGoal("House", 2000000, 5, 1, 30000)
        >>> print(house_goal.timeframe)
        'medium_term'
    """

    name: str
    target_amount: float
    years_to_goal: int
    priority: int  # 1 = highest, 5 = lowest
    monthly_allocation: float = 0.0

    @property
    def timeframe(self) -> GoalTimeframe:
        """Determine goal timeframe category"""
        if self.years_to_goal <= 3:
            return "short_term"
        elif self.years_to_goal <= 7:
            return "medium_term"
        else:
            return "long_term"


@dataclass
class UserProfile:
    """Represents a user's comprehensive financial profile for asset allocation planning.

    This class stores key information about a user's financial situation, risk tolerance,
    and investment preferences needed to generate an appropriate asset allocation plan.
    It includes validation logic to ensure all inputs are within acceptable ranges.

    Attributes:
        age: User's current age (18-100)
        monthly_income: Monthly take-home income in currency units
        monthly_investment: Monthly amount available for investment (SIP)
        lump_sum_investment: One-time investment amount, if any
        risk_profile: User's risk tolerance level (conservative/moderate/aggressive)
        has_emergency_fund: Whether user has 6 months of expenses saved
        has_adequate_insurance: Whether user has term life and health insurance
        custom_equity_percentage: Optional override for equity allocation (0-100)
        goals: List of specific financial goals for goal-based investing

    Example:
        >>> profile = UserProfile(
        ...     age=30,
        ...     monthly_income=100000,
        ...     monthly_investment=20000,
        ...     risk_profile="moderate"
        ... )
        >>> valid, errors = profile.validate()
    """

    age: int
    monthly_income: float
    monthly_investment: float
    lump_sum_investment: float = 0.0
    risk_profile: Optional[RiskProfile] = None
    has_emergency_fund: bool = False  # 6 months of expenses
    has_adequate_insurance: bool = False  # Term + health insurance
    custom_equity_percentage: Optional[float] = None
    goals: list[FinancialGoal] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"UserProfile(age={self.age}, monthly_income={self.monthly_income}, "
            f"monthly_investment={self.monthly_investment}, lump_sum_investment={self.lump_sum_investment}, "
            f"risk_profile={self.risk_profile}, has_emergency_fund={self.has_emergency_fund}, "
            f"has_adequate_insurance={self.has_adequate_insurance}, custom_equity_percentage={self.custom_equity_percentage}, "
            f"goals={[goal.name for goal in self.goals]})"
        )

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate user profile inputs"""
        errors = []

        if self.age < 18 or self.age > 100:
            errors.append("Age must be between 18 and 100")

        if self.monthly_income < 0:
            errors.append("Monthly income cannot be negative")

        if self.monthly_investment < 0:
            errors.append("Monthly investment cannot be negative")

        if self.monthly_investment > self.monthly_income:
            errors.append("Monthly investment cannot exceed monthly income")

        if self.lump_sum_investment < 0:
            errors.append("Lumpsum investment cannot be negative")

        if self.custom_equity_percentage is not None:
            if self.custom_equity_percentage < 0 or self.custom_equity_percentage > 100:
                errors.append("Custom equity percentage must be between 0 and 100")

        return len(errors) == 0, errors

    def get_investment_summary(self) -> Dict[str, float]:
        """Get summary of total investments"""
        annual_sip = self.monthly_investment * 12
        total_first_year = annual_sip + self.lump_sum_investment

        return {
            "monthly_sip": self.monthly_investment,
            "annual_sip": annual_sip,
            "lumpsum": self.lump_sum_investment,
            "first_year_total": total_first_year,
        }


@dataclass
class FundAllocation:
    """Represents allocation details for a specific mutual fund category.

    This class stores both the percentage and absolute amount allocation for a fund
    category, along with recommended specific funds within that category. It supports
    serialization to dictionary format for data persistence.

    Attributes:
        category: Main asset category ("Equity" or "Debt")
        subcategory: Specific fund subcategory (e.g., "Large Cap", "Index", "FD")
        percentage: Allocation percentage of total portfolio (0-100)
        amount: Actual amount allocated in currency units
        recommended_funds: List of specific fund names recommended for this category

    Example:
        >>> allocation = FundAllocation(
        ...     category="Equity",
        ...     subcategory="Large Cap",
        ...     percentage=30.0,
        ...     amount=15000.0
        ... )
        >>> allocation.to_dict()
    """

    category: str
    subcategory: str
    percentage: float
    amount: float = 0.0
    recommended_funds: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for easy serialization"""
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "percentage": self.percentage,
            "amount": self.amount,
            "recommended_funds": self.recommended_funds,
        }


@dataclass
class AssetAllocationPlan:
    """Represents a complete asset allocation plan with portfolio details and recommendations.

    This class encapsulates all aspects of an asset allocation plan including the equity-debt
    split, detailed fund allocations, investment breakdowns, and personalized recommendations.
    It provides methods for retrieving plan summaries and exporting data.

    Attributes:
        user_profile: The user profile this plan was generated for
        equity_percentage: Total equity allocation (0-100)
        debt_percentage: Total debt allocation (0-100)
        equity_allocations: Detailed allocations for each equity fund category
        debt_allocations: Detailed allocations for each debt fund category
        monthly_sip_breakdown: Monthly SIP amount for each fund category
        lumpsum_breakdown: Lumpsum investment split across fund categories
        rebalancing_triggers: Lower and upper bounds for rebalancing each fund
        warnings: List of risk warnings based on the allocation
        recommendations: List of personalized investment recommendations
        created_at: Timestamp when the plan was generated

    Example:
        >>> plan = AssetAllocationPlan(
        ...     user_profile=profile,
        ...     equity_percentage=70,
        ...     debt_percentage=30,
        ...     equity_allocations={'largecap': FundAllocation(...)},
        ...     debt_allocations={'fd': FundAllocation(...)},
        ...     monthly_sip_breakdown={'largecap': 15000, 'fd': 5000},
        ...     lumpsum_breakdown={},
        ...     rebalancing_triggers={'largecap': (65, 75)}
        ... )
        >>> plan.get_allocation_summary()
    """

    user_profile: UserProfile
    equity_percentage: float
    debt_percentage: float
    equity_allocations: Dict[str, FundAllocation]
    debt_allocations: Dict[str, FundAllocation]
    monthly_sip_breakdown: Dict[str, float]
    lumpsum_breakdown: Dict[str, float]
    rebalancing_triggers: Dict[str, Tuple[float, float]]
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def get_total_funds_count(self) -> int:
        """Get total number of fund categories"""
        return len(self.equity_allocations) + len(self.debt_allocations)

    def get_all_allocations(self) -> Dict[str, FundAllocation]:
        """Get combined equity and debt allocations"""
        return {**self.equity_allocations, **self.debt_allocations}

    def get_allocation_summary(self) -> Dict:
        """Get summary statistics"""
        all_allocs = self.get_all_allocations()

        return {
            "total_funds": self.get_total_funds_count(),
            "equity_funds": len(self.equity_allocations),
            "debt_funds": len(self.debt_allocations),
            "equity_percentage": self.equity_percentage,
            "debt_percentage": self.debt_percentage,
            "monthly_sip_total": sum(self.monthly_sip_breakdown.values()),
            "lumpsum_total": sum(self.lumpsum_breakdown.values()),
        }

    def export_to_dict(self) -> Dict:
        """Export complete plan as dictionary"""
        return {
            "user_age": self.user_profile.age,
            "equity_percentage": self.equity_percentage,
            "debt_percentage": self.debt_percentage,
            "equity_allocations": {
                k: v.to_dict() for k, v in self.equity_allocations.items()
            },
            "debt_allocations": {
                k: v.to_dict() for k, v in self.debt_allocations.items()
            },
            "monthly_sip_breakdown": self.monthly_sip_breakdown,
            "lumpsum_breakdown": self.lumpsum_breakdown,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }


class AssetAllocationEngine:
    """Main engine for creating personalized asset allocation plans.

    This class implements the core logic for generating asset allocation plans based on
    user profiles and market conditions. It handles equity-debt split calculations,
    fund category allocation, and generates personalized recommendations.

    The engine supports multiple allocation strategies:
    1. Risk profile based (conservative/moderate/aggressive)
    2. Age-based (100 - age rule with bounds)
    3. Custom allocation (user-specified equity percentage)

    It also provides templates for different equity strategies and debt allocations,
    along with comprehensive warning generation and rebalancing recommendations.

    Attributes:
        equity_templates: Predefined templates for different equity allocation strategies
        debt_templates: Templates for debt allocation based on timeframe
        equity_strategy_descriptions: Detailed descriptions of equity strategies
        debt_strategy_descriptions: Descriptions of debt allocation strategies

    Example:
        >>> engine = AssetAllocationEngine()
        >>> profile = UserProfile(age=30, monthly_income=100000, monthly_investment=20000)
        >>> plan = engine.create_plan(profile, equity_strategy="balanced_growth")
        >>> print(f"Equity: {plan.equity_percentage}%, Debt: {plan.debt_percentage}%")
    """

    equity_templates = {
        "index_core": {
            "index": 100,  # 100% Largecap Index funds (Nifty 50/Sensex)
        },
        "market_weighted": {
            "largecap": 70,  # 70% Large-cap (mirrors market composition)
            "midcap": 20,  # 20% Mid-cap
            "smallcap": 10,  # 10% Small-cap
        },
        "balanced_growth": {
            "largecap": 45,  # 45% Large-cap/Index
            "midcap": 30,  # 30% Mid-cap
            "smallcap": 25,  # 25% Small-cap
        },
        "aggressive_growth": {
            "largecap": 35,  # 35% Large-cap/Index
            "midcap": 35,  # 35% Mid-cap
            "smallcap": 30,  # 30% Small-cap
        },
    }

    # TODO: Add debt options apart from FD, based on user profile and goals
    # Debt allocation templates
    debt_templates = {"long_term": {"FD": 100}}

    # Strategy descriptions for UI
    equity_strategy_descriptions = {
        "index_core": "Investment in 100% Largecap Index funds - Low cost, market returns (like Nifty 50/Sensex)",
        "market_weighted": "Investment in  70% Largecap, 20% Midcap, 10% Smallcap - Conservative, mirrors market",
        "balanced_growth": "Investment in 45% Largecap, 30% Midcap, 25% Smallcap - Balanced risk-return",
        "aggressive_growth": "Investment in 35% Largecap, 35% Midcap, 30% Smallcap - Maximum growth potential",
    }

    debt_strategy_descriptions = {"long_term": "FD for safe long-term low-risk returns"}

    def get_strategy_description(self, strategy_type: str, strategy_name: str) -> str:
        """Get description for a strategy"""
        if strategy_type == "equity":
            return self.equity_strategy_descriptions.get(strategy_name, "")
        elif strategy_type == "debt":
            return self.debt_strategy_descriptions.get(strategy_name, "")
        return ""

    def calculate_equity_debt_split(self, profile: UserProfile) -> Tuple[float, float]:
        """Calculate equity-debt split using multiple methods"""

        if profile.custom_equity_percentage is not None:
            equity_pct = max(0, min(100, profile.custom_equity_percentage))
            return equity_pct, 100 - equity_pct

        if profile.risk_profile:
            equity_pct = get_equity_allocation_from_risk_profile(profile.risk_profile)
            return (equity_pct, 100 - equity_pct)

        equity_pct = max(20, min(80, 100 - profile.age))
        debt_pct = 100 - equity_pct

        return equity_pct, debt_pct

    @staticmethod
    def get_age_based_strategy(age: int) -> EquityStrategy:
        """Recommend equity strategy based on investor age"""
        if age < 35:
            return "aggressive_growth"  # Age 20-35: Wealth Building
        elif age < 50:
            return "balanced_growth"  # Age 35-50: Growth & Stability
        else:
            return "market_weighted"  # Age 50+: Preservation

    def allocate_equity(
        self,
        equity_pct: float,
        strategy: EquityStrategy,
        add_international: bool = False,
        sector_allocation: float = 0.0,
    ) -> Dict[str, FundAllocation]:
        """Allocate equity portion across fund categories"""

        template = self.equity_templates[strategy]
        allocations = {}

        # Reserve space for optional allocations
        international_pct = 10 if add_international else 0
        sector_pct = min(15, max(0, sector_allocation))

        # Base allocation (domestic equity)
        base_pct = 100 - international_pct - sector_pct

        # Allocate across market caps
        for fund_type, template_pct in template.items():
            actual_pct = (template_pct / 100) * (equity_pct * base_pct / 100)
            allocations[fund_type] = FundAllocation(
                category="Equity",
                subcategory=fund_type.title().replace("_", " "),
                percentage=round(actual_pct, 2),
            )

        # Add international exposure if requested
        if add_international:
            allocations["international"] = FundAllocation(
                category="Equity",
                subcategory="International Equity",
                percentage=round(equity_pct * international_pct / 100, 2),
            )

        # Add sector allocation if requested
        if sector_pct > 0:
            allocations["sector"] = FundAllocation(
                category="Equity",
                subcategory="Sector/Thematic",
                percentage=round(equity_pct * sector_pct / 100, 2),
            )

        return allocations

    def allocate_debt(
        self, debt_pct: float, strategy: GoalTimeframe = "long_term"
    ) -> Dict[str, FundAllocation]:
        """Allocate debt portion across fund categories"""

        template = self.debt_templates[strategy]
        allocations = {}

        for fund_type, template_pct in template.items():
            actual_pct = (template_pct / 100) * debt_pct
            allocations[fund_type] = FundAllocation(
                category="Debt",
                subcategory=fund_type.title().replace("_", " "),
                percentage=round(actual_pct, 2),
            )

        return allocations

    def calculate_fund_amounts(
        self, allocations: Dict[str, FundAllocation], total_amount: float
    ) -> Dict[str, float]:
        """Calculate actual rupee amounts for each fund"""
        breakdown = {}
        for fund_name, allocation in allocations.items():
            amount = (allocation.percentage / 100) * total_amount
            allocation.amount = round(amount, 2)
            breakdown[fund_name] = round(amount, 2)
        return breakdown

    def set_rebalancing_triggers(
        self, allocations: Dict[str, FundAllocation], drift_threshold: float = 5.0
    ) -> Dict[str, Tuple[float, float]]:
        """Set rebalancing trigger bands"""
        triggers = {}
        for fund_name, allocation in allocations.items():
            target = allocation.percentage
            lower_trigger = max(0, target - drift_threshold)
            upper_trigger = min(100, target + drift_threshold)
            triggers[fund_name] = (round(lower_trigger, 2), round(upper_trigger, 2))
        return triggers

    def generate_warnings(self, profile: UserProfile, equity_pct: float) -> List[str]:
        """Generate personalized warnings based on user profile"""
        warnings = []

        # Emergency fund warning
        if not profile.has_emergency_fund and equity_pct > 50:
            warnings.append(
                "⚠️ CRITICAL: Build 6 months of emergency fund before investing heavily in equity. "
                "Keep this in liquid/savings accounts for immediate access."
            )

        # Insurance warning
        if not profile.has_adequate_insurance:
            warnings.append(
                "⚠️ IMPORTANT: Ensure adequate term life insurance (10-15x annual income) and "
                "comprehensive health insurance before aggressive equity allocation."
            )

        # High equity allocation warning
        if equity_pct > 80:
            warnings.append(
                "⚠️ Very high equity allocation (>80%). Expect significant volatility. "
                "Only suitable for investors with 10+ year time horizon and high risk tolerance."
            )

        # Age-appropriate warning
        if profile.age > 60 and equity_pct > 50:
            warnings.append(
                "⚠️ At age 60+, consider reducing equity exposure for capital preservation. "
                "Current allocation may be aggressive for typical retirement needs."
            )

        # Low investment warning
        if profile.monthly_investment < 5000:
            warnings.append(
                "💡 Consider increasing monthly investment gradually as income grows. "
                "Even small increases compound significantly over time."
            )

        # High investment ratio warning
        investment_ratio = (
            (profile.monthly_investment / profile.monthly_income * 100)
            if profile.monthly_income > 0
            else 0
        )
        if investment_ratio > 50:
            warnings.append(
                "⚠️ Investing >50% of monthly income is aggressive. "
                "Ensure you have adequate funds for living expenses and emergencies."
            )
        return warnings

    def generate_recommendations(
        self, profile: UserProfile, equity_pct: float, num_funds: int
    ) -> List[str]:
        """Generate personalized recommendations"""
        recs = []

        # Portfolio simplicity
        recs.append(f"📋 SIMPLICITY: Keep portfolio simple with 5-7 funds total. ")

        # Rebalancing discipline
        recs.append(
            "🔄 REBALANCING: Review portfolio annually. Rebalance when any allocation drifts "
            "5-10% from target. Sell outperformers, buy underperformers to maintain risk profile."
        )

        # Market timing
        recs.append(
            "⏱️ NO MARKET TIMING: Never try to time the market. Use 'thali approach' - "
            "maintain diversified portions matching your age, goals, and risk appetite."
        )

        # Index funds
        if equity_pct > 30:
            recs.append(
                "📊 INDEX FUNDS: Use low-cost index funds (Nifty 50/Sensex) as core equity holdings. "
                "They provide market returns with minimal expense ratios (0.05-0.20%)."
            )

        # SIP discipline
        if profile.monthly_investment > 0:
            recs.append(
                "💰 SIP DISCIPLINE: Continue SIPs regardless of market conditions. "
                "Rupee cost averaging works best over 10+ years. Increase SIPs with salary growth."
            )

        # Goal-based investing
        recs.append(
            "🎯 GOAL-BASED: Align investments with specific goals. "
            "Short-term (<3 years) → Debt funds. Long-term (10+ years) → Equity funds."
        )

        # Tax efficiency
        if equity_pct > 40:
            recs.append(
                "💸 TAX EFFICIENCY: Hold equity funds >1 year for LTCG tax benefits. "
                "Consider ELSS for Section 80C deductions (3-year lock-in)."
            )

        # Fund selection
        recs.append(
            "🔍 FUND SELECTION: Choose funds with consistent top-quartile performance over "
            "10+ years. Prioritize low expense ratios and experienced fund managers."
        )

        # Review frequency
        recs.append(
            "📅 REVIEW SCHEDULE: Review portfolio quarterly but rebalance only when portfolio allocation across catogaries changes beyond 5-10% threshold. "
        )

        return recs

    def create_plan(
        self,
        profile: UserProfile,
        equity_strategy: Optional[EquityStrategy] = None,
        debt_strategy: GoalTimeframe = "long_term",
        add_international: bool = False,
        sector_allocation: float = 0.0,
        drift_threshold: float = 5.0,
    ) -> AssetAllocationPlan:
        """
        Create complete asset allocation plan

        Args:
            profile: User financial profile
            equity_strategy: Equity allocation strategy (calculated based on age if None selected)
            debt_strategy: Debt allocation strategy
            add_international: Add international equity exposure
            sector_allocation: Percentage for sector/thematic funds (0-15%)
            drift_threshold: Rebalancing trigger threshold (default 5%)

        Returns:
            Complete AssetAllocationPlan object
        """

        # Validate profile first
        is_valid, errors = profile.validate()
        if not is_valid:
            raise ValueError(f"Invalid profile: {', '.join(errors)}")

        # Calculate equity-debt split
        equity_pct, debt_pct = self.calculate_equity_debt_split(profile)

        # Determine equity strategy if not specified
        if equity_strategy is None:
            equity_strategy = self.get_age_based_strategy(profile.age)

        # Allocate equity and debt
        equity_allocs = self.allocate_equity(
            equity_pct, equity_strategy, add_international, sector_allocation
        )
        debt_allocs = self.allocate_debt(debt_pct, debt_strategy)

        # Combine all allocations
        all_allocations = {**equity_allocs, **debt_allocs}

        # Calculate SIP and lumpsum breakdowns
        monthly_sip = self.calculate_fund_amounts(
            all_allocations, profile.monthly_investment
        )
        lumpsum = self.calculate_fund_amounts(
            all_allocations, profile.lump_sum_investment
        )

        # Set rebalancing triggers
        triggers = self.set_rebalancing_triggers(all_allocations, drift_threshold)

        # Generate warnings and recommendations
        warnings = self.generate_warnings(profile, equity_pct)
        recommendations = self.generate_recommendations(
            profile, equity_pct, len(all_allocations)
        )

        return AssetAllocationPlan(
            user_profile=profile,
            equity_percentage=round(equity_pct, 2),
            debt_percentage=round(debt_pct, 2),
            equity_allocations=equity_allocs,
            debt_allocations=debt_allocs,
            monthly_sip_breakdown=monthly_sip,
            lumpsum_breakdown=lumpsum,
            rebalancing_triggers=triggers,
            warnings=warnings,
            recommendations=recommendations,
        )


class PortfolioRebalancer:
    """Helper class for portfolio rebalancing calculations and analysis.

    This class provides utilities for analyzing current portfolio allocations,
    calculating required trades for rebalancing, and determining when rebalancing
    is needed based on drift thresholds.

    The class uses static methods exclusively as it doesn't need to maintain any state
    between operations. All calculations are performed based on the input parameters.

    Example:
        >>> current_values = {"largecap": 120000, "midcap": 50000}
        >>> target_allocation = {"largecap": 70, "midcap": 30}
        >>> rebalancer = PortfolioRebalancer()
        >>> trades = rebalancer.calculate_rebalance_trades(current_values, target_allocation)
        >>> needs_rebalancing, drifted = rebalancer.check_rebalancing_needed(
        ...     current_pct={"largecap": 75, "midcap": 25},
        ...     target_pct={"largecap": 70, "midcap": 30}
        ... )
    """

    @staticmethod
    def calculate_current_allocation(
        current_values: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate current percentage allocation from values"""
        total = sum(current_values.values())
        if total <= 0:
            return {}

        return {
            fund: round((value / total) * 100, 2)
            for fund, value in current_values.items()
        }

    @staticmethod
    def calculate_rebalance_trades(
        current_values: Dict[str, float], target_allocation_pct: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate required trades to rebalance portfolio"""
        total_value = sum(current_values.values())
        if total_value <= 0:
            raise ValueError("Current portfolio value must be positive")

        # Calculate target amounts
        target_amounts = {}
        for fund in set(current_values.keys()) | set(target_allocation_pct.keys()):
            target_pct = target_allocation_pct.get(fund, 0.0)
            target_amounts[fund] = (target_pct / 100) * total_value

        # Calculate required trades
        trades = {}
        for fund in target_amounts:
            current_val = current_values.get(fund, 0.0)
            target_val = target_amounts[fund]
            trade_amount = target_val - current_val

            if abs(trade_amount) > 100:  # Only show meaningful trades
                trades[fund] = round(trade_amount, 2)

        return trades

    @staticmethod
    def check_rebalancing_needed(
        current_pct: Dict[str, float],
        target_pct: Dict[str, float],
        drift_threshold: float = 5.0,
    ) -> Tuple[bool, List[str]]:
        """Check if rebalancing is needed based on drift threshold"""
        drifted_funds = []

        for fund, target in target_pct.items():
            current = current_pct.get(fund, 0.0)
            drift = abs(current - target)

            if drift >= drift_threshold:
                drifted_funds.append(
                    f"{fund}: Target {target}%, Current {current}%, Drift {drift:.1f}%"
                )

        return len(drifted_funds) > 0, drifted_funds


# Utility functions
def get_risk_profile_from_age(age: int) -> RiskProfile:
    """Determine appropriate risk profile based on investor's age.

    This function implements a simple age-based risk profiling strategy:
    - Young investors (< 35): Aggressive profile due to long investment horizon
    - Mid-age investors (35-55): Moderate profile balancing growth and stability
    - Older investors (> 55): Conservative profile focusing on capital preservation

    Args:
        age: The investor's current age

    Returns:
        RiskProfile: Recommended risk profile ("aggressive", "moderate", or "conservative")

    Example:
        >>> profile = get_risk_profile_from_age(30)
        >>> print(profile)
        'aggressive'
    """
    if age < 35:
        return "aggressive"
    elif age < 55:
        return "moderate"
    else:
        return "conservative"


def get_equity_allocation_from_risk_profile(risk_profile: RiskProfile) -> float:
    """Determine recommended equity allocation percentage based on risk profile.

    Maps each risk profile to a specific equity allocation percentage:
    - Aggressive: 85% equity (high growth potential with high volatility)
    - Moderate: 65% equity (balanced growth with moderate volatility)
    - Conservative: 45% equity (capital preservation with lower volatility)

    Args:
        risk_profile: The investor's risk profile (conservative/moderate/aggressive)

    Returns:
        float: Recommended equity allocation percentage (0-100)

    Example:
        >>> allocation = get_equity_allocation_from_risk_profile("moderate")
        >>> print(allocation)
        65.0
    """
    equity_splits = {
        "aggressive": 85,
        "moderate": 65,
        "conservative": 45,
    }
    return equity_splits[risk_profile]


def estimate_corpus_at_retirement(
    monthly_sip: float,
    current_age: int,
    retirement_age: int = 60,
    expected_return: float = 12.0,
) -> float:
    """Calculate estimated corpus at retirement using SIP investment approach.

    Uses the future value of SIP formula to estimate the corpus that will be accumulated
    by retirement through regular monthly investments. Assumes monthly compounding and
    a consistent rate of return throughout the investment period.

    Args:
        monthly_sip: Monthly investment amount in currency units
        current_age: Current age of the investor
        retirement_age: Target retirement age (default: 60)
        expected_return: Expected annual return percentage (default: 12.0)

    Returns:
        float: Estimated corpus amount at retirement

    Example:
        >>> corpus = estimate_corpus_at_retirement(
        ...     monthly_sip=50000,
        ...     current_age=30,
        ...     retirement_age=60,
        ...     expected_return=12.0
        ... )
        >>> print(f"Estimated retirement corpus: ₹{corpus:,.2f}")

    Note:
        The calculation assumes:
        - Consistent monthly investments
        - Constant rate of return (no volatility)
        - No withdrawal before retirement
        - Monthly compounding of returns
    """
    years = retirement_age - current_age
    months = years * 12
    monthly_return = expected_return / 12 / 100

    # Future value of SIP formula
    if monthly_return == 0:
        return monthly_sip * months

    fv = (
        monthly_sip
        * (((1 + monthly_return) ** months - 1) / monthly_return)
        * (1 + monthly_return)
    )
    return round(fv, 2)


def format_inr(number: float) -> str:
    """Format a number in Indian Rupee format with appropriate separators.

    Converts a number to the Indian currency format which uses different grouping
    than international formats. For example:
    - International: 1,234,567.89
    - Indian: 12,34,567.89

    Args:
        number: The number to format (can be integer or float)

    Returns:
        str: Formatted string with Indian Rupee symbol (₹) and appropriate separators

    Example:
        >>> print(format_inr(1234567.89))
        '₹ 12,34,567.89'
        >>> print(format_inr(1000))
        '₹ 1,000'
    """
    s = str(number)
    if "." in s:
        s, dec = s.split(".")
        dec = "." + dec
    else:
        dec = ""

    # Separate last 3 digits
    last3 = s[-3:]
    rest = s[:-3]

    # Insert commas after every two digits in the remaining part
    if rest:
        res = ""
        while len(rest) > 2:
            res = "," + rest[-2:] + res
            rest = rest[:-2]
        res = rest + res
        return "₹ " + res + "," + last3 + dec
    else:
        return "₹ " + last3 + dec


if __name__ == "__main__":
    # Example usage
    print("Asset Allocation Engine Module")
    # Quick test
    profile = UserProfile(
        age=30,
        monthly_income=100000,
        monthly_investment=30000,
        lump_sum_investment=0,
        has_emergency_fund=False,
        has_adequate_insurance=False,
        custom_equity_percentage=None,
        goals=[],
    )
    engine = AssetAllocationEngine()
    plan = engine.create_plan(profile)
    print(f"\nTest Plan Created:")
    print(f"Equity: {plan.equity_percentage}%, Debt: {plan.debt_percentage}%")
    print(f"Total Funds: {plan.get_total_funds_count()}")
    print(f"Total warning: {plan.warnings}")
    print("✓ Engine module working correctly!")
