#!/bin/bash

# Test script to verify questionnaire fix

echo "🧪 Testing Questionnaire Fix"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend health check
echo -e "\n${YELLOW}1. Testing backend health...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:5001/health)
if [[ $? -eq 0 ]] && [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    exit 1
fi

# Test 2: Company creation
echo -e "\n${YELLOW}2. Testing company creation...${NC}"
COMPANY_RESPONSE=$(curl -s -X POST http://localhost:5001/api/companies \
    -H "Content-Type: application/json" \
    -d '{"name":"Test Company","industry":"Manufacturing"}')

if [[ $? -eq 0 ]] && [[ $COMPANY_RESPONSE == *"data"* ]]; then
    echo -e "${GREEN}✅ Company creation works${NC}"
    COMPANY_ID=$(echo $COMPANY_RESPONSE | jq -r '.data.id')
    echo "   Company ID: $COMPANY_ID"
else
    echo -e "${RED}❌ Company creation failed${NC}"
    echo "   Response: $COMPANY_RESPONSE"
    exit 1
fi

# Test 3: Questionnaire endpoint
echo -e "\n${YELLOW}3. Testing questionnaire endpoint...${NC}"
QUEST_RESPONSE=$(curl -s -X POST http://localhost:5001/api/questionnaire/next \
    -H "Content-Type: application/json" \
    -d "{\"companyId\":\"$COMPANY_ID\",\"previousAnswers\":{}}")

if [[ $? -eq 0 ]] && [[ $QUEST_RESPONSE == *"question"* ]]; then
    echo -e "${GREEN}✅ Questionnaire endpoint works${NC}"
    echo "   Question: $(echo $QUEST_RESPONSE | jq -r '.data.question.text')"
else
    echo -e "${RED}❌ Questionnaire endpoint failed${NC}"
    echo "   Response: $QUEST_RESPONSE"
fi

# Test 4: CORS check
echo -e "\n${YELLOW}4. Testing CORS configuration...${NC}"
CORS_RESPONSE=$(curl -s -X OPTIONS http://localhost:5001/api/companies \
    -H "Origin: http://localhost:8080" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    -I | grep -i "access-control")

if [[ $CORS_RESPONSE == *"Access-Control-Allow-Origin"* ]]; then
    echo -e "${GREEN}✅ CORS is properly configured${NC}"
else
    echo -e "${RED}❌ CORS configuration issue${NC}"
fi

# Test 5: Frontend build check
echo -e "\n${YELLOW}5. Checking frontend environment configuration...${NC}"
if [[ -f "frontend/.env" ]]; then
    API_URL=$(grep VITE_API_BASE_URL frontend/.env | cut -d'=' -f2)
    if [[ $API_URL == *"5001"* ]]; then
        echo -e "${GREEN}✅ Frontend environment configured correctly${NC}"
        echo "   API URL: $API_URL"
    else
        echo -e "${RED}❌ Frontend environment configuration issue${NC}"
        echo "   Expected port 5001, got: $API_URL"
    fi
else
    echo -e "${RED}❌ Frontend .env file not found${NC}"
fi

echo -e "\n${GREEN}🎉 All tests completed!${NC}"
echo ""
echo "To test the full flow:"
echo "1. Run: python dev-server.py"
echo "2. Open: http://localhost:8080"
echo "3. Navigate to Business Simulation"
echo "4. Try creating a company and proceeding to file upload"
echo ""