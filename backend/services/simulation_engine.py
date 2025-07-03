#!/usr/bin/env python3
"""
simulation_engine.py

A generic business simulation engine for product-based businesses that provides
profit forecasting capabilities based on pricing strategies and marketing spend.
"""


class BusinessModel:
    """
    A generic business model for simulating monthly profits of product-based businesses.
    
    This class provides a flexible framework for running profit simulations based on
    various business parameters including pricing, costs, and marketing investments.
    The model uses a configurable relationship between marketing spend and sales volume.
    
    The class is designed to be adaptable for any simple product-based business,
    from retail shops to manufacturing operations.
    
    Attributes:
        unit_price (float): Default selling price per unit in currency units
        unit_cost (float): Cost to produce/acquire one unit in currency units
        fixed_costs (float): Monthly fixed costs in currency units (rent, salaries, etc.)
    """
    
    def __init__(self, unit_price=30, unit_cost=10, fixed_costs=2000):
        """
        Initialize the BusinessModel with configurable business parameters.
        
        This constructor allows for flexible initialization of any product-based
        business by specifying the key financial parameters. Default values are
        provided for testing purposes, representing a typical small retail business.
        
        Args:
            unit_price (float, optional): Selling price per unit. Defaults to 30.
            unit_cost (float, optional): Cost per unit (production/acquisition). Defaults to 10.
            fixed_costs (float, optional): Monthly fixed operating costs. Defaults to 2000.
        
        Example:
            >>> # Create a model for a coffee shop
            >>> coffee_model = BusinessModel(unit_price=5, unit_cost=1.5, fixed_costs=5000)
            >>> # Create a model for a electronics store
            >>> electronics_model = BusinessModel(unit_price=500, unit_cost=300, fixed_costs=10000)
        """
        self.unit_price = unit_price
        self.unit_cost = unit_cost
        self.fixed_costs = fixed_costs
    
    def run_simulation(self, new_unit_price, marketing_spend):
        """
        Run a 12-month profit simulation with specified price and marketing parameters.
        
        This method simulates business performance over a 12-month period based on
        user-defined pricing and marketing strategies. It uses a linear model to
        estimate the impact of marketing spend on sales volume.
        
        The sales formula used is: units_sold = (marketing_spend * 0.2) + 100
        This represents a baseline of 100 units plus additional units driven by marketing.
        
        Args:
            new_unit_price (float): The selling price to use for the simulation
            marketing_spend (float): Monthly marketing/advertising budget
        
        Returns:
            list[float]: A list of 12 values representing monthly profits
        
        Note:
            The current sales formula is a simplified placeholder that can be
            enhanced with more sophisticated models (e.g., diminishing returns,
            seasonality, market saturation effects) in future iterations.
        
        Example:
            >>> model = BusinessModel()
            >>> profits = model.run_simulation(new_unit_price=35, marketing_spend=500)
            >>> print(f"First month profit: ${profits[0]}")
        """
        monthly_profits = []
        
        # Calculate units sold based on marketing spend
        # This formula can be made more complex in future versions
        units_sold_per_month = (marketing_spend * 0.2) + 100
        
        # Calculate profit margin using the new price
        profit_margin = new_unit_price - self.unit_cost
        
        # Simulate 12 months of operations
        for month in range(12):
            # Calculate monthly profit
            gross_profit = profit_margin * units_sold_per_month
            net_profit = gross_profit - self.fixed_costs
            monthly_profits.append(net_profit)
        
        return monthly_profits


if __name__ == "__main__":
    # Create an instance of the BusinessModel using default test values
    # These defaults represent a typical small retail business (e.g., t-shirt shop)
    model = BusinessModel()
    
    # Define simulation parameters
    new_price = 35
    marketing_budget = 500
    
    # Run the simulation
    simulation_results = model.run_simulation(
        new_unit_price=new_price,
        marketing_spend=marketing_budget
    )
    
    # Display results in a user-friendly format
    print("Generic Business Model Simulation")
    print("=" * 60)
    print(f"Initial Business Parameters:")
    print(f"  - Default Unit Price: ${model.unit_price}")
    print(f"  - Unit Cost: ${model.unit_cost}")
    print(f"  - Fixed Monthly Costs: ${model.fixed_costs}")
    print(f"\nSimulation Parameters:")
    print(f"  - New Unit Price: ${new_price}")
    print(f"  - Monthly Marketing Spend: ${marketing_budget}")
    print(f"\nGeneric Model Simulation Results: {simulation_results}")
    print(f"\nSummary Statistics:")
    print(f"  - Total Annual Profit: ${sum(simulation_results):,.2f}")
    print(f"  - Average Monthly Profit: ${sum(simulation_results)/12:,.2f}")
    print(f"  - Minimum Monthly Profit: ${min(simulation_results):,.2f}")
    print(f"  - Maximum Monthly Profit: ${max(simulation_results):,.2f}")