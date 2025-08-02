#!/bin/bash
# Streamlit AI Document Processor - Quick Setup

set -e

echo "🚀 Streamlit AI Document Processor Setup"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python: $PYTHON_CMD${NC}"

# Install system dependencies
echo -e "${YELLOW}📦 Installing system dependencies...${NC}"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-ind tesseract-ocr-eng
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        brew install tesseract tesseract-lang
    fi
fi

# Create virtual environment
echo -e "${YELLOW}🐍 Creating virtual environment...${NC}"
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Install requirements
echo -e "${YELLOW}📚 Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo -e "${YELLOW}⚙️ Creating environment file...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Pinecone (not used in basic version)
PINECONE_API_KEY=your-pinecone-key-here
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo -e "${YELLOW}⚠️ Please edit .env with your OpenAI API key${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create run script
echo -e "${YELLOW}🔧 Creating run script...${NC}"
cat > run.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Streamlit AI Document Processor"

# Activate virtual environment
source venv/bin/activate

# Run Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
EOF

chmod +x run.sh

# Success message
echo -e "\n${GREEN}🎉 Setup completed!${NC}"
echo -e "\n${YELLOW}📋 Next Steps:${NC}"
echo -e "1. Edit .env with your OpenAI API key"
echo -e "2. Run: ./run.sh"
echo -e "3. Open: http://localhost:8501"
echo -e "\n${GREEN}Happy processing! 🚀${NC}"
