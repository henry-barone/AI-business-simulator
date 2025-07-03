from flask import Flask, jsonify, request
from flask_cors import CORS
from simulation_engine import BusinessModel

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins to allow frontend connections during development

@app.route('/run_sandbox', methods=['GET'])
def run_sandbox():
    """
    Run a business simulation with specified parameters.
    
    This endpoint accepts query parameters to configure a business simulation
    and returns monthly profit projections for a 12-month period.
    
    Query Parameters:
        price (float, optional): Unit price for the product. Defaults to 30.
        ad_spend (float, optional): Marketing spend amount. Defaults to 200.
    
    Returns:
        JSON response containing a list of 12 monthly profit values.
        Returns HTTP 200 status code on success.
    """
    try:
        # Get query parameters with fallback defaults
        price = float(request.args.get('price', 30))
        ad_spend = float(request.args.get('ad_spend', 200))
    except (ValueError, TypeError):
        # Use defaults if parameters can't be converted to float
        price = 30
        ad_spend = 200
    
    # Create business model instance and run simulation
    business_model = BusinessModel()
    results = business_model.run_simulation(price, ad_spend)
    
    return jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)