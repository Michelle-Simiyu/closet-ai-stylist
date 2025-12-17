# 👗 Closet AI Stylist

An AI-powered personal stylist that helps users create stylish outfits from their existing wardrobe. The system uses computer vision and machine learning to analyze clothing items and recommend compatible outfit combinations.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git
- 8GB+ RAM recommended (for ML models)
- For GPU acceleration: CUDA-compatible NVIDIA GPU (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/closet-ai-stylist.git
   cd closet-ai-stylist
2. Set up virtual environment
# Create virtual environment
    python -m venv venv
    
    # Activate it
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    # venv\Scripts\activate
3. Install dependencies
     pip install -r requirements.txt
4. Set up environment variables
     cp .env.example .env
# Edit .env file if needed (no changes required for basic setup)
🎯 Getting Started
Option 1: Run the Interactive Demo (Recommended for First Time)
bash
# Generate sample data first
python -m src.data.dataset_generator

# Launch the demo
streamlit run demo/streamlit_app.py
Open your browser to http://localhost:8501

Option 2: Test the Core Engine
bash
# Run the compatibility engine tests
python -m src.models.compatibility
Option 3: Start the API Server
bash
uvicorn src.api.server:app --reload --port 8000
API will be available at http://localhost:8000

Interactive docs: http://localhost:8000/docs

Alternative docs: http://localhost:8000/redoc

🛠️ Development Workflow
1. Generate Synthetic Data
bash
# Generate 200 synthetic clothing items
python -m src.data.dataset_generator --items 200 --outfits 50

# Generate with custom output
python -m src.data.dataset_generator --output my_closet.json
2. Test the Compatibility Engine
bash
# Direct test
python -c "
from src.models.compatibility import RuleBasedStylist
stylist = RuleBasedStylist()
# Test with synthetic data
"

# Run unit tests
pytest tests/
3. Add Your Own Rules
Edit src/models/compatibility.py to:

Add new color compatibility rules

Define new styling patterns

Adjust scoring weights

Add seasonal considerations

4. Extend with ML Models
Check notebooks/01_experiment_compatibility.ipynb for examples of:

Training neural networks on outfit compatibility

Image classification for clothing items

Recommendation system development

🔧 Available Scripts
bash
# Setup scripts
./scripts/setup_environment.sh    # One-time setup (Linux/Mac)
./scripts/run_demo.sh             # Launch demo with all prerequisites

# Development utilities
python -m src.utils.clean_data    # Clean and process data
python -m src.utils.export_model  # Export trained models
📊 API Endpoints
POST /api/generate-outfits
Generate outfit combinations from a list of clothing items.

Request:

json
{
  "items": [
    {
      "item_id": "top_001",
      "category": "top",
      "color": "blue",
      "style": "casual",
      "formality": 2
    }
  ],
  "occasion": "casual",
  "max_outfits": 5
}
Response:

json
{
  "outfits": [
    {
      "outfit_id": "outfit_001",
      "items": ["top_001", "bottom_005"],
      "compatibility_score": 0.85,
      "description": "Blue top with black jeans",
      "feedback": ["Great color combination", "Casual yet stylish"]
    }
  ]
}
POST /api/analyze-item
Analyze a clothing image (MVP returns mock data).

🧪 Testing
bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_compatibility.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
🐛 Troubleshooting
Common Issues
1. CUDA/GPU Issues:

bash
# If you get CUDA errors, install CPU-only PyTorch:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or check CUDA compatibility:
python -c "import torch; print(torch.cuda.is_available())"
2. Port Already in Use:

bash
# Find and kill process using port 8501
lsof -ti:8501 | xargs kill -9  # macOS/Linux
# OR
netstat -ano | findstr :8501  # Windows, then taskkill /PID [PID] /F
3. Missing Dependencies:

bash
# Recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
4. File Permission Issues (Linux/Mac):

bash
chmod +x scripts/*.sh
📈 Next Steps for Development
Add Real Image Processing

Integrate background removal (rembg)

Add image classification models

Implement clothing attribute extraction

Enhance Compatibility Engine

Train ML models on fashion datasets

Add user feedback loop

Implement collaborative filtering

Scale the System

Add database (PostgreSQL/Redis)

Implement user authentication

Add caching layer

Improve UX

Add drag-and-drop closet organization

Implement outfit calendar

Add social sharing features

🎓 Learning Resources
Fashion Datasets

PyTorch Tutorials

FastAPI Documentation

Streamlit Docs

🤝 Contributing
Fork the repository

Create a feature branch: git checkout -b feature-name

Commit changes: git commit -am 'Add feature'

Push to branch: git push origin feature-name

Submit a Pull Request

📄 License
MIT License - see LICENSE file for details.

🙏 Acknowledgments
Built with PyTorch, FastAPI, and Streamlit

Inspired by personal styling challenges

Uses various open-source fashion datasets
